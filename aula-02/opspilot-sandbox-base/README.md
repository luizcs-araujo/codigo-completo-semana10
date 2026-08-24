# OpsPilot Sandbox — Sistema base da Aula 2

Este projeto é o sistema preexistente que todos os trios usarão como base para construir agentes integrados.
Ele simula um ecossistema operacional com tickets, serviços, feature flags, CI/CD, billing, segurança, dados e auditoria.

O objetivo **não** é entregar agentes prontos. O objetivo é oferecer um backend realista, com tools perigosas, dados e eventos suficientes para que cada trio implemente um agente diferente.

## O que existe aqui

- API FastAPI com endpoints de leitura, escrita e webhooks.
- Banco SQLite local com dados mockados, porém persistentes.
- Tool registry com funções LangChain `@tool`.
- Políticas de risco por capability.
- Ações perigosas com `dry_run`, `approval_token`, `request_id` e auditoria.
- Idempotência para evitar execução duplicada.
- Eventos/webhooks para acionar agentes.
- Documentação técnica completa do sistema.
- 8 arquivos de use case para distribuir entre os trios.

> RAG foi excluído de propósito neste exercício. Os times devem focar integração, tools, governança, estado, autorização, auditoria, observabilidade e automação.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## Inicializar dados

```bash
python -m opspilot.seed
```

## Rodar API

```bash
uvicorn opspilot.api:app --reload --port 8088
```

Docs interativas:

```text
http://localhost:8088/docs
```

## Verificar ambiente

```bash
python -m opspilot.doctor
```

## Ver tools disponíveis

```bash
python -m opspilot.cli list-tools
```

## Simular webhook

```bash
python -m opspilot.cli emit-event monitoring_error_spike
python -m opspilot.cli emit-event security_leaked_token
```

## Rodar testes

```bash
pytest
```

## Modelo de segurança das tools

Ações perigosas aceitam sempre:

- `request_id`: chave de idempotência.
- `reason`: justificativa operacional.
- `dry_run`: quando `true`, simula sem alterar estado.
- `approval_token`: obrigatório para execução real de ações sensíveis.

Exemplo:

```python
set_feature_flag_rollout.invoke({
    "flag_key": "checkout_new_router",
    "percentage": 0,
    "request_id": "uc04-001",
    "reason": "erro 500 após rollout",
    "dry_run": True,
})
```

Execução real:

```python
set_feature_flag_rollout.invoke({
    "flag_key": "checkout_new_router",
    "percentage": 0,
    "request_id": "uc04-001",
    "reason": "erro 500 após rollout",
    "dry_run": False,
    "approval_token": "APPROVED-LOCAL-DEMO",
})
```

## Estrutura

```text
src/opspilot/
├── api.py             # FastAPI + endpoints/webhooks
├── cli.py             # comandos para professor/alunos
├── config.py          # configuração
├── database.py        # SQLite e schema
├── doctor.py          # diagnóstico
├── events.py          # payloads de eventos simulados
├── models.py          # modelos Pydantic
├── policies.py        # risco, aprovação, idempotência
├── repository.py      # lógica de negócio sobre o banco
├── seed.py            # dados iniciais
├── tools.py           # tools LangChain
└── tracing.py         # integração opcional com LangSmith
```

## Entrega esperada dos trios

Cada trio deve implementar um agente que:

1. Recebe um evento, ticket ou comando.
2. Consulta dados do sistema usando tools de leitura.
3. Avalia evidências.
4. Decide se pode simular ou executar uma ação perigosa.
5. Usa dry-run antes de qualquer escrita sensível.
6. Só executa ação real com aprovação.
7. Produz saída estruturada.
8. Registra ou preserva trilha de auditoria.
9. Gera trace no LangSmith quando configurado.
10. Explica quando não agiu por falta de evidência ou permissão.
