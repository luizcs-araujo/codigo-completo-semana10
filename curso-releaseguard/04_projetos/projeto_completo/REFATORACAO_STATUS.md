# Refatoração - status do núcleo técnico

## Concluído nesta etapa

- `00_base_clean`: FastAPI, domínio de e-commerce, estado, cenários reproduzíveis, UI HTML real e testes.
- `01_dia1`: schema canônico de TestPlan, geração live via Ollama structured output, executor HTTP real, política de allowlist, workflow n8n exportado com conexões e smoke test offline.
- `02_dia2`: Playwright/Chromium, captura de UI real, pixel diff, SSIM, bounding box, diff image e integração VLM via Ollama.
- `03_dia3`: métricas Prometheus reais expostas em `/metrics`, spans OpenTelemetry exportáveis via OTLP, clientes HTTP de Prometheus/Jaeger e loop SRE por tool calling.
- `complete`: política determinística de release baseada em resultados funcionais, visuais e operacionais.
- `scripts/validate_course.py`: compileall + pytest + smoke tests por versão.

## Validação executada neste runtime

- 00_base_clean: 7 passed + smoke PASS
- 01_dia1: 10 passed + smoke PASS
- 02_dia2: 11 passed + smoke PASS
- 03_dia3: 13 passed + smoke PASS
- complete: 16 passed + smoke PASS

O smoke do Dia 2 renderizou HTML servido pelo FastAPI em Chromium e mediu a regressão visual:
- pixel_change_ratio ~ 0.0115
- SSIM ~ 0.987
- bounding box localizada

O smoke do Dia 3 mediu latência real do cenário `payment_latency` (~0.25s) e confirmou sua presença em `/metrics`.

## Gates live não executados neste runtime

Este ambiente não possui Docker nem Ollama ativos. Portanto não foram declarados como validados:

- import/execução real do workflow n8n;
- scrape do Prometheus em container;
- ingestão/consulta real do Jaeger em container;
- geração live do TestPlan pelo Ollama;
- triagem VLM live;
- investigação SRE live com tool calling no Ollama.

Os arquivos e integrações foram preparados para esses gates, mas eles devem permanecer explicitamente pendentes até execução em ambiente com esses serviços.

## Próxima etapa do plano

Após validar os gates live em um ambiente com Docker/Ollama, congelar o núcleo técnico e reconstruir os materiais derivados: setup, guias de live coding, exercícios mentorados, guia n8n, guia teórico slide a slide e deck.
