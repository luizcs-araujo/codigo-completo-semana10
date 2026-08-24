# ReleaseGuard AI — Guia geral dos três dias

## 1. Fonte técnica congelada

O núcleo desta semana é imutável:

```text
releaseguard_course_validated_2026-08-17.zip
```

A validação oficial está em:

```text
releaseguard_validation_report.md
```

Todos os comandos, exemplos, métricas, screenshots e outputs dos guias derivam desse núcleo.

---

# 2. Tese da semana

A semana não ensina que “IA substitui QA ou SRE”. Ela ensina a separar três responsabilidades:

```text
IA → propõe, seleciona, interpreta
software → valida, executa, mede
política/humano → decide risco e ação
```

Esse princípio reaparece nos três dias.

## Dia 1

```text
requisito
→ LLM propõe TestPlan
→ Pydantic e política validam
→ HTTP executa
→ status real decide assertion
```

**Mensagem:** low-code reduz trabalho de orquestração, não elimina test oracle nem invariantes.

## Dia 2

```text
browser real
→ baseline/current
→ pixel diff + SSIM + bbox
→ VLM interpreta evidência
→ política decide accept/review/block
```

**Mensagem:** diferença visual, similaridade perceptual e correção funcional são conceitos diferentes.

## Dia 3

```text
sintoma
→ agente formula necessidade de evidência
→ tools read-only consultam Prometheus/Jaeger
→ hipótese é revisada
→ causa provável + remediação
→ humano aprova ações sensíveis
```

**Mensagem:** um SRE Agent confiável não recebe a resposta junto com o incidente e não pode converter correlação em causalidade sem evidência.

---

# 3. Sistema central

O ReleaseGuard simula uma pequena plataforma de e-commerce.

Entidades reais do domínio:

- produtos;
- carrinhos;
- checkout;
- pagamentos;
- pedidos.

Fixtures principais:

| ID | Produto | Estoque |
|---|---|---:|
| `sku-001` | Notebook Pro | 3 |
| `sku-002` | Mouse Ergo | 12 |
| `sku-003` | Monitor 27 | 5 |

APIs importantes:

```text
GET  /products
GET  /products/{id}
POST /cart
GET  /cart/{id}
POST /cart/{id}/items
POST /checkout
POST /payments
GET  /orders/{id}
POST /lab/scenarios/{scenario}/activate
POST /lab/scenarios/reset
GET  /health
GET  /metrics
POST /qa/execute-plan
```

UI real:

```text
/store
/store/checkout
```

---

# 4. Fault injection

Cenários existentes no núcleo:

```text
normal
visual_checkout_shift
visual_missing_cta
dynamic_order_timestamp
payment_latency
payment_timeout
inventory_500
inventory_slow
coupon_regression
```

Eles alteram o comportamento real da aplicação. O nome do cenário não é enviado ao SRE Agent durante a investigação.

---

# 5. Stack

## Backend

- Python 3.12;
- FastAPI;
- Pydantic;
- Uvicorn;
- httpx;
- Jinja2.

## IA

- Ollama;
- `qwen3:8b` para structured output e tool calling;
- `qwen3-vl:8b` para triagem multimodal.

## Low-code

- n8n self-hosted.

## Visual QA

- Playwright;
- Pillow;
- NumPy;
- scikit-image/SSIM.

## Observabilidade

- OpenTelemetry SDK;
- Prometheus;
- Jaeger.

---

# 6. Evolução incremental

## `00_base_clean`

Domínio, API, UI, estado e fault scenarios.

## `01_dia1`

Acrescenta:

- `qa/schemas.py`;
- `qa/policy.py`;
- `qa/executor.py`;
- `qa/generate_plan.py`;
- workflow n8n.

## `02_dia2`

Acrescenta:

- Playwright;
- baseline/current/diff;
- SSIM;
- VLM triage.

## `03_dia3`

Acrescenta:

- métricas Prometheus;
- spans OpenTelemetry;
- clientes Prometheus/Jaeger;
- SRE Agent com tools.

## `complete`

Integra todos os artefatos em uma política de release.

---

# 7. Artefatos que o professor deve mostrar

## Dia 1

```text
complete/artifacts/day1/functional_report.json
```

Evidência validada:

```text
POST /cart → 200
POST /cart/{id}/items → 409
passed → true
```

## Dia 2

```text
complete/artifacts/visual/baseline.png
complete/artifacts/visual/current.png
complete/artifacts/visual/diff.png
complete/artifacts/visual/metrics.json
complete/artifacts/visual/vlm_triage.json
```

Valores da validação:

```text
pixel_change_ratio = 0.0114814453125
SSIM = 0.9869284082954217
bbox = [285, 237, 567, 297]
```

## Dia 3

```text
complete/artifacts/sre/investigation_result.json
complete/artifacts/release/release_report.json
complete/artifacts/release/release_report.md
```

Evidência de referência:

```text
payment dependency metric ≈ 0.2536 s
payment.request trace ≈ 253758 µs
requires_human = true
```

---

# 8. Cronograma sugerido

Cada aula tem 150 minutos.

## Dia 1

| Bloco | Tempo |
|---|---:|
| Contextualização | 5 min |
| Live coding | 40 min |
| Formalização e teoria | 55 min |
| Exercício mentorado | 40 min |
| Fechamento | 10 min |

## Dia 2

| Bloco | Tempo |
|---|---:|
| Contextualização | 5 min |
| Live coding | 40 min |
| SSIM, visual policies e VLM | 55 min |
| Exercício mentorado | 40 min |
| Fechamento | 10 min |

## Dia 3

| Bloco | Tempo |
|---|---:|
| Contextualização | 5 min |
| Live coding/investigação | 40 min |
| Observabilidade/SRE theory | 55 min |
| Exercício mentorado | 40 min |
| Fechamento | 10 min |

---

# 9. Ordem operacional de cada aula

## Antes de qualquer aula

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

## Dia 1

1. Mostrar produtos e estoque real.
2. Rodar plano determinístico.
3. Formalizar TestPlan/oracle/policy.
4. Gerar plano com Ollama.
5. Repetir a ideia no n8n.
6. Discutir limites e self-healing.
7. Exercício mentorado.

## Dia 2

1. Abrir checkout saudável.
2. Capturar baseline.
3. Injetar mudança.
4. Capturar current.
5. Gerar diff e métricas.
6. Explicar SSIM e bbox.
7. Chamar VLM.
8. Separar triagem de política.
9. Exercício mentorado.

## Dia 3

1. Gerar pagamento saudável.
2. Ativar `payment_latency`.
3. Mostrar impacto real.
4. Mostrar `/metrics`.
5. Abrir Prometheus.
6. Abrir Jaeger.
7. Executar agente apenas com sintoma.
8. Relacionar tool calls às evidências.
9. Mostrar HITL e release policy.
10. Exercício mentorado.

---

# 10. Ganchos entre dias

## Dia 1 → Dia 2

> “Hoje conseguimos transformar um requisito em um teste executável. Mas nosso oracle foi um status HTTP. Amanhã vamos testar algo cujo resultado não cabe facilmente em `assert status == 409`: a interface visual.”

## Dia 2 → Dia 3

> “Hoje conseguimos detectar e interpretar uma mudança visual, mas isso ainda é pré-release/QA. Em produção, o sintoma chega como latência, erro ou saturação. Amanhã o agente precisará descobrir onde está o problema usando telemetria.”

---

# 11. Troubleshooting geral

Consulte primeiro:

```text
00_setup_ambiente_completo.md
```

Princípio para aula:

1. se a infraestrutura externa falhar, não improvise alterando o núcleo;
2. use os artefatos já validados para explicar o resultado;
3. registre a falha e continue a teoria;
4. não invente métricas ou outputs para “salvar” a demonstração.

---

# 12. Checklist antes do Dia 1

- [ ] FastAPI funcionando.
- [ ] Ollama text funcionando.
- [ ] n8n funcionando.
- [ ] workflow importado.
- [ ] credencial Ollama válida.
- [ ] `/products` retorna `sku-001` com stock 3.
- [ ] `python -m qa.run_demo` passa.

# 13. Checklist antes do Dia 2

- [ ] Playwright Chromium instalado.
- [ ] caminho do Chromium conhecido.
- [ ] `/store/checkout` abre.
- [ ] qwen3-vl disponível.
- [ ] cenário visual resetado.
- [ ] artifacts/visual pode ser sobrescrito durante a demo.

# 14. Checklist antes do Dia 3

- [ ] Prometheus target `releaseguard` UP.
- [ ] Jaeger mostra `releaseguard`.
- [ ] OTLP endpoint configurado antes de iniciar FastAPI.
- [ ] `payment_latency` realmente produz > 0.20 s.
- [ ] qwen3:8b disponível.
- [ ] cenário resetado antes de começar.

