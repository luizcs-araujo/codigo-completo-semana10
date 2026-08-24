# Runbook de backlog e atraso na fila

## Sintomas
Fila crescente, mensagens antigas e workers ativos sem aumento significativo de erros.

## Diagnóstico
Compare profundidade da fila, idade da mensagem mais antiga, número de workers e distribuição de tamanho dos exports. Verifique incidentes semelhantes.

## Mitigação
Priorize exports pequenos, isole arquivos gigantes em fila dedicada e avalie aumento temporário de workers. Mudança de escala em produção exige aprovação.

## Critério de severidade
Idade acima de 15 minutos com fila acima de mil mensagens é incidente de alta prioridade.
