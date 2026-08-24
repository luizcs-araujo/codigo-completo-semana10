# Arquitetura técnica do OpsPilot Sandbox

O sistema simula um ecossistema operacional que já existe antes dos agentes.
A turma não deve construir o sistema do zero: deve integrar agentes a ele.

## Camadas

```text
Eventos externos / Webhooks
        ↓
FastAPI
        ↓
Repository / regras de negócio
        ↓
SQLite
        ↓
Audit log
```

Em paralelo, o projeto oferece uma camada de **tools LangChain** que chama a mesma lógica de negócio usada pela API.

```text
Agente LangChain
        ↓
Tools semânticas
        ↓
Repository
        ↓
SQLite + audit_log
```

## Por que existe API e tools?

Os trios podem escolher dois caminhos:

1. construir um agente que chama diretamente as tools Python;
2. construir um agente que chama endpoints HTTP.

Ambos são válidos. A diferença faz parte da decisão arquitetural.

## Fronteiras importantes

- O agente não deve acessar o banco diretamente.
- O agente não deve inventar dados de produção.
- Toda escrita sensível passa por capability com política.
- Ações reais usam `request_id` e podem exigir aprovação.
- Webhooks são entrada, não execução completa.
- RAG está fora do escopo desta aula.

## Entidades principais

- `tickets`: problemas reportados por usuários ou sistemas.
- `services`: estado operacional de APIs e workers.
- `feature_flags`: rollouts que podem ser alterados.
- `pipeline_runs`: CI/CD e testes falhos.
- `billing_accounts`: contas com cobrança duplicada.
- `data_pipelines`: ingestões e watermarks.
- `security_alerts`: alertas de token e service accounts.
- `incidents`: incidentes operacionais.
- `audit_log`: trilha de ações simuladas e executadas.
