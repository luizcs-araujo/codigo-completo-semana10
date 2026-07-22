"""
Handlers de aprovação e execução para UC08.

Responsável por:
1. Apresentar ações propostas ao humano
2. Coletar aprovação ou rejeição
3. Executar ações com approval_token
4. Registrar no audit_log
5. Capturar erros e retornar feedback
"""
from __future__ import annotations
import json
import sys
from typing import Any, Callable

from .uc08_models import ProposedAction, ApprovalRequest, Evidence
from .repository import Repository
from .models import ActionResult
from .policies import DEMO_APPROVAL_TOKEN
from .tracing import traced


class ApprovalManager:
    """Gerencia fluxo de aprovação e execução de ações."""

    def __init__(self, repo: Repository | None = None, auto_approve: bool = False):
        """
        Args:
            repo: Repository para operações
            auto_approve: Se True, aprova automaticamente (apenas para testes)
        """
        self.repo = repo or Repository()
        self.auto_approve = auto_approve

    @traced(name="uc08_request_approval", run_type="tool")
    def request_approval(
        self,
        action: ProposedAction,
        evidence: list[Evidence],
        alert_id: str,
        request_id: str,
    ) -> bool:
        """
        Solicita aprovação humana para uma ação.

        Presenta evidências e riscos, pergunta sim/não.

        Args:
            action: Ação proposta
            evidence: Evidências que suportam a decisão
            alert_id: ID do alerta
            request_id: ID idempotente

        Returns:
            True se aprovada, False se rejeitada
        """
        if self.auto_approve:
            print(f"[AUTO-APPROVE] {action.action_type} para {action.target_id}")
            return True

        print("\n" + "=" * 70)
        print("⚠️  APROVAÇÃO NECESSÁRIA PARA AÇÃO DE SEGURANÇA")
        print("=" * 70)

        print(f"\n📋 Alerta: {alert_id}")
        print(f"🔑 Request ID: {request_id}")
        print(f"\n🎯 Ação proposta: {action.action_type}")
        if action.target_id:
            print(f"   Target: {action.target_id}")
        print(f"   Razão: {action.reason}")
        print(f"   Risco: {action.risk_level.upper()}")
        print(f"   Requer aprovação: {'Sim' if action.requires_approval else 'Não'}")

        if evidence:
            print(f"\n📊 Evidências coletadas ({len(evidence)}):")
            for i, ev in enumerate(evidence, 1):
                print(f"   {i}. [{ev.source}] {ev.claim}")
                if ev.excerpt:
                    print(f"      → {ev.excerpt[:60]}...")
                print(f"      Confiança: {ev.confidence}")

        print("\n" + "-" * 70)
        print("Riscos potenciais:")
        risk_msg = self._assess_risk(action)
        for line in risk_msg.split("\n"):
            print(f"  ⚡ {line}")

        print("\n" + "-" * 70)
        response = input("\n👤 Aprovar execução? [s/N]: ").strip().lower()
        approved = response in {"s", "sim", "y", "yes"}

        if approved:
            print("✅ Aprovado pelo operador humano")
        else:
            print("❌ Rejeitado pelo operador humano")

        print("=" * 70 + "\n")
        return approved

    def _assess_risk(self, action: ProposedAction) -> str:
        """Descreve riscos específicos da ação."""
        risks = {
            "revoke_token": (
                "Revogação de token pode causar autenticação falha\n"
                "para aplicações legítimas que usam este token."
            ),
            "disable_service_account": (
                "Desabilitar service account pode derrubar processos críticos\n"
                "que dependem desta conta para operação."
            ),
            "escalate_incident": (
                "Escalação criará ticket/incidente que pode exigir\n"
                "ação manual imediata de segurança."
            ),
            "none": "Nenhuma ação automática será tomada.",
        }
        return risks.get(action.action_type, "Risco desconhecido")

    @traced(name="uc08_execute_action", run_type="tool")
    def execute_action(
        self,
        action: ProposedAction,
        alert_id: str,
        request_id: str,
        dry_run_first: bool = True,
    ) -> tuple[ActionResult, bool]:
        """
        Executa uma ação proposta.

        Fluxo:
        1. Se dry_run_first=True, simular primeiro
        2. Executar com approval_token
        3. Capturar resultado
        4. Registrar em audit_log

        Args:
            action: Ação a executar
            alert_id: ID do alerta
            request_id: ID idempotente
            dry_run_first: Se deve fazer dry_run antes

        Returns:
            Tuple (resultado, sucesso)
        """
        # Passo 1: Dry-run (se configurado)
        if dry_run_first and action.action_type != "none":
            print(f"\n🔄 Executando DRY-RUN de {action.action_type}...")
            dry_result = self._call_action_tool(
                action, request_id, dry_run=True
            )
            print(f"   Resultado: {dry_result.status}")
            if dry_result.status == "dry_run":
                action.dry_run_result = dry_result.data
                print(f"   ✓ Simulação bem-sucedida")

        # Passo 2: Execução real (com approval_token)
        if action.action_type == "none":
            result = ActionResult(
                status="executed",
                message="Nenhuma ação automática necessária",
                changed=False,
                request_id=request_id,
            )
            return result, True

        print(f"\n⚡ Executando {action.action_type} para {action.target_id}...")
        result = self._call_action_tool(
            action,
            request_id,
            dry_run=False,
            approval_token=DEMO_APPROVAL_TOKEN,
        )

        success = result.status == "executed"
        if success:
            print(f"   ✅ Executado com sucesso (audit_id: {result.audit_id})")
        else:
            print(f"   ❌ Falha: {result.message}")

        return result, success

    def _call_action_tool(
        self,
        action: ProposedAction,
        request_id: str,
        dry_run: bool = True,
        approval_token: str | None = None,
    ) -> ActionResult:
        """Chama a tool apropriada baseado no tipo de ação."""
        try:
            if action.action_type == "revoke_token":
                return self.repo.revoke_token(
                    token_id=action.target_id,
                    request_id=request_id,
                    reason=action.reason,
                    dry_run=dry_run,
                    approval_token=approval_token,
                )

            elif action.action_type == "disable_service_account":
                return self.repo.disable_service_account(
                    service_account_id=action.target_id,
                    request_id=request_id,
                    reason=action.reason,
                    dry_run=dry_run,
                    approval_token=approval_token,
                )

            elif action.action_type == "escalate_incident":
                # Escalate cria um incidente mas não requer aprovação explícita
                return self.repo.escalate_incident(
                    incident_id=f"sec-{request_id}",
                    owner="security-team",
                    request_id=request_id,
                    reason=action.reason,
                    dry_run=dry_run,
                    approval_token=None,
                )

            else:
                return ActionResult(
                    status="failed",
                    message=f"Tipo de ação desconhecido: {action.action_type}",
                    changed=False,
                )

        except PermissionError as e:
            return ActionResult(
                status="blocked",
                message=str(e),
                changed=False,
                request_id=request_id,
            )
        except Exception as e:
            return ActionResult(
                status="failed",
                message=f"Erro ao executar {action.action_type}: {str(e)}",
                changed=False,
                request_id=request_id,
            )

    @traced(name="uc08_prompt_approval", run_type="tool")
    def prompt_approval(self, action_dict: dict[str, Any]) -> bool:
        """
        Compatível com middleware HITL.

        Middleware chama esta função para pedir aprovação.
        """
        action_name = action_dict.get("name", "unknown")
        arguments = action_dict.get("arguments", {})

        print("\n" + "=" * 70)
        print(f"🔒 MIDDLEWARE HITL: Aprovação necessária para {action_name}")
        print("=" * 70)
        print(json.dumps(arguments, indent=2, ensure_ascii=False))
        print("-" * 70)

        response = input("\n👤 Aprovar? [s/N]: ").strip().lower()
        approved = response in {"s", "sim", "y", "yes"}

        if approved:
            print("✅ Aprovado")
        else:
            print("❌ Rejeitado")

        print("=" * 70 + "\n")
        return approved


class ExecutionLogger:
    """Registra execução de ações para auditoria."""

    def __init__(self, output_file: str | None = None):
        """
        Args:
            output_file: Arquivo para salvar logs (stdout se None)
        """
        self.output_file = output_file
        self.logs: list[dict] = []

    def log_approval_requested(
        self,
        action: ProposedAction,
        alert_id: str,
        request_id: str,
    ) -> None:
        """Registra solicitação de aprovação."""
        entry = {
            "event": "approval_requested",
            "action_type": action.action_type,
            "target_id": action.target_id,
            "alert_id": alert_id,
            "request_id": request_id,
            "timestamp": self._timestamp(),
        }
        self.logs.append(entry)
        self._print(entry)

    def log_approval_decision(
        self,
        action: ProposedAction,
        approved: bool,
        request_id: str,
    ) -> None:
        """Registra decisão de aprovação."""
        entry = {
            "event": "approval_decision",
            "action_type": action.action_type,
            "approved": approved,
            "request_id": request_id,
            "timestamp": self._timestamp(),
        }
        self.logs.append(entry)
        self._print(entry)

    def log_action_executed(
        self,
        action: ProposedAction,
        result: ActionResult,
        request_id: str,
    ) -> None:
        """Registra execução de ação."""
        entry = {
            "event": "action_executed",
            "action_type": action.action_type,
            "target_id": action.target_id,
            "status": result.status,
            "changed": result.changed,
            "audit_id": result.audit_id,
            "request_id": request_id,
            "timestamp": self._timestamp(),
        }
        self.logs.append(entry)
        self._print(entry)

    def _print(self, entry: dict) -> None:
        """Imprime entrada em arquivo ou stdout."""
        line = json.dumps(entry, ensure_ascii=False, default=str)
        if self.output_file:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        else:
            print(f"[AUDIT] {line}", file=sys.stderr)

    def _timestamp(self) -> str:
        """Retorna timestamp ISO8601."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def get_logs(self) -> list[dict]:
        """Retorna todos os logs capturados."""
        return self.logs.copy()


# Funções de conveniência para usar em main_uc08.py

def make_approval_handler(
    approval_manager: ApprovalManager,
    logger: ExecutionLogger | None = None,
) -> Callable[[dict[str, Any]], bool]:
    """
    Cria handler de aprovação compatível com middleware HITL.

    Returns:
        Função que middleware pode chamar
    """

    def handler(action_dict: dict[str, Any]) -> bool:
        approved = approval_manager.prompt_approval(action_dict)
        if logger:
            logger.log_approval_decision(
                action=ProposedAction(
                    action_type=action_dict.get("name", "unknown"),
                    reason="via_middleware",
                    risk_level="high",
                    requires_approval=True,
                ),
                approved=approved,
                request_id="middleware",
            )
        return approved

    return handler
