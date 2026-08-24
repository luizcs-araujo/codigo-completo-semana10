# Dia 3 — Exercício mentorado

## Objetivo

Cada grupo deve investigar um incidente usando evidências observáveis, sem receber uma causa pronta e sem executar remediações destrutivas.

## Ponto inicial

```text
releaseguard_course/03_dia3
```

ou `complete/`.

## Não modificar

```text
observability/
sre/agent.py
sre/tools/registry.py
release/policy.py
```

Grupos podem criar scripts próprios em:

```text
student_work/day3/<grupo>/
```

---

# Regras

1. A apresentação não pode começar pela “causa”.
2. Precisa começar por um sintoma observável.
3. Toda afirmação causal precisa citar evidência.
4. Mutação é apenas proposta.
5. Se a evidência for insuficiente, isso é uma conclusão válida.

---

# Casos

## Grupo A — `payment_latency`

### Sintoma entregue

```text
checkout apresenta latência acima do esperado
```

### Evidências esperadas

- dependency histogram;
- `payment.request` trace.

### Pergunta central

Por que isso sustenta “payment.request provavelmente contribui para a latência” e não “root cause verificada”? 

---

## Grupo B — `payment_timeout`

### Sintoma

```text
pagamentos apresentam erros/timeout
```

### Evidências

- status 504 na aplicação;
- duração dependency;
- trace correspondente, se exportado.

### Pergunta

Como diferenciar falha de dependência de problema no checkout?

---

## Grupo C — `inventory_500`

### Sintoma

```text
consulta de catálogo falha
```

### Evidências

- requests/errors;
- health da aplicação;
- resposta de `/products`.

### Pergunta

Um health geral `ok` contradiz a indisponibilidade parcial?

---

## Grupo D — `inventory_slow`

### Sintoma

```text
catálogo apresenta degradação de duração
```

### Evidências

- request duration;
- comparação com baseline.

### Pergunta

Qual informação adicional seria necessária para localizar dependência interna?

---

## Grupo E — Ausência de mudanças recentes

Use um incidente de latência e consulte `get_recent_changes`.

### Objetivo

Mostrar que evidência negativa também elimina hipóteses.

### Pergunta

Como registrar “não há deployment/feature flag” sem tratar ausência como prova absoluta?

---

## Grupo F — Telemetria insuficiente

Escolha um sintoma para o qual o núcleo não tenha sinal suficiente.

### Objetivo

Produzir uma investigação honesta com `unsupported_claims`/baixa confiança, em vez de alucinar.

### Pergunta

Qual instrumento adicional vocês adicionariam em produção?

---

## Grupo G — Autonomia

Pegue a investigação de outro grupo e classifique possíveis remediações em:

```text
read-only
auto-safe
approval-required
prohibited
```

### Pergunta

Quais critérios determinam mudança de nível?

---

## Grupo H — Release gate

Use outputs funcionais, visuais e SRE e aplique a policy existente.

### Objetivo

Demonstrar três conjuntos de evidência:

```text
healthy → PASS
visual review → REVIEW
active incident → BLOCK
```

---

# Evidências obrigatórias

Cada grupo entrega no mínimo:

- sintoma inicial;
- primeira hipótese;
- queries/tools usadas;
- resultados brutos ou screenshot;
- hipótese revisada;
- causa provável ou declaração de insuficiência;
- confiança;
- remediation options;
- decisão sobre HITL.

---

# Rubrica

| Critério | Peso |
|---|---:|
| Hipótese deriva do sintoma | 15% |
| Evidências reais | 25% |
| Uso adequado de métricas/traces | 20% |
| Causalidade tratada com cautela | 15% |
| Autonomia/HITL coerentes | 15% |
| Comunicação técnica | 10% |

---

# Perguntas de apresentação

1. Que hipótese vocês tinham antes da primeira query?
2. Qual tool teve maior valor diagnóstico?
3. Qual evidência mudou a hipótese?
4. O que vocês **não** conseguem provar?
5. Que ação exigiria humano e por quê?

