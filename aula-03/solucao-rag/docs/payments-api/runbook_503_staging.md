---
doc_id: RB-PAY-503-STG
title: Teste de 503 em staging
service_id: payments-api
environment: staging
version: 2.0
updated_at: 2026-07-13
is_current: true
source_type: runbook
access_scope: internal
---
# Teste de 503 em staging

## Mitigação de teste
Em staging, reinicie o worker de checkout para validar o comportamento do pool. Este procedimento não é autorizado em produção.
