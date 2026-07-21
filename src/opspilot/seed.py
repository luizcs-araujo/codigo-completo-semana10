from __future__ import annotations
from .database import connect, init_db
from .config import get_settings

DATA = {
    'tickets': [
        ('TCK-5001','Erro 500 após rollout do checkout_new_router','checkout-api','u-ana','high','open','Picos de HTTP 500 começaram após rollout de 30% da feature flag checkout_new_router.','2026-06-08T13:20:00Z'),
        ('TCK-4031','Usuário sales_manager recebeu 403 no dashboard','analytics-api','u-maria','medium','open','Role alterada ontem; permissões parecem corretas, mas cache pode estar inconsistente.','2026-06-08T14:15:00Z'),
        ('TCK-BILL9','Cliente cobrado duas vezes no plano Pro','billing-api','u-bruno','high','open','Duas cobranças idênticas em menos de 30 segundos; cliente solicita estorno.','2026-06-08T15:05:00Z'),
        ('TCK-DATA7','Pipeline de vendas travado na partição 2026-06-07','data-ingestion','u-taiane','high','open','Dashboard de BI não atualiza desde ontem por watermark travado.','2026-06-08T15:40:00Z'),
    ],
    'services': [
        ('checkout-api','Checkout API','production','degraded',0.19,2450,4,'DEP-991'),
        ('analytics-api','Analytics API','production','healthy',0.01,280,3,'DEP-880'),
        ('billing-api','Billing API','production','healthy',0.02,340,2,'DEP-700'),
        ('data-ingestion','Data Ingestion','production','degraded',0.08,1200,2,'DEP-810'),
        ('identity-api','Identity API','production','healthy',0.01,210,2,'DEP-650'),
    ],
    'users': [
        ('u-maria','Maria Silva','sales_manager','dashboard:read,analytics:read','stale'),
        ('u-ana','Ana Ribeiro','support_lead','tickets:write,incidents:write','fresh'),
        ('u-bruno','Bruno Lima','customer_success','billing:read,tickets:write','fresh'),
        ('u-taiane','Taiane Baldin','data_ops','data:read,data:write','fresh'),
    ],
    'feature_flags': [
        ('checkout_new_router','checkout-api',30,'payments-platform','2026-06-08T12:45:00Z'),
        ('analytics_role_cache_v2','analytics-api',100,'identity-platform','2026-05-31T10:00:00Z'),
    ],
    'deployments': [
        ('DEP-991','checkout-api','2026.06.08-rc4','succeeded','2026-06-08T12:30:00Z','a1b2c3d'),
        ('DEP-880','analytics-api','2026.06.05','succeeded','2026-06-05T09:00:00Z','bb8877a'),
        ('DEP-700','billing-api','2026.05.29','succeeded','2026-05-29T11:00:00Z','cc123aa'),
        ('DEP-810','data-ingestion','2026.06.01','succeeded','2026-06-01T01:00:00Z','dd901be'),
    ],
    'pipeline_runs': [
        ('RUN-1842','checkout-service','main','failed','integration-tests','test_payment_retry,test_router_timeout',1880),
        ('RUN-1777','identity-service','feature/roles','failed','security-tests','test_role_cache_invalidation',860),
        ('RUN-1888','mobile-api','main','success','', '',720),
    ],
    'billing_accounts': [
        ('acct-100','Cliente Solar',182900,49900,'open'),
        ('acct-101','Cliente Atlântico',42900,0,'none'),
    ],
    'data_pipelines': [
        ('pipe-sales-daily','sales_events','stuck','2026-06-07','2026-06-06T23:59:59Z','deadlock while writing partition'),
        ('pipe-usage-hourly','usage_events','healthy',None,'2026-06-08T14:00:00Z',None),
    ],
    'security_alerts': [
        ('SEC-77','leaked_token','github-secret-scan','critical','open','tok-prod-778','svc-checkout-deploy','Token de deploy apareceu em um commit público.'),
        ('SEC-88','excessive_permissions','service-account-audit','high','open',None,'svc-analytics-admin','Service account com permissão admin sem uso há 45 dias.'),
    ],
    'incidents': [
        ('INC-501','checkout-api','major','investigating','Erro 500 acima de 15% após rollout da flag checkout_new_router',None),
        ('INC-601','data-ingestion','minor','open','Watermark de vendas travado na partição 2026-06-07',None),
    ]
}


def reseed() -> None:
    init_db()
    with connect() as conn:
        for table in DATA:
            conn.execute(f'DELETE FROM {table}')
        for table, rows in DATA.items():
            placeholders = ','.join(['?'] * len(rows[0]))
            conn.executemany(f'INSERT INTO {table} VALUES ({placeholders})', rows)
        conn.execute('DELETE FROM audit_log')
        conn.execute('DELETE FROM events')
        conn.commit()

if __name__ == '__main__':
    reseed()
    print(f'Banco inicializado em {get_settings().db_path}')
