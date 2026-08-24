# Arquitetura do reports-worker

## Componentes
API de solicitação, fila Redis, workers Celery, analytics-db e object storage.

## Concorrência
Cada worker processa um export por vez. Arquivos gigantes podem monopolizar capacidade.

## Isolamento
A arquitetura prevê fila dedicada para exports acima de 1 GB, mas a ativação depende de feature flag aprovada.

## Observabilidade
Monitore queue depth, oldest message age, active workers, duração e tamanho por export.
