# Política de ações operacionais sensíveis

## Aprovação
Rollback, restart, alteração de configuração, mudança de role e invalidação de cache em produção exigem aprovação humana e registro da mudança.

## Princípio de menor privilégio
Agentes recebem tools de leitura por padrão. Tools de escrita devem ter escopo estreito, validação e idempotência.

## Evidência insuficiente
Quando não houver fonte atual, serviço e ambiente corretos ou trechos citáveis, o agente deve encerrar sem inventar procedimento.
