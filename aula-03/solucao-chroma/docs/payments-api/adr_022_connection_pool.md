# ADR-022 — Pool de conexões do checkout

## Decisão
O checkout usa pool adaptativo com máximo de 200 conexões por instância.

## Risco
Retry agressivo pode aumentar concorrência e saturar o pool, produzindo latência e 503 em cascata.

## Métricas
Observe `db_pool_in_use_percent`, `checkout_retry_rate`, latência p95 e taxa de 503.

## Mudanças
Alterações de pool exigem teste em staging e mudança aprovada.
