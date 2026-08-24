# Post-mortem — saturação do pool após deploy

## Evento
A versão `2026.07.14-rc3` elevou retries em timeout e saturou o pool de conexões.

## Evidências
Taxa de erro de 18%, p95 acima de quatro segundos, pool em 98% e início dois minutos após deploy.

## Resolução
Rollback aprovado pelo on-call reduziu erros em sete minutos.

## Ação preventiva
Adicionar teste de carga com falha do adquirente e limite explícito de retry.
