# Modelo de segurança das capabilities

Este sandbox foi desenhado para forçar discussões de autonomia.
Quase todo use case possui pelo menos uma ação perigosa.

## Classes de risco

| Risco | Significado | Exemplo |
|---|---|---|
| `read_only` | consulta sem alteração | `get_service_health` |
| `write_safe` | escrita reversível ou operacionalmente leve | `rerun_pipeline` |
| `write_sensitive` | muda estado importante | `set_feature_flag_rollout` |
| `destructive` | revoga, desabilita ou pode interromper acesso | `revoke_token` |

## Controles obrigatórios

Ações de escrita sensível/destrutivas exigem:

- `request_id` para idempotência;
- `reason` para auditoria;
- `dry_run=true` antes de executar;
- `approval_token` para ação real;
- registro no `audit_log`.

## Token de aprovação demo

```text
APPROVED-LOCAL-DEMO
```

O objetivo pedagógico é que os alunos pensem onde um humano entraria no fluxo.
Não use esse token como se fosse padrão de produção.

## Perguntas que todo time deve responder

- O agente precisa executar ação real ou apenas propor?
- Qual evidência mínima autoriza a escrita?
- Quem aprova a ação?
- O que acontece se o mesmo evento chegar duas vezes?
- Como evitar retry em operação não idempotente?
- O que fica registrado para auditoria?
