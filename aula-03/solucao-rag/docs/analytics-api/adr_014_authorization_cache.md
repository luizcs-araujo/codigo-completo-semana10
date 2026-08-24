---
doc_id: ADR-014
title: Cache de autorização do analytics-api
service_id: analytics-api
environment: all
version: 3.0
updated_at: 2026-05-03
is_current: true
source_type: adr
access_scope: internal
---
# ADR-014 — Cache de autorização

## Decisão
A fonte de verdade de roles é o serviço de identidade. O `analytics-api` usa cache local para reduzir latência, com TTL nominal de 15 minutos.

## Consequências
Mudanças de role podem levar até 15 minutos para convergir. Divergências além desse período devem ser investigadas e a invalidação deve ser direcionada ao usuário, nunca global.
