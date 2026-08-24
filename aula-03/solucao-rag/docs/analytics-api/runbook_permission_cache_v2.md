---
doc_id: RB-AN-403-V2
title: Diagnóstico de 403 após alteração de role
service_id: analytics-api
environment: prod
version: 2.1
updated_at: 2026-07-10
is_current: true
source_type: runbook
access_scope: internal
---
# Diagnóstico de 403 após alteração de role

## Sintomas
O usuário recebe HTTP 403 no dashboard depois de uma alteração de role, embora a fonte de verdade indique acesso válido.

## Pré-condições
Confirme o serviço e o ambiente. Verifique a saúde do `analytics-api`, a autorização na fonte de verdade e as roles presentes no cache de permissões.

## Diagnóstico
A hipótese de cache obsoleto é sustentada quando: o serviço está saudável; o recurso está autorizado na fonte de verdade; e as roles do cache divergem da fonte de verdade. Uma mudança recente de role reforça a hipótese, mas não é evidência suficiente isoladamente.

## Mitigação
Se a divergência persistir por mais de 15 minutos, solicite invalidação direcionada do cache do usuário. A invalidação é ação de escrita e exige aprovação humana do on-call. Não reinicie o serviço nem limpe o cache global.

## Evidências obrigatórias
Registre ticket, usuário, mudança de role, estado do serviço, comparação de roles e versão deste runbook.
