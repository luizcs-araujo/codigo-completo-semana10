from __future__ import annotations
import uuid

EVENTS = {
    'monitoring_error_spike': {
        'event_type': 'monitoring.error_spike',
        'source': 'mock-monitoring',
        'payload': {'service_id': 'checkout-api', 'incident_id': 'INC-501', 'error_rate': 0.19, 'flag_key': 'checkout_new_router'}
    },
    'permission_403': {
        'event_type': 'support.permission_403',
        'source': 'support-queue',
        'payload': {'ticket_id': 'TCK-4031', 'user_id': 'u-maria', 'service_id': 'analytics-api'}
    },
    'billing_duplicate_charge': {
        'event_type': 'billing.duplicate_charge',
        'source': 'billing-monitor',
        'payload': {'ticket_id': 'TCK-BILL9', 'account_id': 'acct-100', 'amount_cents': 49900}
    },
    'cicd_pipeline_failed': {
        'event_type': 'cicd.pipeline_failed',
        'source': 'github-actions-mock',
        'payload': {'run_id': 'RUN-1842', 'repo': 'checkout-service'}
    },
    'data_pipeline_stuck': {
        'event_type': 'data.pipeline_stuck',
        'source': 'airflow-mock',
        'payload': {'pipeline_id': 'pipe-sales-daily', 'partition': '2026-06-07'}
    },
    'security_leaked_token': {
        'event_type': 'security.leaked_token',
        'source': 'secret-scanner-mock',
        'payload': {'alert_id': 'SEC-77', 'token_id': 'tok-prod-778', 'service_account_id': 'svc-checkout-deploy'}
    },
    'sla_escalation': {
        'event_type': 'support.sla_breach_risk',
        'source': 'sla-monitor',
        'payload': {'incident_id': 'INC-501', 'service_id': 'checkout-api', 'suggested_owner': 'payments-platform'}
    },
    'feature_flag_regression': {
        'event_type': 'release.feature_flag_regression',
        'source': 'release-monitor',
        'payload': {'service_id': 'checkout-api', 'flag_key': 'checkout_new_router', 'current_percentage': 30}
    },
}

def make_event(name: str) -> dict:
    base = EVENTS[name]
    return {
        'event_id': f'evt-{uuid.uuid4().hex[:8]}',
        'event_type': base['event_type'],
        'source': base['source'],
        'payload': base['payload'].copy(),
    }
