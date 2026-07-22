"""
Decision Engine para UC08: Resposta a token vazado e service account perigosa.

Lógica de decisão para determinar quando revoke_token, disable_service_account,
escalate_incident ou bloquear sem evidência.

Princípios:
1. Nunca executar ação destrutiva sem evidência de pelo menos 2 fontes
2. Sempre fazer dry_run antes de ação real
3. Exigir aprovação explícita para ações destrutivas
4. Registrar no audit_log
"""
from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from .uc08_models import (
    SecurityAlertData,
    Evidence,
    ProposedAction,
    UC08Decision,
)
from .repository import Repository
from .models import ActionResult


class UC08DecisionEngine:
    """Engine que avalia evidências e propõe ações para alertas de segurança."""

    def __init__(self, repo: Repository | None = None):
        self.repo = repo or Repository()
        self.evidence: list[Evidence] = []
        self.proposed_actions: list[ProposedAction] = []

    def reset(self):
        """Limpa estado interno entre avaliações."""
        self.evidence = []
        self.proposed_actions = []

    def _add_evidence(
        self,
        claim: str,
        source: str,
        confidence: str,
        excerpt: str | None = None,
    ) -> None:
        """Adiciona uma prova ao conjunto de evidências."""
        evidence = Evidence(
            claim=claim,
            source=source,
            confidence=confidence,
            excerpt=excerpt or "",
        )
        self.evidence.append(evidence)

    def _evaluate_alert_severity(self, alert: dict) -> tuple[str, int]:
        """
        Avalia severidade do alerta e retorna (risco, score).
        Score é usado para priorizar ações.
        """
        severity = alert.get("severity", "medium").lower()
        exposure_minutes = alert.get("exposure_window_minutes", 60)

        # Mapa de severidade → score base
        severity_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25,
        }

        score = severity_scores.get(severity, 50)

        # Aumenta score se exposição foi longa
        if exposure_minutes and exposure_minutes > 120:
            score = min(100, score + 20)

        return severity, score

    def evaluate(
        self,
        alert_id: str,
        alert_data: dict,
    ) -> UC08Decision:
        """
        Avalia um alerta de segurança e propõe ações.

        Fluxo:
        1. Extrai dados do alerta
        2. Consulta incidentes abertos para contexto
        3. Coleta evidências
        4. Propõe ações baseado em critérios
        5. Retorna decisão estruturada

        Args:
            alert_id: ID do alerta
            alert_data: Dados brutos do alerta (dict do banco)

        Returns:
            UC08Decision com evidências e ações propostas
        """
        self.reset()

        try:
            severity, risk_score = self._evaluate_alert_severity(alert_data)

            # Evidência 1: Dados do alerta
            self._add_evidence(
                claim=f"Alerta de segurança tipo '{alert_data.get('alert_type')}' com severidade '{severity}'",
                source="security_alert",
                confidence="high",
                excerpt=f"ID: {alert_id}",
            )

            # Evidência 2: Buscar incidentes abertos relacionados
            open_incidents = self.repo.list_open_incidents()
            num_open = len(open_incidents) if open_incidents else 0

            if num_open > 0:
                self._add_evidence(
                    claim=f"Existem {num_open} incidentes abertos no sistema",
                    source="open_incidents",
                    confidence="high",
                    excerpt=f"Incidentes abertos: {num_open}",
                )

            # Decidir ações baseado em tipo de alerta
            alert_type = alert_data.get("alert_type", "unknown")

            if alert_type == "leaked_token":
                self._evaluate_leaked_token(alert_data, risk_score, open_incidents)

            elif alert_type == "compromised_service_account":
                self._evaluate_compromised_service_account(
                    alert_data, risk_score, open_incidents
                )

            elif alert_type == "suspicious_activity":
                self._evaluate_suspicious_activity(alert_data, risk_score)

            else:
                self._add_evidence(
                    claim=f"Tipo de alerta desconhecido: {alert_type}",
                    source="policy",
                    confidence="medium",
                )
                self.proposed_actions.append(
                    ProposedAction(
                        action_type="escalate_incident",
                        reason=f"Alerta de tipo desconhecido '{alert_type}' precisa de revisão humana",
                        risk_level="medium",
                        requires_approval=False,
                    )
                )

            # Preparar decisão final
            decision = UC08Decision(
                alert_id=alert_id,
                status="completed",
                summary=self._generate_summary(alert_data),
                evidence=self.evidence,
                proposed_actions=self.proposed_actions,
                requires_human=self._requires_human_review(),
                request_id=f"uc08-{uuid4().hex[:12]}",
            )

            return decision

        except Exception as e:
            return UC08Decision(
                alert_id=alert_id,
                status="error",
                summary=f"Erro durante avaliação: {str(e)}",
                evidence=self.evidence,
                proposed_actions=self.proposed_actions,
                requires_human=True,
                error_message=str(e),
            )

    def _evaluate_leaked_token(
        self,
        alert: dict,
        risk_score: int,
        open_incidents: list[dict] | None,
    ) -> None:
        """Lógica para token vazado."""
        token_id = alert.get("token_id")
        affected_services = alert.get("affected_services", [])

        # Se token foi usado em múltiplos serviços, risco é maior
        if len(affected_services) > 2:
            self._add_evidence(
                claim=f"Token foi detectado em {len(affected_services)} serviços diferentes",
                source="security_alert",
                confidence="high",
                excerpt=f"Serviços afetados: {', '.join(affected_services)}",
            )
            risk_score = min(100, risk_score + 20)

        # Critério 1: Se risk_score >= 80 E houver incidentes, propõe REVOKE
        if risk_score >= 80 and open_incidents and len(open_incidents) > 0:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="revoke_token",
                    target_id=token_id,
                    reason=f"Token vazado com alta severidade (score: {risk_score}) e incidentes abertos",
                    risk_level="high",
                    requires_approval=True,
                )
            )
            self._add_evidence(
                claim="Há evidência suficiente (severidade alta + incidentes abertos) para revogar token",
                source="policy",
                confidence="high",
            )

        # Critério 2: Se risk_score >= 80 mas SEM incidentes, apenas ESCALATE
        elif risk_score >= 80:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="escalate_incident",
                    reason=f"Token vazado com alta severidade (score: {risk_score}), mas sem incidentes correlatos. Requer revisão.",
                    risk_level="high",
                    requires_approval=False,
                )
            )
            self._add_evidence(
                claim="Severidade alta, mas sem incidentes abertos para correlação",
                source="policy",
                confidence="medium",
            )

        # Critério 3: Se 50 <= risk_score < 80, apenas ESCALATE
        elif risk_score >= 50:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="escalate_incident",
                    reason=f"Token vazado com severidade média (score: {risk_score}). Precisa de análise.",
                    risk_level="medium",
                    requires_approval=False,
                )
            )

        # Critério 4: Se risk_score < 50, nenhuma ação automática
        else:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="none",
                    reason=f"Token vazado com severidade baixa (score: {risk_score}). Monitorar.",
                    risk_level="low",
                    requires_approval=False,
                )
            )
            self._add_evidence(
                claim="Severidade baixa. Não há ação automática recomendada.",
                source="policy",
                confidence="high",
            )

    def _evaluate_compromised_service_account(
        self,
        alert: dict,
        risk_score: int,
        open_incidents: list[dict] | None,
    ) -> None:
        """Lógica para service account comprometida."""
        service_account_id = alert.get("service_account_id")

        # Service account comprometida é extremamente perigosa
        # Requer mais evidência antes de desabilitar

        if risk_score >= 90 and open_incidents and len(open_incidents) > 1:
            # Múltiplas evidências de comprometimento
            self.proposed_actions.append(
                ProposedAction(
                    action_type="disable_service_account",
                    target_id=service_account_id,
                    reason=f"Service account comprometida com alto risco (score: {risk_score}) e múltiplos incidentes",
                    risk_level="critical",
                    requires_approval=True,
                )
            )
            self._add_evidence(
                claim="Evidência suficiente (comprometimento crítico + múltiplos incidentes) para desabilitar conta",
                source="policy",
                confidence="high",
            )

        # Mesmo que crítico, sem múltiplas incidências, escala para humano
        elif risk_score >= 80:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="escalate_incident",
                    reason=f"Service account comprometida com alta severidade (score: {risk_score}). CRÍTICO: requer decisão humana.",
                    risk_level="critical",
                    requires_approval=False,
                )
            )
            self._add_evidence(
                claim="Comprometimento de service account é crítico. Requer aprovação humana especial.",
                source="policy",
                confidence="high",
            )

        else:
            self.proposed_actions.append(
                ProposedAction(
                    action_type="escalate_incident",
                    reason=f"Service account com atividade suspeita (score: {risk_score})",
                    risk_level="high",
                    requires_approval=False,
                )
            )

    def _evaluate_suspicious_activity(
        self,
        alert: dict,
        risk_score: int,
    ) -> None:
        """Lógica para atividade suspeita (requer validação adicional)."""
        self.proposed_actions.append(
            ProposedAction(
                action_type="escalate_incident",
                reason=f"Atividade suspeita detectada (score: {risk_score}). Requer investigação manual.",
                risk_level="medium" if risk_score < 60 else "high",
                requires_approval=False,
            )
        )
        self._add_evidence(
            claim="Atividade suspeita requer investigação manual antes de ações destrutivas",
            source="policy",
            confidence="medium",
        )

    def _requires_human_review(self) -> bool:
        """Verifica se alguma ação requer revisão humana."""
        return any(action.requires_approval for action in self.proposed_actions)

    def _generate_summary(self, alert: dict) -> str:
        """Gera resumo executivo da decisão."""
        alert_type = alert.get("alert_type", "unknown")
        severity = alert.get("severity", "unknown")
        
        return (
            f"Alerta de segurança tipo '{alert_type}' com severidade '{severity}' "
            f"avaliado. {len(self.proposed_actions)} ação(ões) proposta(s). "
            f"Revisão humana: {'Sim' if self._requires_human_review() else 'Não'}."
        )

    def propose_dry_run(self, action: ProposedAction) -> ActionResult | None:
        """
        Executa dry_run de uma ação proposta.

        Args:
            action: Ação a simular

        Returns:
            ActionResult com resultado da simulação
        """
        if action.action_type == "revoke_token":
            return self.repo.revoke_token(
                token_id=action.target_id,
                request_id=action.target_id + "-dryrun",
                reason=action.reason,
                dry_run=True,
            )

        elif action.action_type == "disable_service_account":
            return self.repo.disable_service_account(
                service_account_id=action.target_id,
                request_id=action.target_id + "-dryrun",
                reason=action.reason,
                dry_run=True,
            )

        elif action.action_type == "escalate_incident":
            # Escalate não requer dry_run, é uma ação administrativa
            return ActionResult(
                status="dry_run",
                message=f"Escalação de incidente: {action.reason}",
                changed=False,
            )

        return None
