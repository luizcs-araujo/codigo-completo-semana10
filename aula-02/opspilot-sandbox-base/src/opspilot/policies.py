from __future__ import annotations
from dataclasses import dataclass
from .models import RiskLevel

DEMO_APPROVAL_TOKEN = 'APPROVED-LOCAL-DEMO'

@dataclass(frozen=True)
class Policy:
    risk: RiskLevel
    requires_approval: bool
    writes_state: bool
    idempotency_required: bool

POLICIES: dict[str, Policy] = {
    'get_ticket': Policy(RiskLevel.read_only, False, False, False),
    'get_service_health': Policy(RiskLevel.read_only, False, False, False),
    'get_recent_deploys': Policy(RiskLevel.read_only, False, False, False),
    'get_feature_flag': Policy(RiskLevel.read_only, False, False, False),
    'get_pipeline_run': Policy(RiskLevel.read_only, False, False, False),
    'get_user_permissions': Policy(RiskLevel.read_only, False, False, False),
    'get_billing_account': Policy(RiskLevel.read_only, False, False, False),
    'get_data_pipeline_status': Policy(RiskLevel.read_only, False, False, False),
    'get_security_alert': Policy(RiskLevel.read_only, False, False, False),
    'list_open_incidents': Policy(RiskLevel.read_only, False, False, False),

    'restart_service': Policy(RiskLevel.write_sensitive, True, True, True),
    'scale_service': Policy(RiskLevel.write_sensitive, True, True, True),
    'set_feature_flag_rollout': Policy(RiskLevel.write_sensitive, True, True, True),
    'invalidate_permission_cache': Policy(RiskLevel.write_safe, True, True, True),
    'sync_user_role': Policy(RiskLevel.write_sensitive, True, True, True),
    'issue_credit_memo': Policy(RiskLevel.write_sensitive, True, True, True),
    'quarantine_test': Policy(RiskLevel.write_sensitive, True, True, True),
    'rerun_pipeline': Policy(RiskLevel.write_safe, False, True, True),
    'escalate_incident': Policy(RiskLevel.write_safe, False, True, True),
    'reprocess_data_partition': Policy(RiskLevel.write_sensitive, True, True, True),
    'update_pipeline_watermark': Policy(RiskLevel.write_sensitive, True, True, True),
    'revoke_token': Policy(RiskLevel.destructive, True, True, True),
    'disable_service_account': Policy(RiskLevel.destructive, True, True, True),
}

def assert_allowed(action: str, dry_run: bool, approval_token: str | None, request_id: str | None) -> None:
    policy = POLICIES[action]
    if policy.idempotency_required and not request_id:
        raise PermissionError(f'{action} exige request_id para idempotência')
    if dry_run:
        return
    if policy.requires_approval and approval_token != DEMO_APPROVAL_TOKEN:
        raise PermissionError(f'{action} exige approval_token válido para execução real')
