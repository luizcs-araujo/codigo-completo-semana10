# Dia 3 — Guia de implementação ao vivo

## Tema

**Assistente SRE orientado por evidências: métricas, traces, tool calling e HITL**

## Resultado após 40 minutos

```text
sistema saudável
→ payment_latency real
→ /metrics
→ Prometheus
→ Jaeger
→ Incident sem scenario
→ SRE Agent
→ tool calls read-only
→ probable cause
→ remediation proposal
→ requires_human
→ release policy
```

---

# Preparação

Prometheus e Jaeger devem estar ativos.

FastAPI deve ter sido iniciado com:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verifique:

```text
Prometheus /targets → releaseguard UP
Jaeger → service releaseguard
```

Reset:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

---

# 0–5 min — Produzir baseline operacional

## Problema

Antes de dizer que algo está lento, precisamos saber observar o comportamento normal.

## Arquivo

```text
app/api/routes.py
```

Mostre `payment()` e `_payment_impl()`.

No cenário normal não há `sleep`.

## Demonstração

Crie carrinho, adicione item, faça checkout e pague. Uma forma simples:

```bash
python - <<'PY'
import httpx,time
b='http://localhost:8000'
c=httpx.post(b+'/cart').json()
httpx.post(b+f"/cart/{c['id']}/items",json={'product_id':'sku-001','quantity':1})
o=httpx.post(b+'/checkout',json={'cart_id':c['id'],'address':'Rua Demo 123'}).json()
t=time.perf_counter()
r=httpx.post(b+'/payments',json={'order_id':o['id'],'amount':o['total']})
print('status=',r.status_code,'elapsed=',time.perf_counter()-t)
print(r.json())
PY
```

Referência validada:

```text
~0.002638 s
```

Não espere valor idêntico.

## Checkpoint

Pagamento saudável muito abaixo de 0.20 s.

## Gancho

> “Agora vamos introduzir o mesmo tipo de problema que um alerta de SRE perceberia: latência numa dependência.”

---

# 5–10 min — Injetar `payment_latency`

## Arquivo

```text
app/api/routes.py
```

## Código real

```python
if state.scenario=='payment_latency':
    with DEPENDENCY.labels('payment_provider').time():
        time.sleep(0.25)
```

## O que explicar

- A falha é controlada, mas o tempo medido é real.
- O histogram observa a dependência durante o `sleep`.
- O cenário não contém a conclusão da investigação.

## Comando

```bash
curl -X POST http://localhost:8000/lab/scenarios/payment_latency/activate
```

Repita um pagamento válido.

Referência validada:

```text
~0.257617 s
```

## Checkpoint

Elapsed >= 0.20 s.

## Gancho

> “Nós, humanos, sabemos que ativamos a falha. O agente não saberá. Precisamos fornecer sinais que permitam descobrir onde o tempo foi gasto.”

---

# 10–15 min — Mostrar métricas reais

## Arquivo

```text
observability/metrics.py
```

## Métricas definidas

```python
REQUESTS=Counter('releaseguard_http_requests_total','HTTP requests',['method','path','status'])
DURATION=Histogram('releaseguard_http_request_duration_seconds','HTTP duration',['method','path'])
DEPENDENCY=Histogram('releaseguard_dependency_duration_seconds','Dependency duration',['dependency'])
```

## Demonstração

```bash
curl http://localhost:8000/metrics | grep -A8 releaseguard_dependency_duration_seconds
```

Procure:

```text
dependency="payment_provider"
```

## O que explicar

Counter responde “quantos”. Histogram permite observar distribuição/sum/count de duração.

A métrica é exposição de estado observável, não diagnóstico.

## Checkpoint

`payment_provider` aparece.

## Gancho

> “A aplicação expõe a métrica, mas o agente não deveria parsear texto bruto de `/metrics`. Prometheus existe para armazenar e consultar séries.”

---

# 15–20 min — Prometheus como ferramenta consultável

## UI

Abra:

```text
http://localhost:9090/targets
```

Aponte:

```text
releaseguard → UP
```

Depois execute PromQL:

```promql
releaseguard_dependency_duration_seconds_sum{dependency="payment_provider"}
```

E:

```promql
releaseguard_dependency_duration_seconds_count{dependency="payment_provider"}
```

## Via API

```bash
curl --get \
  --data-urlencode 'query=releaseguard_dependency_duration_seconds_sum{dependency="payment_provider"}' \
  http://localhost:9090/api/v1/query
```

## O que explicar

- Prometheus scrapeia `/metrics` a cada 5 s no compose congelado.
- Labels tornam séries selecionáveis.
- Alta cardinalidade é custo/risco operacional: não use IDs arbitrários como labels por hábito.
- O agente usa a HTTP API, não a UI.

## Checkpoint

Query retorna valor real.

## Gancho

> “A métrica diz que a dependência ficou lenta. Mas ainda não mostra uma requisição específica nem o caminho de execução. Para isso usamos trace.”

---

# 20–25 min — OpenTelemetry e Jaeger

## Arquivo

```text
observability/tracing.py
```

## Código principal

```python
provider=TracerProvider(
    resource=Resource.create({'service.name':'releaseguard'})
)
```

E exporter condicional:

```python
endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
...
OTLPSpanExporter(endpoint=endpoint.rstrip('/')+'/v1/traces')
```

## Spans no domínio

Em `app/api/routes.py`:

```python
with tracer.start_as_current_span('checkout.create')
```

```python
with tracer.start_as_current_span('payment.request')
```

## Demonstração Jaeger

Abra:

```text
http://localhost:16686
```

Service:

```text
releaseguard
```

Procure trace contendo:

```text
payment.request
```

Referência validada:

```text
normal: 865 µs
latency: 253758 µs
```

## O que explicar

- Trace é trajetória individual.
- Span é unidade temporal dentro da trajetória.
- `service.name` é identidade de telemetria; numa validação anterior, sua ausência impedia consultas confiáveis.
- Um span lento é evidência forte de onde o tempo foi gasto, mas ainda precisa ser interpretado no contexto.

## Checkpoint

Span `payment.request` degradado visível.

## Gancho

> “Agora temos duas evidências independentes: série temporal e trace individual. É exatamente isso que vamos oferecer como tools ao agente.”

---

# 25–30 min — Mostrar tools read-only

## Arquivos

```text
sre/tools/clients.py
sre/tools/registry.py
```

## Tools

```text
query_metrics
list_trace_services
query_traces
get_service_health
get_recent_changes
```

## O que explicar

### Por que `list_trace_services` existe?

O incidente fala em serviço lógico `checkout`, mas o `service.name` real no Jaeger é `releaseguard`. Uma versão anterior do agente assumiu que ambos eram iguais e falhou.

### Por que read-only?

O agente está em fase de investigação. Consulta não equivale a remediação.

### Allowlist

`execute()` só aceita nomes registrados. Qualquer tool fora da allowlist gera erro.

## Demonstração sem LLM

```bash
python - <<'PY'
from sre.tools.clients import list_jaeger_services
print(list_jaeger_services())
PY
```

## Checkpoint

`releaseguard` aparece.

## Gancho

> “Agora podemos deixar o LLM decidir qual evidência pedir, mas continuamos controlando o conjunto de ações possíveis.”

---

# 30–35 min — Executar o SRE Agent sem passar scenario

## Arquivo

```text
sre/agent.py
```

## System importante

O system obriga:

- formar hipóteses;
- pedir evidência necessária;
- revisar hipóteses;
- diferenciar symptom/correlation/probable/verified cause;
- propor remediação sem executar;
- consultar métrica e traces antes de concluir latência.

## Incident

```python
Incident(
    service='checkout',
    symptom='latency above expected level',
    window_minutes=10,
)
```

Note que **não existe `scenario` no schema**.

## Comando

```bash
python - <<'PY'
from sre.agent import investigate
from sre.schemas import Incident
r=investigate(Incident(
    service='checkout',
    symptom='latency above expected level',
    window_minutes=10,
))
print(r.model_dump_json(indent=2))
PY
```

## O que observar

Na validação oficial, o resultado citou:

```text
payment_provider ≈ 0.2536 s
payment.request ≈ 253758 µs
```

E retornou:

```text
confidence = 0.85
active_incident = true
requires_human = true
```

## Checkpoint

A causa provável está sustentada pelas evidências e não afirma “verified root cause”.

## Caso não funcione

- Prometheus/Jaeger APIs;
- Ollama;
- service `releaseguard`;
- evidência de tráfego recente;
- máximo de tool steps é 6; o código força finalização com evidência acumulada se necessário.

## Gancho

> “O agente conseguiu chegar a uma causa provável. Agora precisamos discutir por que ele ainda não recebe permissão para reiniciar, rollbackar ou alterar infraestrutura.”

---

# 35–40 min — HITL e release policy

## Schema

```text
sre/schemas.py
```

Campo:

```python
requires_human: bool=True
```

## O que explicar

Remediation options são texto/proposta. Não existem mutating tools no registry do investigador.

Human-in-the-loop aqui é arquitetura de permissão, não uma frase no prompt.

## Release policy

Arquivo:

```text
release/policy.py
```

Regra principal:

```python
if sre and sre.get('active_incident',False):
    reasons.append('active SLO-impacting incident')
```

Com evidência salva, rode:

```bash
python -m complete_report
```

Referência atual:

```text
BLOCK
active SLO-impacting incident
```

## Fechamento

Desenhe:

```text
telemetria → evidência
LLM → investigação
policy → release
humano → mutação sensível
```

## Gancho para teoria

> “A demo funcionou porque construímos observabilidade antes do agente. Agora vamos formalizar RED, USE, SLI/SLO, traces, cardinalidade e a diferença entre causa provável e causa verificada.”

