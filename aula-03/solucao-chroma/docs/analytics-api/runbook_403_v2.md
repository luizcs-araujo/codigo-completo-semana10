# Diagnóstico de 403 após alteração de role

## Sintomas
O usuário recebe HTTP 403 no dashboard depois de uma alteração de role, embora a fonte de verdade indique que o recurso está autorizado. O problema costuma afetar um subconjunto de usuários, enquanto o serviço permanece saudável.

## Pré-condições
Confirme serviço e ambiente. Verifique a saúde do `analytics-api`, o recurso solicitado, as roles na fonte de verdade, as roles presentes no cache e o evento de mudança. Não trate uma mudança recente como causa suficiente por si só.

## Diagnóstico
A hipótese de cache obsoleto é sustentada quando: o serviço está saudável; a fonte de verdade autoriza o recurso; as roles em cache divergem; e a mudança ocorreu há mais de 15 minutos. Antes desse limite, o comportamento pode estar dentro do TTL esperado.

## Mitigação
Solicite invalidação direcionada do cache do usuário. A invalidação é uma ação de escrita e exige aprovação do on-call. Não reinicie o serviço e não limpe o cache global.

## Evidências obrigatórias
Registre ticket, usuário, recurso, comparação de roles, mudança de role, saúde do serviço, versão deste runbook e responsável pela aprovação.
