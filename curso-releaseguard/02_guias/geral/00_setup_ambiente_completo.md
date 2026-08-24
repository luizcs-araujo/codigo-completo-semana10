# ReleaseGuard AI — Setup completo do ambiente

> **Núcleo congelado:** `releaseguard_course_validated_2026-08-17.zip`  
> **Fonte de verdade:** `releaseguard_validation_report.md`  
> Este guia não altera o núcleo. Ele reproduz o ambiente que foi validado localmente em macOS arm64 com 24 GiB de RAM.

## Objetivo

Ao final deste setup você deve ter, simultaneamente:

- FastAPI/ReleaseGuard em `http://localhost:8000`;
- Ollama com `qwen3:8b` e `qwen3-vl:8b`;
- n8n em `http://localhost:5678` ou em uma porta alternativa configurada;
- Prometheus em `http://localhost:9090`;
- Jaeger em `http://localhost:16686`;
- Chromium instalado e gerenciado pelo Playwright;
- target `releaseguard` como **UP** no Prometheus;
- serviço `releaseguard` visível no Jaeger;
- todos os testes offline e smoke tests passando.

---

# 1. Pré-requisitos

## 1.1 Verificar sistema e hardware

Execute:

```bash
uname -a
python3 --version
docker --version
docker compose version
ollama --version
```

Referência do ambiente já validado:

```text
macOS Darwin arm64
24 GiB RAM
Python 3.12.13
Docker 29.3.1
Docker Compose v5.1.1
Ollama 0.31.1
Playwright 1.62.0
```

As versões não precisam ser idênticas, mas o projeto foi validado com **Python 3.12**.

### Checkpoint

- [ ] Python 3.12 disponível.
- [ ] Docker Engine/Desktop disponível.
- [ ] `docker compose` funciona.
- [ ] Ollama responde no terminal.

Se qualquer item falhar, corrija antes de prosseguir.

---

# 2. Descompactar e identificar o núcleo

Descompacte:

```bash
unzip releaseguard_course_validated_2026-08-17.zip
cd releaseguard_course
```

Confira:

```bash
ls
```

Você deve encontrar:

```text
00_base_clean/
01_dia1/
02_dia2/
03_dia3/
complete/
infra/
scripts/
releaseguard_validation_report.md
```

A partir deste ponto, os exercícios serão executados principalmente em `complete/`. As versões incrementais existem para explicar a evolução pedagógica.

---

# 3. Criar o ambiente Python

Entre na versão completa:

```bash
cd complete
```

Crie um ambiente novo. Não reutilize um `.venv` copiado de outra máquina.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instale o browser do Playwright:

```bash
python -m playwright install chromium
```

Verifique o Chromium gerenciado:

```bash
python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
```

Guarde esse caminho. Ele será usado explicitamente no live coding do Dia 2.

> **Importante:** não assuma `/usr/bin/chromium`. Esse caminho foi uma das falhas encontradas no primeiro ciclo de validação em macOS.

### Checkpoint

```bash
python -c "import fastapi,httpx,pydantic,playwright,skimage,prometheus_client,opentelemetry; print('IMPORTS OK')"
```

Esperado:

```text
IMPORTS OK
```

- [ ] Dependências instaladas.
- [ ] Chromium gerenciado encontrado.

---

# 4. Configurar Ollama

Ainda em `complete/`, crie o `.env`:

```bash
cp .env.example .env
```

Conteúdo esperado:

```env
OLLAMA_TEXT_MODEL=qwen3:8b
OLLAMA_VISION_MODEL=qwen3-vl:8b
OLLAMA_NUM_CTX=32768
OLLAMA_BASE_URL=http://localhost:11434
```

Baixe os modelos:

```bash
ollama pull qwen3:8b
ollama pull qwen3-vl:8b
ollama list
```

Valide a API:

```bash
curl http://localhost:11434/api/tags
```

### Checkpoint

- [ ] `qwen3:8b` aparece no `ollama list`.
- [ ] `qwen3-vl:8b` aparece no `ollama list`.
- [ ] `curl /api/tags` retorna JSON.

---

# 5. Subir n8n, Prometheus e Jaeger

Volte para a raiz do curso:

```bash
cd ..
```

## 5.1 Portas padrão

O `infra/docker-compose.yml` usa:

| Serviço | Porta padrão |
|---|---:|
| n8n | 5678 |
| Prometheus | 9090 |
| Jaeger UI | 16686 |
| Jaeger OTLP gRPC | 4317 |
| Jaeger OTLP HTTP | 4318 |

Antes de subir:

```bash
lsof -i :5678 || true
lsof -i :9090 || true
lsof -i :16686 || true
lsof -i :4317 || true
lsof -i :4318 || true
```

## 5.2 Se as portas estiverem livres

```bash
docker compose -f infra/docker-compose.yml up -d
```

## 5.3 Se houver conflito

O núcleo validado permite overrides por variável de ambiente. Exemplo usado durante a validação:

```bash
N8N_PORT=5679 \
JAEGER_UI_PORT=16687 \
JAEGER_OTLP_HTTP_PORT=4319 \
JAEGER_OTLP_GRPC_PORT=4320 \
docker compose -f infra/docker-compose.yml up -d
```

Prometheus permaneceu em `9090` durante a validação.

> Se você alterar a porta OTLP HTTP, ajuste também `OTEL_EXPORTER_OTLP_ENDPOINT` ao iniciar o FastAPI.

Confira:

```bash
docker compose -f infra/docker-compose.yml ps
```

### Checkpoints HTTP

Com portas padrão:

```bash
curl -I http://localhost:5678
curl http://localhost:9090/-/healthy
curl -I http://localhost:16686
```

- [ ] n8n responde.
- [ ] Prometheus responde.
- [ ] Jaeger responde.

---

# 6. Verificar Prometheus antes de iniciar a aplicação

O arquivo `infra/prometheus/prometheus.yml` já possui o target validado:

```yaml
- job_name: releaseguard
  metrics_path: /metrics
  static_configs:
    - targets: ['host.docker.internal:8000']
```

Não remova `host.docker.internal`. O compose contém:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Isso permite ao Prometheus no container acessar a aplicação no host.

Antes de o FastAPI subir, o target pode aparecer DOWN. Isso é esperado.

---

# 7. Iniciar ReleaseGuard com tracing

Entre em `complete/`:

```bash
cd complete
source .venv/bin/activate
```

Com Jaeger nas portas padrão:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TEXT_MODEL=qwen3:8b
export OLLAMA_VISION_MODEL=qwen3-vl:8b
export OLLAMA_NUM_CTX=32768
```

Se você usou `JAEGER_OTLP_HTTP_PORT=4319`:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4319
```

Inicie:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Mantenha este terminal aberto.

Em outro terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/products
curl -I http://localhost:8000/store
curl -I http://localhost:8000/store/checkout
curl http://localhost:8000/metrics | head
```

Esperado em `/health`:

```json
{"status":"ok","scenario":"normal"}
```

Abra no navegador:

```text
http://localhost:8000/store
http://localhost:8000/store/checkout
http://localhost:8000/docs
```

### Checkpoint

- [ ] API responde.
- [ ] Loja renderiza.
- [ ] Checkout renderiza.
- [ ] Swagger/OpenAPI abre.
- [ ] `/metrics` retorna métricas Prometheus.

---

# 8. Confirmar Prometheus

Abra:

```text
http://localhost:9090/targets
```

Procure:

```text
releaseguard
```

Status esperado:

```text
UP
```

Teste pela API:

```bash
curl --get \
  --data-urlencode 'query=releaseguard_http_requests_total' \
  http://localhost:9090/api/v1/query
```

### Checkpoint

- [ ] Target `releaseguard` UP.
- [ ] PromQL retorna estrutura JSON válida.

---

# 9. Confirmar tracing no Jaeger

Primeiro gere algumas requisições:

```bash
curl -X POST http://localhost:8000/cart
curl http://localhost:8000/products
```

Abra:

```text
http://localhost:16686
```

Ou, se alterou a porta, use a porta correspondente.

No seletor de serviço, procure:

```text
releaseguard
```

O nome vem explicitamente de:

```python
Resource.create({'service.name':'releaseguard'})
```

### Checkpoint

- [ ] Serviço `releaseguard` aparece no Jaeger.

---

# 10. Rodar a validação offline

Na raiz do curso, com o venv ativo:

```bash
cd ..
python scripts/validate_course.py
```

Resultado já comprovado no ambiente de validação:

```text
00_base_clean → 7 tests
01_dia1       → 10 tests
02_dia2       → 11 tests
03_dia3       → 13 tests
complete      → 16 tests
TOTAL         → 57 tests
OFFLINE COURSE VALIDATION: PASS
```

### Checkpoint

- [ ] Compilação passa em todas as versões.
- [ ] 57 testes passam.
- [ ] Smoke tests passam.

---

# 11. Smoke do Dia 1

Entre novamente em `complete/`:

```bash
cd complete
python -m qa.run_demo
```

O fluxo real deve criar um carrinho e tentar adicionar quantidade inválida.

O artefato esperado:

```text
artifacts/day1/functional_report.json
```

Na validação oficial, a evidência foi:

```text
POST /cart → 200
POST /cart/cart-003/items → 409
passed: true
```

O ID do carrinho pode variar entre execuções.

---

# 12. Smoke Ollama do Dia 1

A API precisa continuar rodando.

```bash
python -m qa.generate_plan
```

Verifique no JSON:

- criação do carrinho;
- uso de `/cart/{cart_id}/items`;
- `sku-001`;
- quantidade maior que o estoque real (`stock=3`);
- status esperado `409`;
- oracle explicitamente ligado a estoque insuficiente.

---

# 13. Preparar o n8n

Abra a UI:

```text
http://localhost:5678
```

No n8n em Docker, o Ollama no host deve ser acessado por:

```text
http://host.docker.internal:11434
```

E o FastAPI por:

```text
http://host.docker.internal:8000
```

Importe:

```text
complete/n8n/qa_test_generator.json
```

Configure a credencial **Ollama account** no node `Ollama Chat Model`.

O guia `06_guia_n8n_passo_a_passo.md` detalha node por node.

---

# 14. Smoke do Dia 2

## 14.1 Descobrir Chromium

```bash
CHROMIUM=$(python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
)
echo "$CHROMIUM"
```

## 14.2 Rodar demonstração

```bash
python -m visual.guided_demo \
  --base-url http://127.0.0.1:8000 \
  --chromium "$CHROMIUM"
```

Artefatos:

```text
artifacts/visual/baseline.png
artifacts/visual/current.png
artifacts/visual/diff.png
artifacts/visual/metrics.json
```

Referência validada:

```text
pixel_change_ratio = 0.0114814453125
SSIM              = 0.9869284082954217
bbox              = [285, 237, 567, 297]
```

Pequenas diferenças numéricas são aceitáveis. A relação importante é:

```text
pixel_change_ratio > 0
SSIM < 1
bbox != null
```

---

# 15. Smoke Visual AI

```bash
python - <<'PY'
import json
from pathlib import Path
from visual.vlm_triage import triage

root = Path('artifacts/visual')
metrics = json.loads((root/'metrics.json').read_text())
result = triage(root/'baseline.png', root/'current.png', root/'diff.png', metrics)
print(result.model_dump_json(indent=2))
(root/'vlm_triage.json').write_text(result.model_dump_json(indent=2))
PY
```

Referência validada:

```text
change_type: button_shift
recommendation: review
```

A severidade pode variar se o modelo interpretar o impacto de maneira diferente. O resultado precisa permanecer fundamentado nas imagens e métricas.

---

# 16. Smoke do Dia 3

Antes do exercício:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

Execute o smoke determinístico:

```bash
python -m scripts.smoke_dia3
```

Esperado:

```text
SMOKE DIA3 PASS: real latency ...s recorded in /metrics
```

A validação oficial observou:

```text
normal payment:   0.002638 s
payment_latency:  0.257617 s
```

---

# 17. Checklist pré-aula

## Na véspera

- [ ] `python scripts/validate_course.py` passa.
- [ ] Modelos Ollama estão baixados.
- [ ] Docker images já estão disponíveis.
- [ ] Workflow n8n abre.
- [ ] Credencial Ollama do n8n está configurada.
- [ ] Chromium Playwright está instalado.

## 30 minutos antes

- [ ] Subir Docker Compose.
- [ ] Subir FastAPI com `OTEL_EXPORTER_OTLP_ENDPOINT`.
- [ ] Verificar `/health`.
- [ ] Verificar target Prometheus UP.
- [ ] Verificar serviço `releaseguard` no Jaeger.
- [ ] Verificar `ollama list`.

## 5 minutos antes

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

- [ ] Abrir terminal em `complete/`.
- [ ] Abrir `/docs`.
- [ ] Abrir n8n.
- [ ] Abrir Prometheus.
- [ ] Abrir Jaeger.
- [ ] Deixar caminho do Chromium copiado.

---

# 18. Troubleshooting baseado em falhas reais da validação

## Chromium: executable doesn't exist

Não use `/usr/bin/chromium` no macOS.

```bash
python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
```

Use esse path em `--chromium`.

## n8n não alcança Ollama

De dentro do container, `localhost` é o próprio container.

Use:

```text
http://host.docker.internal:11434
```

Documentação oficial: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/common-issues/

## n8n não alcança FastAPI

Use:

```text
http://host.docker.internal:8000
```

## Porta ocupada

Identifique:

```bash
lsof -i :5678
```

Use overrides do Compose em vez de matar serviços sem necessidade.

## Prometheus `releaseguard` DOWN

Verifique primeiro no host:

```bash
curl http://localhost:8000/metrics
```

Depois confirme `host.docker.internal:8000` no `prometheus.yml`.

## Jaeger não mostra `releaseguard`

Confirme que você exportou:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

Reinicie o FastAPI depois de definir a variável e gere novas requisições.

## Ollama retorna 400 com structured output

O núcleo congelado já corrige o regex do JSON Schema para:

```python
r'^/.*$'
```

Se aparecer novamente, confirme que você está executando o núcleo congelado e não uma versão anterior.

## Plano Ollama é válido no schema, mas semanticamente ruim

O código faz até três tentativas e usa `_semantic_issues()` para checar:

- path/method no OpenAPI;
- status documentado;
- body obrigatório;
- placeholders disponíveis.

Se falhar depois das tentativas, preserve o erro: ele demonstra exatamente a diferença entre validação estrutural e semântica.

---

# 19. Critério de ambiente pronto

Considere o ambiente pronto somente quando todos estiverem verdes:

- [ ] 57 testes + smoke tests.
- [ ] FastAPI/UI.
- [ ] Ollama text.
- [ ] Ollama vision.
- [ ] n8n.
- [ ] Prometheus target UP.
- [ ] Jaeger `releaseguard`.
- [ ] Playwright screenshot.
- [ ] Dia 1 report.
- [ ] Dia 2 metrics/diff.
- [ ] Dia 3 latency/metrics/traces.

