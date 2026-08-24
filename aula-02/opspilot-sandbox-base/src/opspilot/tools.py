from __future__ import annotations
from typing import Optional
from langchain_core.tools import tool
from .repository import Repository
from .models import ToolSpec
from .policies import POLICIES

repo = Repository()

def _jsonable(result):
    if hasattr(result, 'model_dump'):
        return result.model_dump()
    return result

@tool
def get_ticket(ticket_id: str) -> dict:
    """Busca um ticket pelo ID. Tool somente leitura."""
    return repo.get_ticket(ticket_id) or {'error': 'ticket_not_found'}

@tool
def get_service_health(service_id: str) -> dict:
    """Busca saúde, latência, taxa de erro e réplicas de um serviço."""
    return repo.get_service_health(service_id) or {'error': 'service_not_found'}

@tool
def get_recent_deploys(service_id: str) -> list[dict]:
    """Lista deployments recentes de um serviço."""
    return repo.get_recent_deploys(service_id)

@tool
def get_feature_flag(flag_key: str) -> dict:
    """Consulta uma feature flag e seu percentual atual."""
    return repo.get_feature_flag(flag_key) or {'error': 'flag_not_found'}

@tool
def get_pipeline_run(run_id: str) -> dict:
    """Busca status, job e testes falhos de uma execução de CI/CD."""
    return repo.get_pipeline_run(run_id) or {'error': 'pipeline_run_not_found'}

@tool
def get_user_permissions(user_id: str) -> dict:
    """Busca role, permissões e estado do cache de permissões de um usuário."""
    return repo.get_user_permissions(user_id) or {'error': 'user_not_found'}

@tool
def get_billing_account(account_id: str) -> dict:
    """Busca saldo, cobrança duplicada e status de disputa de uma conta de billing."""
    return repo.get_billing_account(account_id) or {'error': 'account_not_found'}

@tool
def get_data_pipeline_status(pipeline_id: str) -> dict:
    """Busca status, watermark e erro recente de um pipeline de dados."""
    return repo.get_data_pipeline_status(pipeline_id) or {'error': 'pipeline_not_found'}

@tool
def get_security_alert(alert_id: str) -> dict:
    """Busca alerta de segurança com token ou service account envolvida."""
    return repo.get_security_alert(alert_id) or {'error': 'alert_not_found'}

@tool
def list_open_incidents(service_id: Optional[str] = None) -> list[dict]:
    """Lista incidentes abertos, opcionalmente filtrados por serviço."""
    return repo.list_open_incidents(service_id)

@tool
def restart_service(service_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Reinicia um serviço. Ação sensível: use dry_run antes e aprovação para execução real."""
    return _jsonable(repo.restart_service(service_id, request_id, reason, dry_run, approval_token))

@tool
def scale_service(service_id: str, replicas: int, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Altera número de réplicas de um serviço. Ação sensível."""
    return _jsonable(repo.scale_service(service_id, replicas, request_id, reason, dry_run, approval_token))

@tool
def set_feature_flag_rollout(flag_key: str, percentage: int, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Altera percentual de rollout de uma feature flag. Ação sensível."""
    return _jsonable(repo.set_feature_flag_rollout(flag_key, percentage, request_id, reason, dry_run, approval_token))

@tool
def invalidate_permission_cache(user_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Invalida cache de permissões de um usuário. Ação de escrita controlada."""
    return _jsonable(repo.invalidate_permission_cache(user_id, request_id, reason, dry_run, approval_token))

@tool
def sync_user_role(user_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Solicita sincronização de role de usuário. Ação sensível."""
    return _jsonable(repo.sync_user_role(user_id, request_id, reason, dry_run, approval_token))

@tool
def issue_credit_memo(account_id: str, amount_cents: int, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Emite crédito financeiro em uma conta. Ação sensível."""
    return _jsonable(repo.issue_credit_memo(account_id, amount_cents, request_id, reason, dry_run, approval_token))

@tool
def quarantine_test(run_id: str, test_name: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Marca um teste como quarentenado. Ação sensível de CI/CD."""
    return _jsonable(repo.quarantine_test(run_id, test_name, request_id, reason, dry_run, approval_token))

@tool
def rerun_pipeline(run_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Reexecuta uma pipeline. Ação de escrita controlada."""
    return _jsonable(repo.rerun_pipeline(run_id, request_id, reason, dry_run, approval_token))

@tool
def escalate_incident(incident_id: str, owner: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Escala incidente para um responsável. Ação de escrita controlada."""
    return _jsonable(repo.escalate_incident(incident_id, owner, request_id, reason, dry_run, approval_token))

@tool
def reprocess_data_partition(pipeline_id: str, partition: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Reprocessa partição de dados. Ação sensível e onerosa."""
    return _jsonable(repo.reprocess_data_partition(pipeline_id, partition, request_id, reason, dry_run, approval_token))

@tool
def update_pipeline_watermark(pipeline_id: str, watermark: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Atualiza watermark de pipeline de dados. Ação sensível."""
    return _jsonable(repo.update_pipeline_watermark(pipeline_id, watermark, request_id, reason, dry_run, approval_token))

@tool
def revoke_token(token_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Revoga token comprometido. Ação destrutiva."""
    return _jsonable(repo.revoke_token(token_id, request_id, reason, dry_run, approval_token))

@tool
def disable_service_account(service_account_id: str, request_id: str, reason: str, dry_run: bool = True, approval_token: Optional[str] = None) -> dict:
    """Desabilita service account. Ação destrutiva."""
    return _jsonable(repo.disable_service_account(service_account_id, request_id, reason, dry_run, approval_token))

ALL_TOOLS = [
    get_ticket, get_service_health, get_recent_deploys, get_feature_flag, get_pipeline_run,
    get_user_permissions, get_billing_account, get_data_pipeline_status, get_security_alert,
    list_open_incidents, restart_service, scale_service, set_feature_flag_rollout,
    invalidate_permission_cache, sync_user_role, issue_credit_memo, quarantine_test,
    rerun_pipeline, escalate_incident, reprocess_data_partition, update_pipeline_watermark,
    revoke_token, disable_service_account,
]

def tool_specs() -> list[dict]:
    specs = []
    for t in ALL_TOOLS:
        policy = POLICIES[t.name]
        specs.append(ToolSpec(
            name=t.name,
            description=t.description or '',
            risk=policy.risk,
            requires_approval=policy.requires_approval,
            idempotency_required=policy.idempotency_required,
            writes_state=policy.writes_state,
            tags=[],
        ).model_dump())
    return specs
