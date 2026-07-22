"""
Modelos Pydantic para UC08: Resposta a token vazado e service account perigosa.

Estruturas de dados para capturar evidências, decisões e ações propostas.
"""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field


class SecurityAlertData(BaseModel):
    """Dados de um alerta de segurança recuperado."""
    id: str
    alert_type: Literal["leaked_token", "compromised_service_account", "suspicious_activity"]
    severity: Literal["low", "medium", "high", "critical"]
    token_id: str | None = None
    service_account_id: str | None = None
    discovered_at: str  # ISO datetime
    exposure_window_minutes: int | None = None
    affected_services: list[str] = Field(default_factory=list)
    created_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Uma fonte ou prova que suporta a decisão do agente."""
    claim: str
    """Afirmação feita (ex: 'token foi usado em 3 serviços diferentes')"""
    
    source: Literal["security_alert", "open_incidents", "policy", "manual_review"]
    """De onde veio a evidência"""
    
    confidence: Literal["low", "medium", "high"]
    """Quão confiante o agente está nesta evidência"""
    
    excerpt: str | None = None
    """Trecho dos dados que suporta a claim"""


class ProposedAction(BaseModel):
    """Uma ação que o agente está considerando tomar."""
    action_type: Literal["revoke_token", "disable_service_account", "escalate_incident", "none"]
    target_id: str | None = None
    reason: str
    risk_level: Literal["low", "medium", "high", "critical"]
    requires_approval: bool
    dry_run_result: dict[str, Any] | None = None
    """Resultado de um dry_run, se executado"""


class UC08Decision(BaseModel):
    """Decisão final do agente para um alerta de segurança."""
    alert_id: str
    status: Literal["completed", "needs_human", "blocked", "error"]
    """
    - completed: ação executada com sucesso
    - needs_human: agente parou e pede aprovação
    - blocked: agente bloqueou por falta de evidência ou autorização
    - error: erro durante processamento
    """
    
    summary: str
    """Resumo executivo da decisão"""
    
    evidence: list[Evidence] = Field(default_factory=list)
    """Todas as evidências coletadas"""
    
    proposed_actions: list[ProposedAction] = Field(default_factory=list)
    """Ações que o agente está propondo"""
    
    action_executed: ProposedAction | None = None
    """A ação que foi realmente executada, se houver"""
    
    request_id: str | None = None
    """ID idempotente da operação"""
    
    audit_ids: list[int] = Field(default_factory=list)
    """IDs dos registros no audit_log"""
    
    requires_human: bool
    """Se necessita aprovação ou revisão humana"""
    
    error_message: str | None = None
    """Se houver erro, a mensagem"""
    
    limitations: list[str] = Field(default_factory=list)
    """Limitações conhecidas durante este run"""


class UC08RunSummary(BaseModel):
    """Resumo completo de uma execução do agente UC08."""
    run_id: str
    alert_id: str
    decision: UC08Decision
    tools_called: list[str] = Field(default_factory=list)
    model_calls: int = 0
    total_tokens_used: int | None = None
    trace_url: str | None = None
    duration_seconds: float | None = None
    timestamp: str  # ISO datetime


class ApprovalRequest(BaseModel):
    """Requisição de aprovação humana para uma ação perigosa."""
    action: ProposedAction
    evidence: list[Evidence]
    alert_id: str
    request_id: str
    risk_assessment: str
    """Descrição de riscos da ação proposta"""
