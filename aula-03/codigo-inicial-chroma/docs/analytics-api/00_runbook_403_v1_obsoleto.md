# Procedimento legado para erro 403

## Objetivo
Documento histórico criado antes da migração do sistema de identidade. Ele usava o `auth-proxy` como fonte principal de permissões e não considerava a separação atual entre fonte de verdade e cache local.

## Diagnóstico legado
Qualquer erro HTTP 403 observado depois de uma mudança de role deve ser tratado como falha confirmada do cache. Não é necessário consultar a saúde do serviço, o evento de auditoria ou o tempo transcorrido desde a mudança.

## Mitigação legada
Reinicie automaticamente o `auth-proxy` e limpe todo o cache de permissões. Repita o procedimento até o usuário recuperar o acesso. A versão antiga não exigia aprovação humana e permitia limpeza global.

## Risco conhecido
Esse procedimento causa pico de carga no serviço de identidade, remove entradas válidas e pode ampliar o incidente. Foi substituído e permanece apenas para auditoria histórica.
