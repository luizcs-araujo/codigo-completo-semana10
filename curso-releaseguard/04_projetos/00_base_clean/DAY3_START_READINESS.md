# ReleaseGuard — prontidão para o exercício mentorado do Dia 3

Validação: 2026-08-20  
Estado: **PRONTO**

## O que já deve estar disponível aos grupos

- aplicação FastAPI e cenários controlados;
- `/metrics` com métricas HTTP e de dependência;
- spans `checkout.create` e `payment.request` exportados por OTLP;
- clientes Prometheus e Jaeger;
- tools SRE somente leitura;
- agente SRE com conclusão estruturada e compacta;
- schemas com `active_incident` e `requires_human`;
- release policy `PASS / REVIEW / BLOCK`;
- artefatos funcionais, visuais e SRE de referência.

Os alunos trabalham somente em:

```text
student_work/day3/<grupo>/
```

Não modificar durante o exercício:

```text
observability/
sre/agent.py
sre/tools/registry.py
release/policy.py
```

## Subida do ambiente

Infraestrutura:

```bash
cd ../../releaseguard_course
docker compose -f infra/docker-compose.yml up -d
```

API, a partir desta pasta:

```bash
source .venv/bin/activate
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TEXT_MODEL=qwen3:8b
export OLLAMA_NUM_CTX=32768
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Checkpoint antes de entregar o exercício

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl http://localhost:9090/-/healthy
curl http://localhost:16686/api/services
ollama list
```

Resultados esperados:

- cenário da aplicação: `normal`;
- Prometheus target `releaseguard`: `UP`;
- Jaeger lista o serviço `releaseguard` depois de gerar checkout/pagamento;
- Ollama contém `qwen3:8b`;
- nenhuma tool mutável está disponível ao agente.

## Cobertura dos grupos

| Grupo | Starter disponível |
| --- | --- |
| A — payment latency | histogram de `payment_provider` e span `payment.request` |
| B — payment timeout | HTTP 504, duração da dependência e trace com erro |
| C — inventory 500 | `/products` 500 com health geral ainda `ok` |
| D — inventory slow | duração HTTP observável e baseline normal |
| E — mudanças recentes | `get_recent_changes` read-only com resultado negativo |
| F — telemetria insuficiente | schema aceita limites/unsupported claims sem inventar causa |
| G — autonomia | tools somente leitura e `requires_human=true` |
| H — release gate | `release/policy.py`, `complete_report.py` e artefatos dos três dias |

## Validação executada

- `pytest`: 16 testes aprovados;
- smoke base: PASS;
- smoke Dia 1: PASS;
- smoke Dia 2 com Chromium real: PASS;
- smoke Dia 3: latência real acima de 0,20 s e métrica presente;
- smoke complete: PASS e BLOCK derivados de evidência;
- Prometheus: target `releaseguard=1` e série de `payment_provider` presente;
- Jaeger: `checkout.create` e `payment.request` presentes;
- agente SRE real: JSON válido, evidência compacta, unidades corretas e HITL;
- report integrado: `BLOCK` esperado por incidente ativo salvo.

Os cenários de falha acima foram usados apenas na validação. Depois dos testes, a
API e o Jaeger foram reiniciados e uma única compra saudável foi gerada para
estabelecer a linha de base da aula.

## Estado deixado para o início do exercício

- API em `http://localhost:8000`;
- n8n, Prometheus e Jaeger em execução;
- cenário da aplicação resetado para `normal`;
- target `releaseguard` em `UP`, sem série ativa de `payment_provider` deixada pelos testes;
- Jaeger com uma execução saudável (`payment.request` de 20 µs) para o serviço aparecer na interface;
- artefatos de referência preservados;
- cada grupo ainda precisa produzir sua própria investigação e evidência.
