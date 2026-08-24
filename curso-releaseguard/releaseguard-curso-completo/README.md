# ReleaseGuard — código completo das aulas

Projeto final da semana de QA com IA, regressão visual e SRE agentic. Este
repositório reúne apenas o código executável e os artefatos de exemplo usados
nas três aulas.

## O que está incluído

- aplicação FastAPI e loja de demonstração;
- cenários de falha controlados;
- geração e execução de testes funcionais com Ollama;
- workflow do n8n;
- regressão visual com Playwright, pixel diff, SSIM e triagem por VLM;
- métricas Prometheus e traces OpenTelemetry no Jaeger;
- agente SRE com tools somente leitura e HITL;
- policy integrada de release: `PASS`, `REVIEW` ou `BLOCK`;
- testes, smokes e artefatos de referência dos três dias.

## Pré-requisitos

- Python 3.12;
- Docker com Docker Compose;
- Ollama;
- modelos `qwen3:8b` e `qwen3-vl:8b`.

Baixe os modelos:

```bash
ollama pull qwen3:8b
ollama pull qwen3-vl:8b
```

## Instalação

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

O arquivo `.env` é local e não é versionado.

## Subir o ambiente

Em um terminal, inicie n8n, Prometheus e Jaeger:

```bash
docker compose -f infra/docker-compose.yml up -d
```

Em outro terminal, inicie a API com exportação de traces:

```bash
source .venv/bin/activate
set -a
source .env
set +a
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Interfaces:

- loja: http://localhost:8000/store
- OpenAPI: http://localhost:8000/docs
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090
- Jaeger: http://localhost:16686

## Validar a instalação

```bash
source .venv/bin/activate
pytest -q
python -m scripts.smoke_base
python -m scripts.smoke_dia1
python -m scripts.smoke_dia2
python -m scripts.smoke_dia3
python -m scripts.smoke_complete
```

## Aula 1 — QA funcional com IA

```bash
python -m qa.run_demo
python -m qa.generate_plan
```

O workflow importável está em `n8n/qa_test_generator.json`. Depois da
importação, configure no n8n a credencial local do Ollama.

## Aula 2 — regressão visual

Com a API em execução:

```bash
python -m visual.guided_demo
```

Baseline, captura atual, diff e métricas são gravados em `artifacts/visual/`.

## Aula 3 — observabilidade e SRE agentic

A API expõe `/metrics` e envia spans por OTLP quando
`OTEL_EXPORTER_OTLP_ENDPOINT` está definido. Prometheus e Jaeger são iniciados
pelo Docker Compose acima.

O relatório integrado usa as evidências dos três dias:

```bash
python -m complete_report
```

Os resultados são gravados em `artifacts/release/`.

## Encerrar a infraestrutura

```bash
docker compose -f infra/docker-compose.yml down
```

Esse comando preserva os volumes locais do n8n e do Prometheus.
