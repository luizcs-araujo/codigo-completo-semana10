# Post-mortem — 403 após migração de roles

## Resumo
Após uma migração de roles, usuários autorizados receberam 403 porque entradas antigas permaneceram no cache além do TTL.

## Linha do tempo
A mudança de role foi registrada às 09:02. O primeiro 403 ocorreu às 09:21. A API permaneceu saudável e a divergência foi confirmada às 09:28.

## Causa raiz
Um consumidor de eventos perdeu mensagens durante rebalanceamento e não invalidou as entradas afetadas.

## Resolução
O on-call aprovou invalidação direcionada. A equipe proibiu a limpeza global e adicionou alerta para divergência persistente.

## Aprendizado
Runbooks devem exigir evidências independentes antes de recomendar ação de escrita.
