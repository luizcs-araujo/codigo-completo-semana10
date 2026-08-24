# Post-mortem — fila saturada por exports gigantes

## Resumo
Cinco exports acima de 3 GB ocuparam todos os workers e aumentaram a espera dos demais clientes.

## Evidências
Workers ativos, poucos erros, queue depth crescente e mensagens com mais de 20 minutos.

## Resolução
A equipe aprovou fila dedicada e limite temporário de tamanho.

## Aprendizado
Saúde do processo não implica saúde da fila. Métricas de backlog são essenciais.
