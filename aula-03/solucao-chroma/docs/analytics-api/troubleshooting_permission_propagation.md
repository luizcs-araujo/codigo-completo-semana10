# Guia de troubleshooting de propagação de permissões

## Perguntas iniciais
O recurso está autorizado na fonte de verdade? A role mudou recentemente? O ambiente é produção? O cache apresenta a role anterior? O serviço está saudável?

## Interpretação temporal
Até 15 minutos, aguarde a convergência quando não houver impacto crítico. Entre 15 e 30 minutos, confirme eventos de auditoria. Acima de 30 minutos, trate como divergência persistente.

## Evidência fraca
Relato de usuário, proximidade temporal e mensagens de chat não são suficientes isoladamente.

## Evidência forte
Comparação entre fonte de verdade e cache, evento de mudança e runbook vigente formam um conjunto adequado para escalonamento.
