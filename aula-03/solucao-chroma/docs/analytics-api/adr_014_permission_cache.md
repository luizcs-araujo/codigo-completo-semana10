# ADR-014 — Cache de autorização

## Contexto
Consultas de autorização síncronas ao serviço de identidade adicionavam latência ao dashboard. Foi adotado um cache local por usuário e recurso.

## Decisão
A fonte de verdade permanece no identity-service. O cache do `analytics-api` possui TTL nominal de 15 minutos e nunca deve ser tratado como autoridade final.

## Consequências
Mudanças de role podem levar até 15 minutos para convergir. Divergências além desse período devem ser investigadas. A invalidação deve ser direcionada ao usuário e registrada; a limpeza global é proibida.

## Observabilidade
As métricas `permission_cache_hit_percent`, `permission_cache_stale_entries` e eventos de auditoria devem ser correlacionados com o ticket.
