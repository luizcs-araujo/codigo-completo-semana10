# Checklist de deploy do payments-api

## Antes do deploy
Validar pool, timeout, retry, migrações e capacidade do adquirente.

## Após o deploy
Acompanhar 503, p95, pool e taxa de retry por 30 minutos.

## Rollback
Necessita aprovação e registro de mudança. Não faça rollback com base em um único log.
