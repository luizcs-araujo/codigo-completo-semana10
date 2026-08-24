---
doc_id: PM-AN-2026-06
title: Incidente de 403 após migração de roles
service_id: analytics-api
environment: prod
version: 1.0
updated_at: 2026-06-20
is_current: true
source_type: postmortem
access_scope: internal
---
# Incidente de 403 após migração de roles

## Resumo
Após uma migração de roles, usuários autorizados receberam 403 porque entradas antigas permaneceram no cache de permissões.

## Evidência observada
A API estava saudável, a fonte de verdade continha a role nova e o cache ainda continha a role anterior.

## Ação corretiva
O on-call aprovou invalidação direcionada. Foi proibida a limpeza global do cache por risco de aumento de carga.
