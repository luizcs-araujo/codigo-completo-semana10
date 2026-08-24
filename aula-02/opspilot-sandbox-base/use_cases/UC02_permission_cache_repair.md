# UC02 — Correção controlada de 403 por cache de permissões

## Evento de entrada

`support.permission_403`

## Cenário

O agente recebe ticket de 403 após alteração de role e precisa decidir se existe evidência suficiente para invalidar cache ou sincronizar role.

## Por que isso vale um agente?

Reduzir o tempo de diagnóstico de permissões que normalmente dependeria de um dev olhar ticket, usuário, cache e serviço.

## Dados e ferramentas de leitura disponíveis

- `get_ticket`
- `get_user_permissions`
- `get_service_health`
- `list_open_incidents`

## Ferramentas perigosas envolvidas

- `invalidate_permission_cache`
- `sync_user_role`
- `escalate_incident`

Essas ferramentas não devem ser chamadas de forma ingênua. O trio precisa decidir quando fazer `dry_run`, quando bloquear, quando pedir aprovação e quando registrar limitação.

## Requisitos específicos

1. O agente deve receber o evento ou identificador principal do caso.
2. Deve consultar pelo menos duas fontes antes de propor ação perigosa, quando houver fontes suficientes.
3. Deve executar `dry_run=True` antes de qualquer escrita sensível ou destrutiva.
4. Deve produzir saída estruturada com evidências, ação proposta, riscos e necessidade de humano.
5. Deve usar `request_id` idempotente.
6. Deve registrar ou preservar auditoria da ação simulada ou executada.
7. Deve demonstrar bloqueio quando não houver aprovação para ação real.
8. Deve ter trace LangSmith ou configuração pronta para LangSmith.

## O que não pode fazer

- Não implementar RAG.
- Não acessar o banco diretamente a partir do agente.
- Não executar ação real sem aprovação explícita.
- Não tratar toda falha como automaticamente corrigível.
- Não esconder regra crítica apenas no prompt.

## Entrega do trio

- Código do agente.
- Comando para executar o cenário.
- Um run de dry-run.
- Um exemplo de bloqueio sem aprovação.
- Se fizer execução real: um exemplo com `approval_token` e consulta ao `audit_log`.
- Explicação de uma decisão de segurança.
- Limitação conhecida.

## Perguntas para a apresentação

- Qual evidência autorizou a ação proposta?
- Qual seria o impacto de uma ação errada?
- A idempotência foi garantida onde?
- O que aparece no trace e no audit log?
- Em que situação o agente deveria parar e pedir humano?
