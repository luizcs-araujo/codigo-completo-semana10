# Resposta a 503 no checkout em produção

## Triagem
Correlacione taxa de erro, latência p95, saturação do pool, deploys recentes e incidentes ativos. Não conclua rollback apenas pela proximidade temporal.

## Critério de regressão
A hipótese de regressão após deploy é forte quando a taxa de erro supera 10%, o pool permanece acima de 95% e o início coincide com a nova versão.

## Mitigação
Proponha rollback quando houver regressão confirmada. Rollback em produção exige aprovação humana do responsável de plantão.

## Alternativas
Se não houver deploy recente, investigue adquirente, fraude e banco antes de agir.
