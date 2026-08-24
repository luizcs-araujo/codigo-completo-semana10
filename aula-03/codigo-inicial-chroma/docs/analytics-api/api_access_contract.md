# Contrato da API de autorização do analytics-api

## Endpoint de verificação
`GET /internal/access/{user_id}/{resource}` retorna a decisão da fonte de verdade e a decisão em cache separadamente.

## Semântica do 403
HTTP 403 significa que a camada de autorização negou o recurso. Não comprova indisponibilidade, falha de banco ou problema de autenticação.

## Campos de auditoria
Toda decisão deve carregar `decision_id`, `source_role_version`, `cache_role_version` e `evaluated_at`.

## Limites
O endpoint é somente leitura. Invalidação utiliza endpoint administrativo separado, não exposto ao agente.
