# RELEASEGUARD AI

## Runbook de validação local do núcleo técnico

**Low-Code para QA e SRE com IA**

Objetivo: validar o núcleo refatorado antes de congelá-lo e regenerar guias, exercícios e slides.

## Regra de validação

Não corrija silenciosamente uma falha do pacote durante a validação. Marque FAIL, salve a evidência e registre qualquer ajuste manual separadamente. O objetivo é descobrir o que ainda precisa ser corrigido antes de congelar o núcleo.

# Como usar este documento

- [ ] Execute os gates na ordem. Um gate que falha pode invalidar os seguintes.

- [ ] Mantenha dois terminais: um para FastAPI/serviços e outro para comandos de validação.

- [ ] Salve screenshots ou outputs apenas nos checkpoints indicados.

- [ ] Use PASS somente quando o comportamento observado corresponder ao checkpoint descrito.

- [ ] Use SKIP somente quando uma dependência externa não estiver disponível e registre o motivo.

- [ ] No fim, preencha o relatório de validação usando os resultados coletados.

Diretório de referência: O pacote deve estar descompactado com a estrutura releaseguard_course/. Os comandos indicam quando executar na raiz ou em complete/.

## Dois pontos que devem ser testados sem correção silenciosa

- [ ] Prometheus: verificar se o ReleaseGuard aparece como target. A configuração entregue pode ainda não conter o scrape da aplicação.

- [ ] Jaeger: verificar o service.name. Se aparecer unknown_service ou equivalente, registrar como falha/limitação estrutural.

# Gate 0 - Preparar o ambiente

Objetivo: Garantir que Python, Docker, Ollama, Playwright e as dependências do projeto estejam disponíveis.

## 0.1 Entre na versão completa

```promql
cd releaseguard_course/complete
```

- [ ] O terminal está dentro de releaseguard_course/complete.

## 0.2 Crie e ative o ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

- [ ] A instalação termina sem erro.

## 0.3 Verifique as ferramentas

```bash
python --version
docker --version
docker compose version
ollama --version
```

Checkpoint: Todos os comandos devem responder com versão. Se Docker/Ollama não estiverem instalados, registre antes de continuar.

## 0.4 Configure o ambiente e os modelos

```bash
cp .env.example .env
ollama pull qwen3:8b
ollama pull qwen3-vl:8b
ollama list
```

- [ ] qwen3:8b aparece em ollama list.

- [ ] qwen3-vl:8b aparece em ollama list.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Python/venv | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Docker + Compose | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Ollama | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Playwright Chromium | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Modelos Ollama | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 1 - Validação offline completa

Objetivo: Comprovar que todas as versões compilam, passam nos testes e nos smoke tests antes de subir infraestrutura live.

## 1.1 Volte para a raiz do curso

```bash
cd ..
```

Confirme: Você deve estar em releaseguard_course/.

## 1.2 Execute o validador

```bash
python scripts/validate_course.py
```

Esperado: OFFLINE COURSE VALIDATION: PASS

Referência de testes: 00_base_clean: 7 passed | 01_dia1: 10 passed | 02_dia2: 11 passed | 03_dia3: 13 passed | complete: 16 passed.

Se falhar: Pare. Copie o primeiro erro relevante e marque o Gate 1 como FAIL. Não prossiga para infraestrutura live.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| compileall em todas as versões | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| pytest em todas as versões | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| smoke tests | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| resultado final do validator | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 2 - Subir a infraestrutura local

Objetivo: Disponibilizar n8n, Prometheus e Jaeger em containers.

```bash
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
```

Abra no navegador: n8n: http://localhost:5678 | Prometheus: http://localhost:9090 | Jaeger: http://localhost:16686

```bash
curl -I http://localhost:5678
curl http://localhost:9090/-/healthy
curl -I http://localhost:16686
```

| Check | Status | Evidência / observação |
| --- | --- | --- |
| n8n responde | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Prometheus saudável | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Jaeger responde | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| docker compose ps mostra serviços ativos | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 3 - Subir o ReleaseGuard

Objetivo: Executar a aplicação real com configuração de Ollama e exportação OTLP.

## 3.1 Em outro terminal, entre em complete/

```promql
cd releaseguard_course/complete
source .venv/bin/activate
```

## 3.2 Exporte as configurações live

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TEXT_MODEL=qwen3:8b
export OLLAMA_VISION_MODEL=qwen3-vl:8b
```

## 3.3 Suba a API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 3.4 Em outro terminal, faça os checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/products
curl http://localhost:8000/metrics
```

Abra no navegador: http://localhost:8000/store | http://localhost:8000/store/checkout | http://localhost:8000/docs

- [ ] A UI do e-commerce é real e navegável.

- [ ] /store/checkout retorna 200 e mostra a tela de checkout.

- [ ] /metrics retorna métricas em formato Prometheus.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| /health | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| /products | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| /metrics | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| /store | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| /store/checkout | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| /docs | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 4 - Dia 1 - executor determinístico

Objetivo: Comprovar que o teste funcional executa HTTP real e que o oracle determinístico julga o status retornado.

```promql
cd releaseguard_course/complete
source .venv/bin/activate
python -m qa.run_demo
```

O que observar: Uma requisição real contra a aplicação, status 409 para estoque insuficiente e assertion final marcada como sucesso porque o erro esperado ocorreu.

- [ ] O produto usado pelo teste existe nas fixtures reais.

- [ ] O status recebido é 409.

- [ ] O status esperado é 409.

- [ ] O report final marca o caso como PASS.

Evidência: Salve o output do terminal ou um screenshot curto contendo request/status/assertion.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| HTTP real | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| 409 real | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| assertion determinística | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| report PASS | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 5 - Dia 1 - geração live pelo Ollama

Objetivo: Comprovar que o modelo gera um TestPlan estruturado que o Pydantic aceita e que faz referência a endpoints reais.

```bash
python -m qa.generate_plan
```

- [ ] Ollama respondeu sem erro de conexão.

- [ ] O JSON retornado foi validado pelo Pydantic.

- [ ] Nenhum endpoint inexistente foi inventado.

- [ ] O oracle é plausivelmente derivado do requisito/contrato, não apenas uma expectativa arbitrária.

Importante: Schema válido não significa plano semanticamente bom. Registre planos malformados do ponto de vista de QA mesmo que o Pydantic aceite.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Ollama live | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| structured output | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Pydantic | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| endpoints reais | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| qualidade semântica do oracle | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 6 - Dia 1 - workflow n8n

Objetivo: Validar que o workflow entregue é importável, mantém conexões e executa o fluxo low-code contra Ollama + FastAPI.

- [ ] Abra http://localhost:5678.

- [ ] Importe complete/n8n/qa_test_generator.json.

- [ ] Configure a credencial do Ollama usando http://host.docker.internal:11434 quando o n8n estiver em Docker e o Ollama no host.

- [ ] Confirme que chamadas ao FastAPI usam http://host.docker.internal:8000 quando partem do container.

- [ ] Execute o workflow manualmente.

- [ ] Abra o output de cada node e valide a cadeia completa.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Workflow importou | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Connections preservadas | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Ollama Chat Model | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| FastAPI acessível | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Structured Output Parser | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Validation | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| HTTP execution | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Report | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

Evidência: Salve um screenshot do canvas executado e, idealmente, o output do node de structured output e do report final.

# Gate 7 - Dia 2 - regressão visual real

Objetivo: Comprovar que as imagens vêm da UI real via Playwright e que a diferença é medida por pixel ratio, SSIM e bounding box.

## 7.1 Descubra o Chromium instalado pelo Playwright

```python
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()"
```

## 7.2 Execute a demonstração

```bash
python -m visual.guided_demo --chromium "/CAMINHO/RETORNADO/PELO/COMANDO"
```

Arquivos esperados: artifacts/visual/baseline.png, current.png, diff.png e metrics.json.

- [ ] baseline.png veio da página real /store/checkout.

- [ ] current.png veio da mesma página após ativação do cenário visual.

- [ ] A regressão é visível manualmente.

- [ ] pixel_change_ratio > 0.

- [ ] SSIM < 1.

- [ ] bounding box não é nula.

Evidência: Abra baseline/current/diff lado a lado e salve um screenshot. Guarde também metrics.json.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Playwright real | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| baseline | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| current | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| diff | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| pixel ratio | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| SSIM | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| bounding box | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 8 - Dia 2 - Visual AI live

Objetivo: Comprovar que Qwen3-VL recebe baseline/current/diff e produz triagem estruturada baseada em evidência visual.

```python
python

import json
from pathlib import Path
from visual.vlm_triage import triage

root = Path("artifacts/visual")
metrics = json.loads((root / "metrics.json").read_text())

result = triage(
    root / "baseline.png",
    root / "current.png",
    root / "diff.png",
    metrics,
)

print(result.model_dump_json(indent=2))
(root / "vlm_triage.json").write_text(result.model_dump_json(indent=2))
```

- [ ] A chamada utilizou qwen3-vl:8b.

- [ ] O structured output foi validado.

- [ ] As evidências citadas existem nas imagens.

- [ ] Não houve alucinação visual relevante.

- [ ] A recomendação não trata similaridade visual como garantia de correção funcional.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Ollama vision | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| structured output | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| evidência visual | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| alucinação | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| recommendation | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 9 - Dia 3 - gerar uma falha operacional real

Objetivo: Produzir uma degradação mensurável no payment provider e comprovar que a aplicação exporta o sinal correspondente.

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
curl -X POST http://localhost:8000/lab/scenarios/payment_latency/activate
```

Ação: Faça várias chamadas de checkout/pagamento para produzir dados suficientes. Use a UI ou a API real.

```bash
curl http://localhost:8000/metrics
```

- [ ] A latência com o cenário é maior que a latência normal.

- [ ] releaseguard_dependency_duration_seconds aparece em /metrics.

- [ ] payment_provider aparece na métrica de dependência.

Importante: O valor observado deve vir da execução. Não compare com os números artificiais antigos de vários segundos.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| fault injection | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| latência real | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| métrica de dependência | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| payment_provider | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 10 - Prometheus

Objetivo: Comprovar que o Prometheus faz scrape do ReleaseGuard e retorna dados reais pela HTTP API.

- [ ] Abra http://localhost:9090/targets.

- [ ] Procure um target do ReleaseGuard.

Regra: Se o ReleaseGuard NÃO aparecer como target no pacote original, marque FAIL. Não edite o prometheus.yml antes de registrar a falha.

```promql
curl --get   --data-urlencode 'query=releaseguard_dependency_duration_seconds_count{dependency="payment_provider"}'   http://localhost:9090/api/v1/query
```

- [ ] A query retorna dados reais da execução.

Ajuste exploratório opcional: Depois de registrar FAIL do pacote original, você pode testar localmente um target host.docker.internal:8000 em Docker Desktop/macOS. Registre esse ajuste separadamente.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| container saudável | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| ReleaseGuard em /targets | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| target UP | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| PromQL retorna dados | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| ajuste manual necessário | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 11 - Jaeger

Objetivo: Comprovar que spans reais chegam ao backend e que a latência da dependência aparece no trace.

- [ ] Abra http://localhost:16686.

- [ ] Procure o serviço do ReleaseGuard.

Regra: Se o nome aparecer como unknown_service ou equivalente, registre FAIL/limitação. Não masque o problema renomeando apenas para passar o gate.

- [ ] Encontre um trace contendo checkout.create.

- [ ] Encontre payment.request.

- [ ] A duração do span payment.request cresce no cenário payment_latency.

```bash
curl "http://localhost:16686/api/services"
# Substitua NOME_DO_SERVICO pelo valor retornado:
curl "http://localhost:16686/api/traces?service=NOME_DO_SERVICO&limit=5"
```

Evidência: Tire screenshot de um trace mostrando checkout e payment, com duração observável.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| traces recebidos | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| service.name identificável | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| checkout.create | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| payment.request | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| latência no span | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 12 - APIs usadas pelo SRE Agent

Objetivo: Validar os wrappers/read-only data sources antes de envolver o LLM.

```promql
curl --get   --data-urlencode 'query=releaseguard_dependency_duration_seconds_count{dependency="payment_provider"}'   http://localhost:9090/api/v1/query

curl "http://localhost:16686/api/services"
```

- [ ] Prometheus retorna dados.

- [ ] Jaeger retorna lista de serviços.

- [ ] É possível consultar traces de um serviço real.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| Prometheus API | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Jaeger services API | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| Jaeger traces API | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 13 - SRE Agent live

Objetivo: Comprovar que o agente recebe apenas sintoma/contexto, escolhe tools e constrói uma conclusão baseada em evidências.

```python
python

from sre.agent import investigate
from sre.schemas import Incident

incident = Incident(
    service="checkout",
    symptom="latency above expected level",
    window_minutes=10,
)

result = investigate(incident)
print(result.model_dump_json(indent=2))
```

- [ ] O nome do cenário payment_latency NÃO foi fornecido ao agente.

- [ ] O agente realizou pelo menos uma tool call real.

- [ ] Prometheus e/ou Jaeger foram consultados conforme a hipótese.

- [ ] A conclusão cita evidência retornada pelas tools.

- [ ] Não houve salto injustificado de correlação para causa verificada.

- [ ] A mitigação é proposta, não executada automaticamente.

- [ ] requires_human está coerente com uma ação sensível.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| input sem scenario | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| tool calling | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| evidência real | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| causa sustentada | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| mitigação | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| HITL | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Gate 14 - Relatório integrado

Objetivo: Comprovar que a política final consome evidências reais dos três dias e varia PASS/REVIEW/BLOCK conforme o cenário.

Pré-requisito: Os artefatos funcionais, visuais e SRE devem existir antes desta etapa.

```bash
python -m complete_report
```

Arquivos esperados: artifacts/release/release_report.json e artifacts/release/release_report.md

- [ ] Cenário saudável produz PASS.

- [ ] Regressão visual crítica produz REVIEW ou BLOCK conforme a política.

- [ ] Incidente operacional ativo produz BLOCK.

- [ ] A decisão muda com as evidências e não é hardcoded.

| Check | Status | Evidência / observação |
| --- | --- | --- |
| healthy → PASS | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| visual regression → REVIEW/BLOCK | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| incident → BLOCK | ☐ PASS   ☐ FAIL   ☐ SKIP |  |
| decision evidence-driven | ☐ PASS   ☐ FAIL   ☐ SKIP |  |

# Checklist de congelamento do núcleo

- [ ] Gate 1 - Offline suite: PASS

- [ ] Gate 3 - FastAPI/UI real: PASS

- [ ] Gate 5 - Ollama text: PASS

- [ ] Gate 6 - n8n: PASS

- [ ] Gate 7 - Playwright/visual comparison: PASS

- [ ] Gate 8 - Ollama vision: PASS

- [ ] Gate 10 - Prometheus: PASS

- [ ] Gate 11 - Jaeger: PASS

- [ ] Gate 13 - SRE tool calling: PASS

- [ ] Gate 14 - Integrated release: PASS

Aprovação recomendada: Congele o núcleo somente quando os gates obrigatórios estiverem verdes ou quando qualquer exceção restante estiver explicitamente classificada como não bloqueadora.

# Template de relatório de validação local

Preencha este relatório depois da execução. Para falhas, inclua o erro essencial e o gate onde ocorreu. Não é necessário colar logs extensos.

## 1. Ambiente

Data da validação: ____________________________________________________________

Sistema operacional: ____________________________________________________________

Arquitetura: ____________________________________________________________

Python: ____________________________________________________________

Docker: ____________________________________________________________

Docker Compose: ____________________________________________________________

Ollama: ____________________________________________________________

Playwright: ____________________________________________________________

Navegador Playwright: ____________________________________________________________

RAM disponível: ____________________________________________________________

OLLAMA_TEXT_MODEL: ____________________________________________________________

OLLAMA_VISION_MODEL: ____________________________________________________________

OLLAMA_NUM_CTX: ____________________________________________________________

## 2. Validação offline

| Versão | compileall | pytest | smoke |
| --- | --- | --- | --- |
| 00_base_clean | PASS / FAIL | ____ passed / ____ failed / ____ skipped | PASS / FAIL |
| 01_dia1 | PASS / FAIL | ____ passed / ____ failed / ____ skipped | PASS / FAIL |
| 02_dia2 | PASS / FAIL | ____ passed / ____ failed / ____ skipped | PASS / FAIL |
| 03_dia3 | PASS / FAIL | ____ passed / ____ failed / ____ skipped | PASS / FAIL |
| complete | PASS / FAIL | ____ passed / ____ failed / ____ skipped | PASS / FAIL |

Observações: ____________________________________________________________

## 3. Infraestrutura

| Serviço | Status | URL | Observação |
| --- | --- | --- | --- |
| FastAPI | PASS / FAIL | localhost:8000 |  |
| n8n | PASS / FAIL | localhost:5678 |  |
| Prometheus | PASS / FAIL | localhost:9090 |  |
| Jaeger | PASS / FAIL | localhost:16686 |  |
| Ollama | PASS / FAIL | localhost:11434 |  |

## 4. Dia 1 - QA funcional + Ollama

qa.run_demo status: ____________________________________________________________

Status esperado: ____________________________________________________________

Status recebido: ____________________________________________________________

Assertion final: ____________________________________________________________

qa.generate_plan status: ____________________________________________________________

Modelo utilizado: ____________________________________________________________

Structured output válido?: ____________________________________________________________

Pydantic validou?: ____________________________________________________________

Endpoint inexistente inventado?: ____________________________________________________________

Oracle ancorado no requisito/contrato?: ____________________________________________________________

Problemas observados: ____________________________________________________________

## 5. n8n

Workflow importou?: ____________________________________________________________

Connections preservadas?: ____________________________________________________________

Ollama Chat Model conectou?: ____________________________________________________________

FastAPI acessível pelo container?: ____________________________________________________________

Structured Output Parser funcionou?: ____________________________________________________________

Plano executado por HTTP?: ____________________________________________________________

Report final gerado?: ____________________________________________________________

Problemas observados: ____________________________________________________________

## 6. Dia 2 - regressão visual

Página testada: ____________________________________________________________

Browser real utilizado?: ____________________________________________________________

Baseline gerada?: ____________________________________________________________

Current gerada?: ____________________________________________________________

diff.png gerado?: ____________________________________________________________

Pixel change ratio: ____________________________________________________________

SSIM: ____________________________________________________________

Bounding box: ____________________________________________________________

Mudança visual observável manualmente?: ____________________________________________________________

Observações: ____________________________________________________________

## 7. Visual AI

Modelo: ____________________________________________________________

Chamada multimodal live: ____________________________________________________________

Structured output: ____________________________________________________________

Change type: ____________________________________________________________

Severity: ____________________________________________________________

Affected region: ____________________________________________________________

Recommendation: ____________________________________________________________

Evidências correspondem às imagens?: ____________________________________________________________

Alucinação visual relevante?: ____________________________________________________________

Observações: ____________________________________________________________

## 8. Dia 3 - telemetria

Cenário ativado: ____________________________________________________________

Latência sem cenário: ____________________________________________________________

Latência com cenário: ____________________________________________________________

/metrics funcionando?: ____________________________________________________________

releaseguard_http_requests_total: ____________________________________________________________

releaseguard_http_request_duration_seconds: ____________________________________________________________

releaseguard_dependency_duration_seconds: ____________________________________________________________

payment_provider presente?: ____________________________________________________________

## 9. Prometheus

Container saudável: ____________________________________________________________

ReleaseGuard em /targets?: ____________________________________________________________

Target UP?: ____________________________________________________________

Query retornou dados reais?: ____________________________________________________________

Query utilizada: ____________________________________________________________

Ajuste manual necessário?: ____________________________________________________________

Qual ajuste?: ____________________________________________________________

## 10. Jaeger

Container saudável: ____________________________________________________________

Traces recebidos?: ____________________________________________________________

Nome do serviço exibido: ____________________________________________________________

checkout.create encontrado?: ____________________________________________________________

payment.request encontrado?: ____________________________________________________________

Latência visível no span?: ____________________________________________________________

Problemas: ____________________________________________________________

## 11. SRE Agent live

Incident enviado: ____________________________________________________________

Nome do cenário fornecido ao agente?: ____________________________________________________________

Modelo: ____________________________________________________________

Agent terminou?: ____________________________________________________________

Número de steps: ____________________________________________________________

Tool calls: ____________________________________________________________

Prometheus consultado?: ____________________________________________________________

Jaeger consultado?: ____________________________________________________________

Health consultado?: ____________________________________________________________

Recent changes consultado?: ____________________________________________________________

Probable cause: ____________________________________________________________

Confidence: ____________________________________________________________

Unsupported claims: ____________________________________________________________

Remediation options: ____________________________________________________________

Requires human: ____________________________________________________________

Causa sustentada pelas evidências?: ____________________________________________________________

Salto correlação→causalidade?: ____________________________________________________________

Tool call desnecessária?: ____________________________________________________________

Hallucination relevante?: ____________________________________________________________

Observações: ____________________________________________________________

## 12. Release report integrado

| Cenário | Decisão esperada | Decisão obtida | Resultado |
| --- | --- | --- | --- |
| saudável | PASS |  | PASS / FAIL |
| regressão visual crítica | REVIEW / BLOCK |  | PASS / FAIL |
| incidente operacional ativo | BLOCK |  | PASS / FAIL |

Decisão derivada das evidências?: ____________________________________________________________

Valor hardcoded determinando decisão?: ____________________________________________________________

## 13. Veredito

Offline suite: ____________________________________________________________

FastAPI: ____________________________________________________________

Ollama text: ____________________________________________________________

n8n: ____________________________________________________________

Playwright: ____________________________________________________________

Visual comparison: ____________________________________________________________

Ollama vision: ____________________________________________________________

Prometheus: ____________________________________________________________

Jaeger: ____________________________________________________________

SRE tool calling: ____________________________________________________________

Integrated release: ____________________________________________________________

- [ ] Núcleo aprovado para congelamento.

- [ ] Núcleo aprovado com correções pequenas.

- [ ] Núcleo requer nova refatoração antes dos materiais pedagógicos.

Bloqueador 1: ____________________________________________________________

Bloqueador 2: ____________________________________________________________

Bloqueador 3: ____________________________________________________________

Problema não bloqueador 1: ____________________________________________________________

Problema não bloqueador 2: ____________________________________________________________

Observações adicionais: ____________________________________________________________