# UC04 — Rollback parcial de feature flag após regressão

## Evento de entrada

`release.feature_flag_regression`

## Cenário

O agente correlaciona erro, deploy recente e flag de rollout para decidir se reduz percentual de uma feature flag.

## Por que isso vale um agente?

Automatizar uma ação que um humano faria abrindo dashboards, verificando deploys e ajustando flag manualmente.

## Dados e ferramentas de leitura disponíveis

- `get_service_health`
- `get_feature_flag`
- `get_recent_deploys`
- `list_open_incidents`

## Ferramentas perigosas envolvidas

- `set_feature_flag_rollout`
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
