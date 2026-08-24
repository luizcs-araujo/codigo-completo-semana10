# ReleaseGuard AI — Setup para agente de coding

> O agente deve operar sobre o núcleo congelado sem modificar seu código. O objetivo deste arquivo é preparar e validar o ambiente. **Falhou checkpoint obrigatório: pare e reporte.**

## Regra de execução

Para cada passo:

```text
AÇÃO → COMANDO → CHECKPOINT → PASS: continuar / FAIL: parar
```

## 1. Identificar sistema

**Ação:** registrar SO e arquitetura.

```bash
uname -a
```

**Checkpoint:** comando retorna sem erro.

## 2. Verificar Python 3.12

```bash
python3.12 --version
```

**Checkpoint:** major/minor = `3.12`.

## 3. Entrar no núcleo

```bash
cd releaseguard_course/complete
```

**Checkpoint:** `requirements.txt`, `app/`, `qa/`, `visual/`, `sre/` existem.

## 4. Criar venv novo

```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Checkpoint:** `python -c "import fastapi,httpx,pydantic"` retorna 0.

## 5. Instalar Chromium do Playwright

```bash
python -m playwright install chromium
python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
```

**Checkpoint:** path existente. Não exigir `/usr/bin/chromium`.

## 6. Verificar Ollama

```bash
ollama --version
ollama list
```

Se faltarem modelos:

```bash
ollama pull qwen3:8b
ollama pull qwen3-vl:8b
```

**Checkpoint:** ambos aparecem no `ollama list`.

## 7. Configurar env

```bash
cp -n .env.example .env || true
export OLLAMA_TEXT_MODEL=qwen3:8b
export OLLAMA_VISION_MODEL=qwen3-vl:8b
export OLLAMA_NUM_CTX=32768
export OLLAMA_BASE_URL=http://localhost:11434
```

**Checkpoint:** `curl http://localhost:11434/api/tags` retorna JSON.

## 8. Verificar Docker

```bash
docker --version
docker compose version
```

**Checkpoint:** ambos retornam 0.

## 9. Voltar à raiz e subir infraestrutura

```bash
cd ..
docker compose -f infra/docker-compose.yml up -d
```

Se houver conflito, usar portas alternativas, por exemplo:

```bash
N8N_PORT=5679 JAEGER_UI_PORT=16687 JAEGER_OTLP_HTTP_PORT=4319 JAEGER_OTLP_GRPC_PORT=4320 \
  docker compose -f infra/docker-compose.yml up -d
```

**Checkpoint:** `docker compose -f infra/docker-compose.yml ps` mostra n8n, Prometheus e Jaeger ativos.

## 10. Iniciar FastAPI

Em `complete/`:

```bash
cd complete
source .venv/bin/activate
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Se OTLP foi mapeado em outra porta, substituir `4318`.

**Checkpoint externo:** `curl http://localhost:8000/health` retorna status ok.

## 11. Validar UI

```bash
curl -I http://localhost:8000/store
curl -I http://localhost:8000/store/checkout
```

**Checkpoint:** HTTP 200.

## 12. Validar Prometheus

```bash
curl http://localhost:9090/-/healthy
curl --get --data-urlencode 'query=releaseguard_http_requests_total' http://localhost:9090/api/v1/query
```

**Checkpoint:** API responde. Depois verificar manualmente `/targets`: `releaseguard` deve estar UP.

## 13. Validar Jaeger

```bash
curl http://localhost:16686/api/services
```

Gere tráfego antes, se necessário.

**Checkpoint:** `releaseguard` está em `data`.

## 14. Rodar validação offline completa

Na raiz:

```bash
python scripts/validate_course.py
```

**Checkpoint obrigatório:** saída final `OFFLINE COURSE VALIDATION: PASS`.

Referência: 57 testes.

## 15. Validar Dia 1 determinístico

```bash
cd complete
python -m qa.run_demo
```

**Checkpoint:** `passed: true`, fluxo 200 → 409 e arquivo `artifacts/day1/functional_report.json`.

## 16. Validar geração Ollama

API precisa estar disponível:

```bash
python -m qa.generate_plan
```

**Checkpoint:** TestPlan JSON válido, executável, usando estoque real e 409.

## 17. Validar Dia 2

```bash
CHROMIUM=$(python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
)
python -m visual.guided_demo --base-url http://127.0.0.1:8000 --chromium "$CHROMIUM"
```

**Checkpoint:** baseline/current/diff/metrics existem; ratio > 0; SSIM < 1; bbox não nula.

## 18. Validar VLM

```bash
python - <<'PY'
import json
from pathlib import Path
from visual.vlm_triage import triage
r=Path('artifacts/visual')
m=json.loads((r/'metrics.json').read_text())
result=triage(r/'baseline.png',r/'current.png',r/'diff.png',m)
print(result.model_dump_json(indent=2))
PY
```

**Checkpoint:** JSON conforme `VisualTriage` e evidência visual fundamentada.

## 19. Validar Dia 3 determinístico

```bash
python -m scripts.smoke_dia3
```

**Checkpoint:** latência >= ~0.20 s e `payment_provider` em `/metrics`.

## 20. Validar clientes SRE

Prometheus:

```bash
curl --get --data-urlencode 'query=releaseguard_dependency_duration_seconds_sum{dependency="payment_provider"}' http://localhost:9090/api/v1/query
```

Jaeger:

```bash
curl http://localhost:16686/api/services
curl 'http://localhost:16686/api/traces?service=releaseguard&limit=5'
```

**Checkpoint:** evidência real em ambas as fontes.

## 21. Validar SRE Agent

```bash
python - <<'PY'
from sre.agent import investigate
from sre.schemas import Incident
result=investigate(Incident(service='checkout',symptom='latency above expected level',window_minutes=10))
print(result.model_dump_json(indent=2))
PY
```

**Checkpoint:** agente não recebe nome do cenário; usa métricas/traces; `requires_human=true`; conclusão usa linguagem de causa provável.

## 22. Validar report integrado

```bash
python -m complete_report
```

**Checkpoint:** `artifacts/release/release_report.json` e `.md` existem e decisão deriva dos artefatos.

## 23. Emitir relatório

Registrar para cada gate:

- PASS/FAIL;
- comando;
- evidência;
- qualquer alteração de porta;
- qualquer skip.

**Não declarar ambiente válido se um checkpoint obrigatório falhar.**
