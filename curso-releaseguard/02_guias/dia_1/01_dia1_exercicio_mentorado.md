# Dia 1 — Exercício mentorado

## Objetivo comum

Cada grupo deve transformar um requisito de negócio em um `TestPlan` executável, usando o núcleo congelado sem alterar as fronteiras de segurança centrais.

## Ponto inicial

Trabalhar a partir de:

```text
releaseguard_course/01_dia1
```

ou, se a turma estiver usando a versão consolidada:

```text
releaseguard_course/complete
```

## Arquivos que podem ser modificados

Cada grupo pode criar arquivos próprios em:

```text
student_work/day1/<grupo>/
```

E pode escrever planos/casos usando:

```text
qa/schemas.py
qa/executor.py
```

como dependências.

## Arquivos que não devem ser modificados

Não alterar:

```text
app/
qa/schemas.py
qa/policy.py
qa/executor.py
qa/generate_plan.py
```

O objetivo é resolver o caso **dentro dos contratos existentes**, não adaptar o sistema para o teste passar.

---

# Entregável obrigatório

Cada grupo deve entregar:

1. requisito reescrito de forma testável;
2. `TestPlan` válido;
3. justificativa do oracle;
4. execução HTTP real;
5. JSON do report;
6. uma limitação identificada;
7. uma resposta às perguntas de reflexão.

## Evidências mínimas

- print/terminal do plano;
- print do status esperado versus recebido;
- `report.json`;
- se usarem Ollama, saída estruturada original.

---

# Casos por grupo

## Grupo A — Carrinho stateful

### Contexto

Um carrinho precisa manter múltiplas operações em sequência. O segundo passo depende do ID criado no primeiro.

### Objetivo

Criar um plano que:

1. cria carrinho;
2. adiciona `sku-002` com quantidade válida;
3. consulta o carrinho;
4. comprova que a ação anterior alterou o estado.

### Principal decisão técnica

Como representar dependência de estado sem hardcodar `cart-001`?

### Evidência

O `cart_id` deve ser produzido pela aplicação.

---

## Grupo B — Boundary de estoque

### Contexto

`sku-003` possui estoque 5.

### Objetivo

Comparar dois casos:

- quantidade 5 → aceita;
- quantidade 6 → rejeitada.

### Principal decisão técnica

Definir por que isso é boundary testing e qual é o oracle de cada caso.

### Evidência

Dois reports ou um relatório consolidado mostrando os dois lados da fronteira.

---

## Grupo C — Checkout de carrinho vazio

### Contexto

A API rejeita checkout de carrinho vazio.

### Objetivo

Descobrir no OpenAPI/execução o comportamento esperado e escrever um plano defensável.

### Principal decisão técnica

Não inventar o status esperado. Derivá-lo do contrato/comportamento.

---

## Grupo D — Pagamento com valor divergente

### Contexto

O `PaymentRequest` precisa corresponder ao total do pedido.

### Objetivo

Criar pedido válido e, em seguida, enviar pagamento com valor incorreto.

### Principal decisão técnica

Gerenciar `order_id` dinamicamente e fundamentar o status de erro.

---

## Grupo E — Payment timeout

### Contexto

O cenário `payment_timeout` introduz timeout do provedor.

### Objetivo

Ativar cenário, gerar pedido e comprovar o comportamento HTTP do pagamento.

### Principal decisão técnica

Separar o fato de que o teste controla o cenário do fato de que o endpoint precisa responder conforme a regra operacional.

---

## Grupo F — Inventory 500

### Contexto

`inventory_500` torna `GET /products` indisponível.

### Objetivo

Criar plano que ative o cenário e valide a falha.

### Principal decisão técnica

Discutir se um teste que injeta falha está validando comportamento de resiliência ou apenas erro bruto.

---

## Grupo G — Host/método proibido

### Contexto

O sistema possui allowlist de host e método.

### Objetivo

Construir um TestPlan estruturalmente válido que seja bloqueado por `validate_plan_policy()`.

### Principal decisão técnica

Explicar por que esse resultado é PASS do controle de segurança, não falha do exercício.

---

## Grupo H — Plano gerado por Ollama

### Contexto

O grupo recebe um requisito diferente e precisa utilizar `generate_plan()`.

### Objetivo

Fornecer OpenAPI + runtime context e verificar se o plano resultante é executável.

### Principal decisão técnica

Registrar qualquer diferença entre:

```text
schema-valid
semanticamente válido
executável
```

---

# Comandos base

Reset:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

Produtos:

```bash
curl http://localhost:8000/products | python -m json.tool
```

Exemplo de execução em Python:

```python
from qa.executor import run_plan
from qa.schemas import TestPlan

plan = TestPlan.model_validate({...})
report = run_plan(plan)
print(report.as_dict())
```

---

# Critérios de avaliação

| Critério | Evidência | Peso |
|---|---|---:|
| Oracle fundamentado | requisito/OpenAPI/regra | 25% |
| Plano válido e mínimo | TestPlan | 20% |
| Execução HTTP real | report | 20% |
| Estado/placeholders corretos | passos executados | 15% |
| Controle/segurança respeitados | policy | 10% |
| Explicação técnica | apresentação | 10% |

---

# Perguntas para apresentação

Cada grupo responde em no máximo 3 minutos:

1. Qual era o risco de negócio?
2. De onde veio o oracle?
3. Que parte poderia ser gerada por IA sem risco excessivo?
4. Qual decisão continuou determinística?
5. O que faria este teste dar falso positivo?

---

# Extensões

Somente depois da solução obrigatória:

- gerar plano com Ollama;
- comparar plano manual versus gerado;
- criar segundo caso boundary;
- escrever uma validação semântica adicional fora do núcleo;
- representar o fluxo em n8n sem alterar o workflow oficial.
