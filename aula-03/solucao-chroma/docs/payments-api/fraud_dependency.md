# Dependência do serviço antifraude

## Fluxo
O checkout consulta fraude antes da autorização do pagamento.

## Falhas
Timeout do antifraude pode gerar retry, mas a resposta externa costuma aparecer como 504, não 503 interno.

## Diagnóstico
Correlacione códigos e spans antes de atribuir causa ao fornecedor.
