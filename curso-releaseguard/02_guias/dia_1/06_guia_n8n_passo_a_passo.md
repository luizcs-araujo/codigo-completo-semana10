# ReleaseGuard — Guia n8n passo a passo

## Objetivo

Reproduzir e explicar o workflow validado do Dia 1 usando a interface atual do n8n.

Arquivo congelado:

```text
complete/n8n/qa_test_generator.json
```

ID do workflow:

```text
releaseguard-day1-qa-plan
```

## Referências oficiais consultadas

- Basic LLM Chain: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.chainllm/
- Structured Output Parser: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.outputparserstructured/
- Structured Output Parser — common issues: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.outputparserstructured/common-issues/
- Ollama Chat Model — common issues: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/common-issues/
- Ollama credentials: https://docs.n8n.io/integrations/builtin/credentials/ollama/

A documentação atual do n8n descreve o **Basic LLM Chain** como o node para definir o prompt e conectar um model e, opcionalmente, um output parser. Isso corresponde exatamente ao problema do Dia 1. Não usamos AI Agent porque não precisamos de tool selection dinâmica nesta etapa.

---

# 1. Pré-condições

Antes de abrir o n8n:

- FastAPI em `localhost:8000`;
- Ollama em `localhost:11434`;
- n8n rodando em Docker;
- `qwen3:8b` instalado.

No host:

```bash
curl http://localhost:8000/health
curl http://localhost:11434/api/tags
```

Dentro do n8n Docker, a aplicação host é acessada via:

```text
http://host.docker.internal:8000
```

O Ollama via:

```text
http://host.docker.internal:11434
```

---

# 2. Importar o workflow pronto

1. Abra o n8n.
2. Na tela de workflows, abra o menu de importação.
3. Escolha **Import from File** / **Import workflow from file** — o texto exato pode variar levemente entre releases.
4. Selecione:

```text
complete/n8n/qa_test_generator.json
```

5. Confirme a importação.
6. Verifique se aparecem os nodes:

```text
Manual Trigger
Requirement
Fetch OpenAPI
Fetch Products
Generate TestPlan
Ollama Chat Model
Structured Output Parser
Validation
Execute Plan
Report
```

### Checkpoint

A importação deve manter connections. Se aparecerem nodes soltos, não avance.

> Uma versão anterior do material não tinha workflow ID e falhou com `SQLITE_CONSTRAINT: NOT NULL constraint failed: workflow_entity.id`. O núcleo congelado já contém o ID estável.

---

# 3. Configurar credencial Ollama

## 3.1 Abrir o node

Clique em:

```text
Ollama Chat Model
```

## 3.2 Credentials

No campo de credencial, crie ou selecione uma credencial do tipo Ollama.

Base URL:

```text
http://host.docker.internal:11434
```

Salve.

O model configurado no workflow é:

```text
qwen3:8b
```

## 3.3 Teste simples

Se a UI oferecer **Test credential**, execute.

Caso contrário, execute posteriormente o node conectado ao Basic LLM Chain.

### Erro comum

Usar:

```text
http://localhost:11434
```

quando n8n está em Docker.

Nesse caso, `localhost` aponta para o container n8n, não para seu Mac/host.

---

# 4. Node `Manual Trigger`

## Papel

Fornece início manual e controlado para aula.

## O que mostrar

Clique no node e explique:

> “Estamos evitando triggers automáticos porque queremos inspecionar cada estado do workflow durante a demonstração.”

Não há configuração importante.

---

# 5. Node `Requirement`

## Tipo

`Edit Fields (Set)` / Set node.

## Valor validado

Campo:

```text
requirement
```

Valor:

```text
Um usuário não pode adicionar ao carrinho uma quantidade maior que o estoque disponível.
```

## Como verificar

Execute o node ou o workflow até este ponto.

No painel **Output**, confirme um item com:

```json
{
  "requirement": "Um usuário não pode adicionar ao carrinho uma quantidade maior que o estoque disponível."
}
```

### O que explicar

Esse texto é a intenção de negócio. Ainda não contém endpoint, fixture nem status esperado.

---

# 6. Node `Fetch OpenAPI`

## Tipo

`HTTP Request`.

## URL

```text
http://host.docker.internal:8000/openapi.json
```

## Método

```text
GET
```

## Como verificar

Execute o node.

No output, procure:

```text
paths
```

E dentro de `paths`:

```text
/cart
/cart/{cart_id}/items
```

### Checkpoint

Se os paths não aparecem, o n8n não está alcançando o FastAPI.

### O que explicar

O contrato OpenAPI é evidência de engenharia. O modelo não precisa inventar quais endpoints existem.

---

# 7. Node `Fetch Products`

## Tipo

`HTTP Request`.

## URL

```text
http://host.docker.internal:8000/products/sku-001
```

## Método

```text
GET
```

## Output esperado

```json
{
  "id": "sku-001",
  "name": "Notebook Pro",
  "price": 5499.0,
  "stock": 3
}
```

### O que explicar

Essa consulta foi adicionada após a validação adversarial porque um schema pode ser perfeito e o modelo ainda inventar valores de fixture. O workflow fornece estoque real.

---

# 8. Node `Generate TestPlan`

## Tipo

Pesquise/adicone:

```text
Basic LLM Chain
```

Na versão do workflow congelado, o type é:

```text
@n8n/n8n-nodes-langchain.chainLlm
```

## Prompt type

Selecione equivalente a:

```text
Define below
```

O workflow usa `promptType: define`.

## Texto do prompt validado

```text
Requisito: {{$node["Requirement"].json["requirement"]}}

Produto real: {{ JSON.stringify($json) }}

Contrato POST /cart: {{ JSON.stringify($node["Fetch OpenAPI"].json["paths"]["/cart"]) }}

Contrato POST /cart/{cart_id}/items: {{ JSON.stringify($node["Fetch OpenAPI"].json["paths"]["/cart/{cart_id}/items"]) }}

Gere exatamente dois passos: crie o carrinho e depois tente adicionar sku-001 com quantity 4. Preserve literalmente {cart_id}. Inclua json_body em ambos os passos; no primeiro use também {"product_id":"sku-001","quantity":4}, embora o endpoint ignore esse corpo. Espere 200 e depois 409.
```

## System message

```text
Você é um engenheiro de QA. Gere um TestPlan HTTP mínimo, seguro e diretamente executável. Use apenas paths, métodos, corpos e status documentados no OpenAPI. Use produtos reais fornecidos. Crie o carrinho antes de usar {cart_id}. O oracle deve vir do requisito ou contrato.
```

## Output parser

Ative a opção de output parser / specific output format.

O workflow congelado usa:

```text
hasOutputParser = true
```

### Conexões especiais

O node precisa receber:

- `Ollama Chat Model` em **Chat Model**;
- `Structured Output Parser` em **Output Parser**.

### O que explicar

O Basic LLM Chain não está “agindo”. Ele está fazendo transformação estruturada:

```text
contexto → TestPlan
```

---

# 9. Subnode `Ollama Chat Model`

Conecte ao conector **Chat Model** do Basic LLM Chain.

Configuração:

```text
Model: qwen3:8b
Credential: Ollama account
Base URL da credencial: http://host.docker.internal:11434
```

No workflow congelado, o mesmo model também alimenta o parser para auto-fix.

### Checkpoint

A connection visual deve aparecer do model para:

1. `Generate TestPlan`;
2. `Structured Output Parser`.

Essa segunda ligação foi necessária para o auto-fix do parser funcionar corretamente.

---

# 10. Subnode `Structured Output Parser`

Conecte ao conector **Output Parser** do Basic LLM Chain.

## Schema example validado

```json
{
  "name": "checkout bloqueia excesso",
  "intent": "validar estoque",
  "risk": "overselling",
  "oracle": "HTTP 409 ao exceder estoque",
  "steps": [
    {
      "name": "criar carrinho",
      "method": "POST",
      "path": "/cart",
      "json_body": {"product_id":"sku-001","quantity":4},
      "expect_status": 200
    },
    {
      "name": "adicionar quantidade acima do estoque",
      "method": "POST",
      "path": "/cart/{cart_id}/items",
      "json_body": {"product_id":"sku-001","quantity":4},
      "expect_status": 409
    }
  ]
}
```

## Auto-fix

Ativado no workflow congelado.

### Nuance para explicar

A documentação atual do n8n alerta que structured output junto a agentes pode ser menos previsível e recomenda em vários casos uma chain separada para parsing. Esse é outro motivo para esta aula usar Basic LLM Chain em vez de AI Agent.

---

# 11. Executar `Generate TestPlan`

Execute o node ou o workflow até ele.

O output validado veio embrulhado pelo parser em:

```text
$json.output
```

Isso é importante porque uma versão anterior enviava o wrapper inteiro para a API e recebia FastAPI 422.

No output, expanda:

```text
output → steps
```

Verifique:

```text
POST /cart → 200
POST /cart/{cart_id}/items → 409
sku-001
quantity 4
```

### Checkpoint

Se esses elementos não estiverem presentes, não avance para execução.

---

# 12. Node `Validation`

## Tipo

`Code`.

## Linguagem

JavaScript.

## Código exato do núcleo

```javascript
const plan = $json.output;
const [create, add] = plan?.steps ?? [];
if (
  plan.steps.length !== 2 ||
  create.method !== 'POST' ||
  create.path !== '/cart' ||
  create.expect_status !== 200 ||
  add.method !== 'POST' ||
  add.path !== '/cart/{cart_id}/items' ||
  add.expect_status !== 409 ||
  add.json_body?.product_id !== 'sku-001' ||
  add.json_body?.quantity <= 3
) {
  throw new Error('Generated plan failed deterministic requirement validation');
}
return [{ json: plan }];
```

## Como explicar

Este node é deliberadamente “menos inteligente”. Ele faz justamente o que o LLM não deve controlar:

- invariantes do exercício;
- fixture obrigatória;
- ordem;
- status;
- condição de quantidade.

### Demonstração

Abra input e output lado a lado.

Mostre que o wrapper `output` desaparece e que o node retorna o plano puro.

---

# 13. Node `Execute Plan`

## Tipo

`HTTP Request`.

## Método

```text
POST
```

## URL

```text
http://host.docker.internal:8000/qa/execute-plan
```

## Body

Ative envio de body raw JSON.

Expression validada:

```text
{{ JSON.stringify($json) }}
```

Content-Type:

```text
application/json
```

## Output esperado

Estrutura equivalente a:

```json
{
  "name": "...",
  "passed": true,
  "steps": [
    {"status":200,"expected_status":200,"passed":true},
    {"status":409,"expected_status":409,"passed":true}
  ]
}
```

### O que explicar

O n8n não executa arbitrariamente cada URL gerada pelo LLM. Ele envia o plano inteiro ao endpoint controlado `/qa/execute-plan`, que usa a policy e o executor Python congelados.

Isso preserva uma única fronteira de execução.

---

# 14. Node `Report`

É um `No Operation` node.

O papel pedagógico é simplesmente deixar o resultado final fácil de selecionar no canvas.

Clique nele e abra o output.

Aponte:

```text
passed: true
```

E os dois status.

---

# 15. Executar o workflow completo

1. Resetar aplicação:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

2. No n8n, clique **Execute Workflow**.
3. Aguarde todos os nodes ficarem verdes.
4. Clique em `Report`.

### Checklist visual

- [ ] Manual Trigger verde.
- [ ] Requirement verde.
- [ ] Fetch OpenAPI verde.
- [ ] Fetch Products verde.
- [ ] Generate TestPlan verde.
- [ ] Validation verde.
- [ ] Execute Plan verde.
- [ ] Report verde.

---

# 16. Troubleshooting do workflow

## `workflow_entity.id` / import failure

Confirme que está importando o arquivo congelado atual. Ele possui top-level:

```json
"id": "releaseguard-day1-qa-plan"
```

## Ollama indisponível

Credencial deve usar:

```text
http://host.docker.internal:11434
```

## FastAPI 422 em Execute Plan

Abra `Validation`. O output enviado deve ser o plano puro, não:

```json
{"output": {...}}
```

## Parser retorna campos nulos

Confira o JSON Schema Example e a conexão do Ollama Chat Model ao Structured Output Parser.

## `Generated plan failed deterministic requirement validation`

Isso é uma falha correta. Abra output do `Generate TestPlan` e compare:

- path;
- status;
- fixture;
- quantity.

Não desabilite Validation para “fazer passar”.

## FastAPI não acessível do container

Use:

```text
host.docker.internal
```

não `localhost`.

---

# 17. Fechamento conceitual do n8n

Ao terminar, faça a turma nomear as responsabilidades:

| Componente | Responsabilidade |
|---|---|
| Requirement | intenção de negócio |
| OpenAPI/Product | contexto verificável |
| Basic LLM Chain | propor TestPlan |
| Structured Parser | forma |
| Validation | invariantes semânticos do exercício |
| `/qa/execute-plan` | policy + HTTP real |
| Report | evidência |

Pergunta de fechamento:

> “Qual dessas etapas vocês removeriam se migrássemos o workflow para Python puro?”

Resposta esperada: talvez a interface/orquestração do n8n, **não** os contratos e controles.
