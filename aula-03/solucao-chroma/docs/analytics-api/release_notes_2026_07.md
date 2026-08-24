# Release notes do analytics-api — julho de 2026

## Versão 2026.07.12
Adicionada telemetria de autorização e correlação entre ticket e `decision_id`. Não houve mudança na política de roles ou no TTL do cache.

## Risco operacional
A versão não contém alteração conhecida capaz de produzir 403 por si só. Um 403 após role deve priorizar investigação de autorização e cache.

## Rollback
Rollback desta versão não corrige entradas antigas de cache e não deve ser a primeira mitigação.
