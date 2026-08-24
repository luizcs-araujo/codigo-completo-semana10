from __future__ import annotations
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from .repository import Repository
from .models import EventEnvelope
from .tools import tool_specs

app = FastAPI(title='OpsPilot Sandbox', version='0.1.0')
repo = Repository()

class WriteRequest(BaseModel):
    request_id: str
    reason: str
    dry_run: bool = True
    approval_token: str | None = None

class ScaleRequest(WriteRequest):
    replicas: int

class FlagRequest(WriteRequest):
    percentage: int

class CreditMemoRequest(WriteRequest):
    amount_cents: int

class QuarantineRequest(WriteRequest):
    test_name: str

class EscalateRequest(WriteRequest):
    owner: str

class ReprocessRequest(WriteRequest):
    partition: str

class WatermarkRequest(WriteRequest):
    watermark: str

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/tools')
def tools():
    return tool_specs()

@app.get('/api/tickets/{ticket_id}')
def get_ticket(ticket_id: str):
    return repo.get_ticket(ticket_id) or {'error': 'not_found'}

@app.get('/api/services/{service_id}/health')
def service_health(service_id: str):
    return repo.get_service_health(service_id) or {'error': 'not_found'}

@app.get('/api/services/{service_id}/deploys')
def deploys(service_id: str):
    return repo.get_recent_deploys(service_id)

@app.post('/api/services/{service_id}/restart')
def restart(service_id: str, body: WriteRequest):
    try:
        return repo.restart_service(service_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/api/services/{service_id}/scale')
def scale(service_id: str, body: ScaleRequest):
    try:
        return repo.scale_service(service_id, body.replicas, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/feature-flags/{flag_key}')
def get_flag(flag_key: str):
    return repo.get_feature_flag(flag_key) or {'error': 'not_found'}

@app.post('/api/feature-flags/{flag_key}/rollout')
def set_flag(flag_key: str, body: FlagRequest):
    try:
        return repo.set_feature_flag_rollout(flag_key, body.percentage, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/users/{user_id}/permissions')
def permissions(user_id: str):
    return repo.get_user_permissions(user_id) or {'error': 'not_found'}

@app.post('/api/users/{user_id}/invalidate-cache')
def invalidate_cache(user_id: str, body: WriteRequest):
    try:
        return repo.invalidate_permission_cache(user_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/api/users/{user_id}/sync-role')
def sync_role(user_id: str, body: WriteRequest):
    try:
        return repo.sync_user_role(user_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/pipelines/{run_id}')
def pipeline(run_id: str):
    return repo.get_pipeline_run(run_id) or {'error': 'not_found'}

@app.post('/api/pipelines/{run_id}/rerun')
def rerun(run_id: str, body: WriteRequest):
    try:
        return repo.rerun_pipeline(run_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/api/pipelines/{run_id}/quarantine-test')
def quarantine(run_id: str, body: QuarantineRequest):
    try:
        return repo.quarantine_test(run_id, body.test_name, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/billing/{account_id}')
def billing(account_id: str):
    return repo.get_billing_account(account_id) or {'error': 'not_found'}

@app.post('/api/billing/{account_id}/credit-memo')
def credit(account_id: str, body: CreditMemoRequest):
    try:
        return repo.issue_credit_memo(account_id, body.amount_cents, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/data-pipelines/{pipeline_id}')
def data_pipeline(pipeline_id: str):
    return repo.get_data_pipeline_status(pipeline_id) or {'error': 'not_found'}

@app.post('/api/data-pipelines/{pipeline_id}/reprocess')
def reprocess(pipeline_id: str, body: ReprocessRequest):
    try:
        return repo.reprocess_data_partition(pipeline_id, body.partition, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/api/data-pipelines/{pipeline_id}/watermark')
def watermark(pipeline_id: str, body: WatermarkRequest):
    try:
        return repo.update_pipeline_watermark(pipeline_id, body.watermark, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/security-alerts/{alert_id}')
def security_alert(alert_id: str):
    return repo.get_security_alert(alert_id) or {'error': 'not_found'}

@app.post('/api/security/tokens/{token_id}/revoke')
def revoke(token_id: str, body: WriteRequest):
    try:
        return repo.revoke_token(token_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/api/security/service-accounts/{service_account_id}/disable')
def disable_sa(service_account_id: str, body: WriteRequest):
    try:
        return repo.disable_service_account(service_account_id, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get('/api/incidents')
def incidents(service_id: str | None = None):
    return repo.list_open_incidents(service_id)

@app.post('/api/incidents/{incident_id}/escalate')
def escalate(incident_id: str, body: EscalateRequest):
    try:
        return repo.escalate_incident(incident_id, body.owner, body.request_id, body.reason, body.dry_run, body.approval_token)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post('/webhooks/events')
def receive_event(event: EventEnvelope, x_signature: str | None = Header(default=None)):
    # Em produção, validar assinatura. Aqui fica propositalmente simples para os trios implementarem política.
    return repo.record_event(event.event_id, event.event_type, event.source, event.payload)

@app.get('/api/audit')
def audit():
    return repo.list_audit()
