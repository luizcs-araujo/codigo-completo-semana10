from __future__ import annotations
from typing import Any
import json
from .database import connect
from .models import ActionResult
from .policies import assert_allowed

ACTOR = 'agent-or-human-operator'

def row_to_dict(row) -> dict[str, Any] | None:
    return dict(row) if row else None

class Repository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def _fetchone(self, sql: str, args=()):
        with connect(self.db_path) as conn:
            return row_to_dict(conn.execute(sql, args).fetchone())

    def _fetchall(self, sql: str, args=()):
        with connect(self.db_path) as conn:
            return [dict(r) for r in conn.execute(sql, args).fetchall()]

    def get_ticket(self, ticket_id: str):
        return self._fetchone('SELECT * FROM tickets WHERE id=?', (ticket_id,))

    def get_service_health(self, service_id: str):
        return self._fetchone('SELECT * FROM services WHERE id=?', (service_id,))

    def get_recent_deploys(self, service_id: str):
        return self._fetchall('SELECT * FROM deployments WHERE service_id=? ORDER BY started_at DESC LIMIT 5', (service_id,))

    def get_feature_flag(self, flag_key: str):
        return self._fetchone('SELECT * FROM feature_flags WHERE key=?', (flag_key,))

    def get_pipeline_run(self, run_id: str):
        return self._fetchone('SELECT * FROM pipeline_runs WHERE id=?', (run_id,))

    def get_user_permissions(self, user_id: str):
        return self._fetchone('SELECT * FROM users WHERE id=?', (user_id,))

    def get_billing_account(self, account_id: str):
        return self._fetchone('SELECT * FROM billing_accounts WHERE id=?', (account_id,))

    def get_data_pipeline_status(self, pipeline_id: str):
        return self._fetchone('SELECT * FROM data_pipelines WHERE id=?', (pipeline_id,))

    def get_security_alert(self, alert_id: str):
        return self._fetchone('SELECT * FROM security_alerts WHERE id=?', (alert_id,))

    def list_open_incidents(self, service_id: str | None = None):
        if service_id:
            return self._fetchall('SELECT * FROM incidents WHERE service_id=? AND status != "closed"', (service_id,))
        return self._fetchall('SELECT * FROM incidents WHERE status != "closed"')

    def list_audit(self):
        return self._fetchall('SELECT * FROM audit_log ORDER BY id DESC LIMIT 50')

    def record_event(self, event_id: str, event_type: str, source: str, payload: dict[str, Any]):
        with connect(self.db_path) as conn:
            conn.execute('INSERT OR IGNORE INTO events(event_id,event_type,source,payload_json) VALUES (?,?,?,?)',
                         (event_id, event_type, source, json.dumps(payload, ensure_ascii=False)))
            conn.commit()
        return {'event_id': event_id, 'accepted': True}

    def _audit(self, request_id: str | None, action: str, target: str, dry_run: bool, status: str, details: dict[str, Any]) -> int:
        with connect(self.db_path) as conn:
            cur = conn.execute(
                'INSERT INTO audit_log(request_id,actor,action,target,dry_run,status,details) VALUES (?,?,?,?,?,?,?)',
                (request_id, ACTOR, action, target, int(dry_run), status, json.dumps(details, ensure_ascii=False))
            )
            conn.commit()
            return int(cur.lastrowid)

    def _duplicate(self, request_id: str, action: str) -> ActionResult | None:
        with connect(self.db_path) as conn:
            row = conn.execute('SELECT * FROM audit_log WHERE request_id=? AND action=? AND dry_run=0', (request_id, action)).fetchone()
            if not row:
                return None
            return ActionResult(status='duplicate', message='request_id já executado para esta ação', changed=False, request_id=request_id, audit_id=row['id'], data=dict(row))

    def _guard(self, action: str, target: str, request_id: str | None, reason: str, dry_run: bool, approval_token: str | None) -> ActionResult | None:
        assert_allowed(action, dry_run, approval_token, request_id)
        if request_id and not dry_run:
            dup = self._duplicate(request_id, action)
            if dup:
                return dup
        if dry_run:
            audit_id = self._audit(request_id, action, target, True, 'dry_run', {'reason': reason})
            return ActionResult(status='dry_run', message=f'{action} simulado para {target}', changed=False, request_id=request_id, audit_id=audit_id)
        return None

    def restart_service(self, service_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('restart_service', service_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE services SET status="healthy", error_rate=0.01, latency_ms=300 WHERE id=?', (service_id,))
            conn.commit()
        audit_id = self._audit(request_id, 'restart_service', service_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'serviço {service_id} reiniciado', changed=True, request_id=request_id, audit_id=audit_id)

    def scale_service(self, service_id: str, replicas: int, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('scale_service', service_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE services SET replicas=? WHERE id=?', (replicas, service_id))
            conn.commit()
        audit_id = self._audit(request_id, 'scale_service', service_id, False, 'executed', {'reason': reason, 'replicas': replicas})
        return ActionResult(status='executed', message=f'{service_id} escalado para {replicas} réplicas', changed=True, request_id=request_id, audit_id=audit_id)

    def set_feature_flag_rollout(self, flag_key: str, percentage: int, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('set_feature_flag_rollout', flag_key, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE feature_flags SET percentage=?, last_changed_at=CURRENT_TIMESTAMP WHERE key=?', (percentage, flag_key))
            conn.commit()
        audit_id = self._audit(request_id, 'set_feature_flag_rollout', flag_key, False, 'executed', {'reason': reason, 'percentage': percentage})
        return ActionResult(status='executed', message=f'flag {flag_key} ajustada para {percentage}%', changed=True, request_id=request_id, audit_id=audit_id)

    def invalidate_permission_cache(self, user_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('invalidate_permission_cache', user_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE users SET permission_cache_state="fresh" WHERE id=?', (user_id,))
            conn.commit()
        audit_id = self._audit(request_id, 'invalidate_permission_cache', user_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'cache de permissões invalidado para {user_id}', changed=True, request_id=request_id, audit_id=audit_id)

    def sync_user_role(self, user_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('sync_user_role', user_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        audit_id = self._audit(request_id, 'sync_user_role', user_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'sync de role solicitado para {user_id}', changed=True, request_id=request_id, audit_id=audit_id)

    def issue_credit_memo(self, account_id: str, amount_cents: int, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('issue_credit_memo', account_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE billing_accounts SET balance_cents=balance_cents-?, dispute_status="credit_issued" WHERE id=?', (amount_cents, account_id))
            conn.commit()
        audit_id = self._audit(request_id, 'issue_credit_memo', account_id, False, 'executed', {'reason': reason, 'amount_cents': amount_cents})
        return ActionResult(status='executed', message=f'crédito de {amount_cents} centavos emitido para {account_id}', changed=True, request_id=request_id, audit_id=audit_id)

    def quarantine_test(self, run_id: str, test_name: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('quarantine_test', run_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        audit_id = self._audit(request_id, 'quarantine_test', run_id, False, 'executed', {'reason': reason, 'test_name': test_name})
        return ActionResult(status='executed', message=f'teste {test_name} marcado para quarentena em {run_id}', changed=True, request_id=request_id, audit_id=audit_id)

    def rerun_pipeline(self, run_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('rerun_pipeline', run_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        audit_id = self._audit(request_id, 'rerun_pipeline', run_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'pipeline {run_id} reenfileirado', changed=True, request_id=request_id, audit_id=audit_id)

    def escalate_incident(self, incident_id: str, owner: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('escalate_incident', incident_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE incidents SET owner=?, status="escalated" WHERE id=?', (owner, incident_id))
            conn.commit()
        audit_id = self._audit(request_id, 'escalate_incident', incident_id, False, 'executed', {'reason': reason, 'owner': owner})
        return ActionResult(status='executed', message=f'incidente {incident_id} escalado para {owner}', changed=True, request_id=request_id, audit_id=audit_id)

    def reprocess_data_partition(self, pipeline_id: str, partition: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('reprocess_data_partition', pipeline_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE data_pipelines SET status="reprocessing", last_error=NULL WHERE id=?', (pipeline_id,))
            conn.commit()
        audit_id = self._audit(request_id, 'reprocess_data_partition', pipeline_id, False, 'executed', {'reason': reason, 'partition': partition})
        return ActionResult(status='executed', message=f'partição {partition} reenfileirada em {pipeline_id}', changed=True, request_id=request_id, audit_id=audit_id)

    def update_pipeline_watermark(self, pipeline_id: str, watermark: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('update_pipeline_watermark', pipeline_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        with connect(self.db_path) as conn:
            conn.execute('UPDATE data_pipelines SET watermark=? WHERE id=?', (watermark, pipeline_id))
            conn.commit()
        audit_id = self._audit(request_id, 'update_pipeline_watermark', pipeline_id, False, 'executed', {'reason': reason, 'watermark': watermark})
        return ActionResult(status='executed', message=f'watermark de {pipeline_id} atualizado para {watermark}', changed=True, request_id=request_id, audit_id=audit_id)

    def revoke_token(self, token_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('revoke_token', token_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        audit_id = self._audit(request_id, 'revoke_token', token_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'token {token_id} revogado', changed=True, request_id=request_id, audit_id=audit_id)

    def disable_service_account(self, service_account_id: str, request_id: str, reason: str, dry_run: bool=True, approval_token: str | None=None):
        guarded = self._guard('disable_service_account', service_account_id, request_id, reason, dry_run, approval_token)
        if guarded: return guarded
        audit_id = self._audit(request_id, 'disable_service_account', service_account_id, False, 'executed', {'reason': reason})
        return ActionResult(status='executed', message=f'service account {service_account_id} desabilitada', changed=True, request_id=request_id, audit_id=audit_id)
