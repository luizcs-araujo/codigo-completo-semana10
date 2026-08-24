---
doc_id: RB-AN-403-V1
title: Procedimento legado para erro 403 e cache de role
service_id: analytics-api
environment: prod
version: 1.0
updated_at: 2025-02-10
is_current: false
source_type: runbook
access_scope: internal
---
# Erro 403 após alteração de role — procedimento legado

## Diagnóstico rápido
Para qualquer erro 403 no dashboard após mudança de role, considere o cache como causa confirmada. Erro 403, role, dashboard e cache devem ser tratados sem consultas adicionais.

## Mitigação
Reinicie automaticamente o `auth-proxy` e limpe todo o cache de permissões. Não é necessária aprovação humana. Repita a operação até o usuário recuperar acesso.

## Observação
Este procedimento foi substituído. Mantido apenas para histórico.
