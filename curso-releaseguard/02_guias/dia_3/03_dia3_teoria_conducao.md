# Dia 3 — Guia teórico de condução

## Como usar este documento

Este é uma **cola técnica**, não um texto para leitura literal. A teoria deve entrar depois da demonstração prática, usando os dados que a turma acabou de ver:

```text
normal payment ≈ 0.0026 s
payment_latency ≈ 0.2576 s
Prometheus: payment_provider ≈ 0.2536 s
Jaeger: payment.request ≈ 253758 µs
SRE Agent: probable cause, confidence 0.85, requires_human=true
```

A narrativa central é:

```text
sintoma
→ sinal
→ hipótese
→ evidência necessária
→ consulta
→ revisão da hipótese
→ causa provável
→ proposta de mitigação
→ limite de autonomia
```

---

# Bloco 1 — Observabilidade: de “está lento” para “consigo explicar o estado interno”

## Onde estamos

A turma viu que o mesmo endpoint de pagamento saiu de alguns milissegundos para aproximadamente 250 ms após fault injection.

## Ideia central

**Monitoring** responde perguntas previamente conhecidas. **Observability** busca permitir inferir estados internos a partir de sinais externos, inclusive diante de falhas que você não predefiniu exatamente.

Não transforme isso numa disputa semântica rígida. O ponto útil é:

```text
monitoring → checks/dashboards/alerts conhecidos
observability → qualidade dos sinais para investigação aberta
```

## Como desenvolver

Comece pela pergunta:

> “Se eu só tivesse um alerta `checkout lento`, o que ainda não sei?”

Espere respostas:

- qual endpoint;
- qual dependência;
- quando começou;
- afeta todos ou alguns requests;
- houve erro;
- houve deploy.

Então diga: observabilidade não é uma ferramenta específica. É uma propriedade prática do sistema: **eu consigo obter evidência suficiente para reduzir incerteza sobre o estado interno?**

## Exemplo do ReleaseGuard

A aplicação expõe três tipos de evidência úteis:

- duração/requisições em métricas;
- `checkout.create` e `payment.request` como spans;
- health/config/change tools no agente.

## Nuance técnica

“Three pillars” (logs, metrics, traces) é uma heurística popular, não uma definição formal completa de observabilidade. Profiles, continuous profiling, events e domain telemetry também podem ser fundamentais.

## Erro conceitual comum

> “Se temos Grafana/Prometheus/Jaeger, temos observabilidade.”

Ferramenta não garante instrumentação boa. Métrica sem labels úteis, trace sem context propagation ou log sem correlation ID podem produzir pouco valor diagnóstico.

## Pergunta útil

> “Qual foi o menor conjunto de sinais que permitiu localizar a latência no ReleaseGuard?”

## Gancho

> “Para responder isso, precisamos separar o papel de cada sinal. Métrica, log e trace não são três maneiras redundantes de guardar a mesma coisa.”

## Ritmo

**Desacelerar moderadamente.** Essa definição orienta todo o restante.

## Se estiver atrasado

Corte a discussão histórica sobre observability e fique na diferença operacional monitoring vs investigação.

---

# Bloco 2 — Métricas, logs e traces: três formas diferentes de evidência

## Onde estamos

Temos um problema de latência e queremos decidir que evidência coletar primeiro.

## Ideia central

### Metrics

Agregam comportamento ao longo do tempo. Excelentes para detectar padrão, tendência e magnitude.

### Logs

Registram eventos discretos e detalhes ricos. Bons para erro/contexto local, mas podem ser volumosos e difíceis de correlacionar.

### Traces

Representam a trajetória de uma operação/requisição e a relação temporal entre spans.

## Como desenvolver

Use a frase:

> “A métrica diz que existe um incêndio; o trace ajuda a encontrar o cômodo; o log pode mostrar o que estava acontecendo ali.”

Depois retire a analogia e mostre o caso concreto:

- Prometheus: `payment_provider` ficou ~0.2536 s;
- Jaeger: uma operação `payment.request` durou 253758 µs;
- se houvesse exceção interna, um log poderia carregar stack trace/contexto.

## Nuance técnica

Métricas podem carregar exemplars para ligar um ponto de histogram a um trace. Logs podem incluir trace/span IDs. Os sinais ficam muito mais poderosos quando correlacionados.

## Erro conceitual comum

> “Trace substitui log.”

Não. Trace é estrutura causal/temporal da execução distribuída; log pode registrar payload/contexto não representado no span.

## Pergunta útil

> “Se o p95 de checkout aumentou, qual sinal vocês consultariam depois para descobrir onde o tempo está sendo gasto?”

## Gancho

> “Antes de falar em ferramenta, precisamos escolher um modo de organizar as métricas que realmente importam para serviços.”

---

# Bloco 3 — RED e USE

## Onde estamos

Queremos evitar dashboards de centenas de métricas sem uma estratégia de leitura.

## Ideia central

### RED — serviços orientados a requests

- **Rate**: volume de requisições;
- **Errors**: proporção/quantidade de falhas;
- **Duration**: latência/distribuição de duração.

### USE — recursos

- **Utilization**: quanto do recurso está sendo usado;
- **Saturation**: demanda esperando/capacidade excedida;
- **Errors**: falhas do recurso.

## Como desenvolver

Mostre que `releaseguard_http_requests_total` e `releaseguard_http_request_duration_seconds` são aproximações naturais ao RED.

Pergunte:

> “CPU a 90% significa necessariamente usuário sofrendo?”

Não. Esse é um bom contraste entre resource signal e service symptom.

## Exemplo

No incidente do Dia 3, o sintoma é duration. Se a hipótese fosse saturação de CPU, USE ganharia relevância.

## Nuance técnica

RED e USE não são SLOs. São heurísticas de instrumentação/diagnóstico.

## Erro comum

Misturar utilization e saturation. Um recurso pode estar com alta utilização e pouca fila; saturation é fila/espera/pressão além da capacidade.

## Gancho

> “RED ajuda a escolher métricas. Mas ainda precisamos transformar ‘latência boa’ ou ‘latência ruim’ em objetivo de confiabilidade. Entram SLI e SLO.”

## Se estiver atrasado

Explique RED profundamente e USE em 2 minutos, pois o laboratório é orientado a serviço e não a resource saturation.

---

# Bloco 4 — SLI, SLO e error budget

## Onde estamos

Temos latência medida. Agora precisamos discutir o que significa “latency above expected level”.

## Ideia central

### SLI

Indicador mensurado: por exemplo, proporção de requests de checkout abaixo de 300 ms.

### SLO

Objetivo para o SLI: por exemplo, 99.9% dos checkouts abaixo de 300 ms numa janela.

### Error budget

Quantidade tolerável de comportamento fora do objetivo antes de violar o SLO.

## Como desenvolver

Escreva:

```text
SLI = o que medimos
SLO = a meta
error budget = quanto podemos falhar sem violar a meta
```

Explique que o núcleo usa a expressão “SLO-impacting incident” na policy, mas **não implementa uma plataforma completa de SLO/error budget**. Esse é um conceito de produção que estamos conectando à decisão do ReleaseGuard.

## Nuance técnica

Um SLO não deve ser igual a 100% por padrão. Zero budget torna releases e manutenção impraticáveis e não reflete sistemas reais.

## Erro comum

Confundir SLA com SLO. SLA é compromisso contratual/externo; SLO é objetivo técnico/operacional.

## Pergunta

> “Um único pagamento de 250 ms viola um SLO?”

Resposta: não necessariamente. Depende do indicador, threshold e janela.

## Gancho

> “Para medir duration corretamente em escala, precisamos entender por que Prometheus usa histogramas e por que uma média simples pode esconder cauda.”

---

# Bloco 5 — Counters, gauges e histograms

## Onde estamos

A turma viu `Counter` e `Histogram` no código.

## Ideia central

### Counter

Cresce monotonamente; ideal para eventos acumulados como requests.

### Gauge

Pode subir/descer; ideal para valores instantâneos como fila/tamanho/temperatura.

### Histogram

Conta observações em buckets e expõe count/sum, permitindo estimar distribuição e quantis agregados no backend.

## Como desenvolver

Abra `observability/metrics.py` e aponte:

```python
REQUESTS=Counter(...)
DURATION=Histogram(...)
DEPENDENCY=Histogram(...)
```

Mostre que o SRE Agent usa `sum` e `count` para obter um sinal de duração média da dependência na evidência validada.

## Nuance técnica

Para SLO de latência, média é frequentemente inadequada. p95/p99 ajudam a entender cauda. Prometheus histogram quantiles dependem de buckets e agregação corretos.

## Erro comum

> “p99 é o request mais lento.”

Não. É o valor abaixo do qual aproximadamente 99% das observações caem, dependendo do método/estrutura usada.

## Pergunta

> “Por que dois sistemas com média de 100 ms podem ter experiências de usuário completamente diferentes?”

## Gancho

> “Quando adicionamos labels, a métrica ganha contexto. Mas labels também podem explodir custo e memória.”

---

# Bloco 6 — Labels e cardinalidade

## Ideia central

Cada combinação única de labels cria uma série temporal distinta.

Exemplo seguro no núcleo:

```text
dependency="payment_provider"
```

Exemplo perigoso em produção:

```text
user_id="..."
request_id="..."
```

## Como desenvolver

Explique cardinalidade como produto das combinações possíveis.

Se adicionarmos labels:

```text
method × path × status
```

ainda é controlável se paths forem templates estáveis. Se o path tiver IDs brutos, explode.

## Nuance

Observability pipelines precisam de governança de atributos/labels. Mais contexto não é sempre melhor.

## Gancho

> “Metrics são agregadas. Para ver uma requisição específica e seus componentes temporais, vamos entrar em tracing.”

---

# Bloco 7 — Trace e span

## Onde estamos

Já vimos o waterfall do `payment.request`.

## Ideia central

**Trace** representa uma operação ponta a ponta. **Span** representa uma unidade de trabalho temporal com início, duração, atributos e relação parental.

## Como desenvolver

Aponte no código:

```python
with tracer.start_as_current_span('checkout.create')
```

```python
with tracer.start_as_current_span('payment.request')
```

No Jaeger, mostre:

- operation name;
- duration;
- attributes `order.id`;
- service `releaseguard`.

## Nuance técnica

No núcleo didático há spans internos manuais. Em sistemas distribuídos, context propagation via headers (W3C Trace Context, por exemplo) permite ligar spans em serviços diferentes.

## Erro comum

> “Um trace longo prova qual função é culpada.”

Ele mostra onde o tempo foi observado, não necessariamente por que aquele componente ficou lento.

## Pergunta

> “Se `payment.request` leva 250 ms, o que ainda falta para provar que o provedor externo é a root cause?”

## Gancho

> “Essa cautela é central para o SRE Agent: ele precisa distinguir evidência de causalidade.”

---

# Bloco 8 — OpenTelemetry: instrumentação separada do backend

## Ideia central

OpenTelemetry fornece APIs/SDKs/convenções/exportação para telemetria sem obrigar um backend específico.

No núcleo:

```text
OpenTelemetry SDK → OTLP HTTP → Jaeger
```

Prometheus é alimentado separadamente pelo endpoint `/metrics` via `prometheus_client`.

## Como desenvolver

Mostre `configure_tracing()`.

Explique:

- `TracerProvider`;
- Resource;
- `service.name`;
- `BatchSpanProcessor`;
- `OTLPSpanExporter`.

## Nuance

OpenTelemetry não é “o Jaeger”. Jaeger é backend/UI de trace. OTel é o padrão/camada de instrumentação/exportação.

## Erro comum

Confundir collector, SDK e backend.

## Gancho

> “Agora vamos ver por que `service.name` aparentemente pequeno foi crítico para o agente.”

---

# Bloco 9 — Identidade de serviço e propagação de contexto

## Onde estamos

A validação inicial falhou porque o agente assumia que o nome lógico do incidente `checkout` era o mesmo que o `service.name` no Jaeger.

## Ideia central

Taxonomia/identidade de telemetria precisa ser confiável e descobrível.

O núcleo corrigiu:

```python
Resource.create({'service.name':'releaseguard'})
```

E adicionou tool:

```text
list_trace_services
```

## Como desenvolver

Esse é um ótimo exemplo de engenharia de agentes:

> não basta o LLM “ser inteligente”; o ambiente precisa oferecer nomes estáveis e ferramentas que permitam descobrir a realidade.

## Gancho

> “Com fontes consultáveis e identidade consistente, podemos finalmente falar de investigação orientada por hipótese.”

---

# Bloco 10 — Hypothesis-driven investigation

## Ideia central

O agente não deve executar queries aleatórias até achar algo interessante.

Ciclo:

```text
sintoma
→ hipótese inicial
→ qual evidência discriminaria hipóteses?
→ query/tool
→ observation
→ revisão
```

## Como desenvolver

Use o caso:

```text
Sintoma: checkout lento
```

Hipóteses possíveis:

- payment;
- inventory;
- saturação;
- deploy recente;
- problema geral de aplicação.

Pergunte:

> “Qual query reduz mais incerteza?”

Depois mostre a estratégia do system prompt: consultar dependency metric + listar serviços + traces antes de finalizar latência.

## Nuance técnica

O system prompt do núcleo contém heurística específica do laboratório. Em produção, você pode combinar playbooks, service topology e dynamic tool selection.

## Erro comum

Confundir “mais tool calls” com melhor investigação. Cada call custa tempo, contexto e potencial de ruído.

## Gancho

> “Isso leva a budgets: precisamos limitar investigação também.”

---

# Bloco 11 — Tool budgets e bounded autonomy

## Ideia central

O agente tem `max_steps=6`.

Além disso, clients têm timeout.

Esses limites protegem:

- custo;
- loop infinito;
- consultas excessivas;
- contexto explosivo.

## Como desenvolver

Abra:

```python
def investigate(..., max_steps:int=6,...)
```

E mostre que, ao atingir o máximo, `_finalize()` força conclusão a partir da evidência disponível.

## Nuance

Um budget baixo demais produz investigação prematura; alto demais aumenta custo e risco. Precisa ser calibrado por domínio.

## Gancho

> “Mesmo com muitas evidências, existe uma fronteira conceitual difícil: correlação não significa causalidade.”

---

# Bloco 12 — Correlação, causa provável e root cause verificada

## Onde desacelerar

**Este é um dos pontos mais importantes da aula.**

## Ideia central

No laboratório:

- métricas mostram payment_provider lento;
- trace mostra `payment.request` lento;
- checkout tem sintoma de latência.

Isso sustenta uma **causa provável/contribuinte**.

Mas não necessariamente prova a causa física subjacente do provider.

## Escada de linguagem

```text
sintoma
↓
correlação observada
↓
fator contribuinte
↓
causa provável
↓
causa verificada
```

Quanto mais forte a afirmação, maior a evidência exigida.

## Exemplo real do output

```text
probable_cause:
"A specific payment.request operation ... is experiencing high latency, which may be causing ..."
```

Repare em **may be causing**.

## Erro conceitual comum

“Encontramos o span mais lento, logo encontramos a root cause.”

## Pergunta

> “Que experimento adicional aumentaria nossa confiança?”

Possibilidades:

- reproduzir com provider alternativo;
- correlacionar provider telemetry;
- desabilitar componente e medir;
- verificar saturação/erro downstream.

## Gancho

> “Mesmo uma causa provável forte não autoriza automaticamente um rollback. Vamos separar investigação de remediação.”

---

# Bloco 13 — Read-only tools e princípio do menor privilégio

## Ideia central

O registry contém apenas ferramentas de leitura.

Não existe `restart`, `rollback`, `scale`, `delete` no agente investigativo.

## Como desenvolver

Mostre `TOOL_SPECS` e `execute()`.

Explique que tool use é parte da superfície de segurança: descriptions e schema ajudam seleção; allowlist e implementação controlam capacidade real.

## Nuance

Separar “investigator” e “remediator” pode ser arquiteturalmente superior a um único agente superprivilegiado.

## Gancho

> “Então como saímos da investigação para uma ação? A transição é explicitamente humana.”

---

# Bloco 14 — Human-in-the-loop

## Ideia central

`requires_human=true` não significa “IA fraca”. Significa que o risco da mutação exige mudança de autoridade.

## Como desenvolver

Separe:

```text
investigate → pode ser automático
propose → pode ser automático
approve → humano/policy
execute → tool privilegiada separada
```

No núcleo, só os dois primeiros existem no SRE Agent.

## Nuance

Em produção, HITL pode ser ticket, approval workflow, ChatOps, change management ou policy engine — não precisa ser um `input()` no terminal.

## Pergunta

> “Reiniciar um pod sempre exige humano?”

Resposta madura: depende da reversibilidade, blast radius, confiança e política.

## Gancho

> “Essa mesma lógica de política aparece no fim do projeto: release decision.”

---

# Bloco 15 — Release policy e integração dos três dias

## Onde estamos

Temos três classes de evidência:

- functional QA;
- visual QA;
- SRE/operational.

## Ideia central

O LLM não escolhe unilateralmente `PASS/BLOCK`.

`release/policy.py` faz decisão determinística.

Regras relevantes:

```text
functional fail → BLOCK
visual recommendation block → BLOCK
active incident → BLOCK
visual review → REVIEW
sem gates → PASS
```

## Como desenvolver

Mostre o report real:

```text
BLOCK
active SLO-impacting incident
```

Explique que a validação também executou policy checks independentes para:

```text
healthy → PASS
visual regression → REVIEW
active incident → BLOCK
```

## Nuance

Em produção, policies podem ser mais ricas: severity, ownership, waivers, time windows, error budget, compliance.

## Pergunta

> “Por que o Visual AI devolveu review, mas o report final deu block?”

Porque havia **outra evidência**, um incidente operacional ativo. A política agrega sinais independentes.

## Gancho final

> “Isso fecha a tese da semana: IA aumenta criação e interpretação de evidência; confiabilidade vem de contratos, telemetria e políticas.”

---

# Bloco 16 — O que cortar se estiver atrasado

Prioridade alta — não cortar:

1. observability vs monitoring;
2. metrics vs traces;
3. RED;
4. trace/span;
5. hypothesis-driven investigation;
6. probable vs verified cause;
7. HITL;
8. release policy.

Pode resumir:

- USE;
- error budget aprofundado;
- cardinalidade matemática;
- detalhes de OTLP exporter;
- p95/p99 avançado.

---

# Perguntas de checagem rápida

Use ao longo da aula:

1. “Qual evidência temos e qual ainda estamos inferindo?”
2. “Essa query testa qual hipótese?”
3. “Métrica agregada e trace individual respondem a mesma pergunta?”
4. “Esse label poderia explodir cardinalidade?”
5. “Temos causa provável ou verificada?”
6. “Qual seria o blast radius dessa remediação?”
7. “Quem deve ter a permissão de executar?”
8. “Por que o release gate não ficou dentro do LLM?”
