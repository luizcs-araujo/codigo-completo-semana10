# Teste de 503 em staging

## Escopo
Procedimento exclusivo para staging durante testes de carga.

## Mitigação de teste
Reinicie o worker de checkout, reduza a concorrência e repita o cenário. A execução pode ser feita pelo time de QA.

## Proibição
Este procedimento não é autorizado em produção. Não use restart como recomendação para tickets de `prod`.
