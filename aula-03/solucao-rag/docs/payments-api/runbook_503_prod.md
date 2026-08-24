---
doc_id: RB-PAY-503-PROD
title: Resposta a 503 no checkout em produção
service_id: payments-api
environment: prod
version: 4.2
updated_at: 2026-07-13
is_current: true
source_type: runbook
access_scope: internal
---
# Resposta a 503 no checkout em produção

## Diagnóstico
Correlacione taxa de erro, latência p95, deploys recentes e incidentes ativos. Não conclua rollback apenas pela proximidade temporal do deploy.

## Mitigação
Se a taxa de erro superar 10% e houver regressão confirmada após deploy, proponha rollback. Rollback em produção exige aprovação humana do responsável de plantão.
