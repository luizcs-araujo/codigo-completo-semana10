# Dia 1 — Guia de implementação ao vivo

## Tema

**QA funcional low-code com IA: do requisito ao TestPlan executável**

## Resultado que deve existir após 40 minutos

O aluno precisa ter observado esta cadeia completa:

```text
requisito
→ schema
→ plano de teste
→ política determinística
→ HTTP real
→ 200 / 409
→ assertion
→ relatório
→ plano gerado por Ollama
```

> O foco não é digitar o projeto do zero. O núcleo está congelado e será aberto incrementalmente para explicar as decisões. Cada etapa deve ser demonstrada com algo observável.

---

# Preparação antes da aula

Terminal 1:

```bash
cd releaseguard_course/complete
source .venv/bin/activate
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TEXT_MODEL=qwen3:8b
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Terminal 2:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

Abra também:

```text
http://localhost:8000/docs
http://localhost:8000/products
```

---

# 0–5 min — Começar pelo requisito e pelo dado real

## Onde estamos

Ainda não fale de “low-code”, structured output ou agentes. Mostre um requisito concreto.

## Problema observado

Requisito:

> “Um usuário não pode adicionar ao carrinho uma quantidade maior que o estoque disponível.”

A pergunta para a turma é: **como transformamos essa frase em uma evidência executável?**

## Arquivos abertos

```text
app/state/store.py
app/api/routes.py
```

## O que já existe

Em `app/state/store.py`:

```python
PRODUCT_FIXTURES = {
 'sku-001': Product(id='sku-001', name='Notebook Pro', price=5499.0, stock=3),
 'sku-002': Product(id='sku-002', name='Mouse Ergo', price=249.0, stock=12),
 'sku-003': Product(id='sku-003', name='Monitor 27', price=1799.0, stock=5),
}
```

Em `app/api/routes.py`, `add_item()` retorna 409 quando `quantity > p.stock`.

## O que explicar

- O requisito sozinho não é teste.
- Precisamos de fixture, ação e oracle.
- `sku-001` tem estoque 3; quantidade 4 ou 99 viola a regra.
- O status 409 não foi escolhido pelo modelo: está implementado/documentado na API.

## Comando para demonstrar

```bash
curl http://localhost:8000/products | python -m json.tool
```

## Output que importa

Você deve apontar:

```text
id: sku-001
stock: 3
```

## Checkpoint

Se a turma viu o dado real que fundamentará o teste, avance.

## Caso não funcione

```bash
curl http://localhost:8000/health
```

Se falhar, FastAPI não está de pé.

## Gancho

> “Já sabemos que 4 é inválido porque o estoque é 3. Agora precisamos representar essa intenção de teste de uma forma que código e LLM consigam compartilhar sem depender de texto livre.”

---

# 5–10 min — Abrir o schema canônico

## Arquivo

```text
qa/schemas.py
```

## Código exato

```python
class HttpStep(BaseModel):
    name: str = Field(min_length=3)
    method: Literal['GET','POST','PUT','PATCH','DELETE']
    path: str = Field(pattern=r'^/.*$')
    json_body: dict | None = None
    expect_status: int = Field(ge=100, le=599)

class TestPlan(BaseModel):
    __test__ = False
    name: str = Field(min_length=3)
    intent: str = Field(min_length=5)
    risk: str = Field(min_length=3)
    oracle: str = Field(min_length=5)
    steps: list[HttpStep] = Field(min_length=1, max_length=8)
```

## O que explicar

- `HttpStep` é uma unidade de execução.
- `TestPlan` carrega **intenção**, **risco** e **oracle**, não só chamadas HTTP.
- Pydantic garante forma/tipos, mas ainda não garante que um endpoint exista ou que o oracle faça sentido.
- O regex `^/.*$` foi necessário para compatibilidade com o structured output do Ollama; uma versão anterior mais restrita gerou erro 400 no runtime.

## Demonstração simples

```bash
python - <<'PY'
from qa.schemas import TestPlan
p=TestPlan.model_validate({
 'name':'teste de estoque',
 'intent':'bloquear excesso de estoque',
 'risk':'overselling',
 'oracle':'HTTP 409 ao exceder estoque',
 'steps':[{'name':'criar carrinho','method':'POST','path':'/cart','expect_status':200}]
})
print(p.model_dump_json(indent=2))
PY
```

## Checkpoint

JSON validado aparece sem erro.

## Caso não funcione

Se `ValidationError`, leia a mensagem em voz alta. Isso é útil pedagogicamente: mostra que schema é uma fronteira real.

## Gancho

> “O schema impede um TestPlan malformado. Mas ainda permitiria `POST /delete-everything` se o path tivesse a forma certa. Precisamos separar validação estrutural de autorização.”

---

# 10–15 min — Mostrar a política determinística

## Arquivo

```text
qa/policy.py
```

## Código exato

```python
ALLOWED_METHODS={'GET','POST'}
ALLOWED_PREFIXES=('/products','/cart','/checkout','/payments','/orders','/lab/scenarios')

def validate_plan_policy(plan:TestPlan, base_url:str)->None:
    parsed=urlparse(base_url)
    if parsed.hostname not in {'127.0.0.1','localhost','host.docker.internal'}:
        raise ValueError('base_url host is not allowlisted')
    for step in plan.steps:
        if step.method not in ALLOWED_METHODS:
            raise ValueError(f'method not allowed: {step.method}')
        if not step.path.startswith(ALLOWED_PREFIXES):
            raise ValueError(f'path not allowed: {step.path}')
```

## O que explicar

- O LLM não recebe autoridade implícita só porque gerou JSON válido.
- A policy limita método, paths e host.
- Essa é a diferença entre “orientar por prompt” e “impor invariant no código”.
- O mesmo padrão vale para agentes com ferramentas mutáveis.

## Demonstração de falha controlada

```bash
python - <<'PY'
from qa.schemas import TestPlan
from qa.policy import validate_plan_policy
p=TestPlan.model_validate({
 'name':'plano proibido','intent':'mostrar policy','risk':'ação indevida',
 'oracle':'a policy deve bloquear',
 'steps':[{'name':'deletar algo','method':'DELETE','path':'/orders/1','expect_status':200}]
})
try:
    validate_plan_policy(p,'http://127.0.0.1:8000')
except Exception as e:
    print(type(e).__name__, e)
PY
```

## Output esperado

```text
ValueError method not allowed: DELETE
```

## Checkpoint

A turma viu uma ação estruturalmente válida ser bloqueada pela política.

## Gancho

> “Agora temos um plano autorizado. Ainda falta a parte que transforma intenção em ação: o executor HTTP.”

---

# 15–20 min — Abrir o executor HTTP real

## Arquivo

```text
qa/executor.py
```

## Código a destacar

```python
def run_plan(plan:TestPlan, base_url:str='http://127.0.0.1:8000', client:httpx.Client|None=None)->TestReport:
    validate_plan_policy(plan,base_url)
    own=client is None
    client=client or httpx.Client(base_url=base_url,timeout=3.0)
    context={}
    results=[]
    try:
        for step in plan.steps:
            path=step.path.format(**context)
            r=client.request(step.method,path,json=step.json_body)
            body=r.json() if 'application/json' in r.headers.get('content-type','') else r.text
            if step.path=='/cart' and isinstance(body,dict) and 'id' in body:
                context['cart_id']=body['id']
            if step.path=='/checkout' and isinstance(body,dict) and 'id' in body:
                context['order_id']=body['id']
            results.append(StepResult(
                step.name,step.method,path,r.status_code,
                step.expect_status,r.status_code==step.expect_status,body
            ))
        return TestReport(plan.name, all(s.passed for s in results), results)
```

## O que explicar

- HTTP é real; não há chamada direta a função interna da aplicação.
- `context` resolve placeholders criados por passos anteriores.
- O oracle operacional é simples e explícito: `status_code == expect_status`.
- O executor não “interpreta” sucesso; ele compara evidência.
- Timeout de 3 segundos limita comportamento ruim.

## Demonstração rápida

Ainda não rode o plano inteiro. Mostre o `sample_plan`:

```text
qa/sample_plans.py
```

Aponte o segundo passo:

```python
{'product_id':'sku-001','quantity':99}
```

e o oracle:

```python
'expect_status':409
```

## Gancho

> “Já conseguimos seguir o plano. Agora vamos executar e descobrir se a aplicação realmente produz a evidência que o teste espera.”

---

# 20–25 min — Executar o plano determinístico ponta a ponta

## Comando

```bash
python -m qa.run_demo
```

## O que deve acontecer

`qa.run_demo` chama `run_plan(insufficient_stock_plan())`, imprime o report e persiste:

```text
artifacts/day1/functional_report.json
```

## Output de referência validado

```json
{
  "name": "checkout bloqueia quantidade acima do estoque",
  "passed": true,
  "steps": [
    {
      "method": "POST",
      "path": "/cart",
      "status": 200,
      "expected_status": 200,
      "passed": true
    },
    {
      "method": "POST",
      "path": "/cart/cart-003/items",
      "status": 409,
      "expected_status": 409,
      "passed": true,
      "body": {"detail": "insufficient stock"}
    }
  ]
}
```

O `cart-003` pode mudar.

## Como demonstrar

Depois do terminal:

```bash
cat artifacts/day1/functional_report.json
```

Aponte três linhas:

```text
status: 409
expected_status: 409
passed: true
```

## Checkpoint

Se o report foi criado e o segundo step passou por 409, avance.

## Caso não funcione

1. `curl http://localhost:8000/health`;
2. resetar cenário;
3. conferir que `sku-001` existe;
4. conferir porta 8000.

## Gancho

> “Até aqui nenhum LLM foi necessário. Isso é intencional: primeiro estabelecemos uma execução confiável. Agora podemos perguntar qual parte vale a pena delegar à IA.”

---

# 25–30 min — Mostrar o que o LLM realmente gera

## Arquivo

```text
qa/generate_plan.py
```

## Trecho principal

```python
SYSTEM_INSTRUCTIONS = """Você é um engenheiro de QA. Gere um plano HTTP mínimo, seguro e diretamente executável. Use somente paths, métodos, corpos e status documentados no OpenAPI fornecido. Use valores concretos do contexto de execução; apenas cart_id e order_id podem ser placeholders, depois dos passos que os criam. O oracle deve estar ancorado no requisito ou no contrato, nunca inventado. Retorne somente o schema solicitado."""
```

E:

```python
schema=TestPlan.model_json_schema()
```

O prompt recebe:

- requisito;
- produtos reais;
- OpenAPI;
- JSON Schema.

## O que explicar

A IA não recebe só “escreva um teste”. Ela recebe a fronteira operacional.

Structured output garante forma; contexto real reduz valores inventados.

## Comando live

```bash
python -m qa.generate_plan
```

## O que observar

Procure no JSON:

- `/cart`;
- `/cart/{cart_id}/items`;
- `sku-001`;
- quantidade > 3;
- 200 depois 409;
- oracle ancorado em estoque.

## Checkpoint

O Pydantic aceitou o retorno e os dados fazem sentido com a API real.

## Caso não funcione

- confirme `ollama list`;
- confirme `/api/tags`;
- confirme API FastAPI;
- se houver 400 de schema, você provavelmente não está usando o núcleo congelado.

## Gancho

> “Mesmo structured output não garante semântica. O modelo pode escolher um status que existe como número, mas não está documentado naquele endpoint. É por isso que existe uma segunda validação.”

---

# 30–35 min — Mostrar correção semântica limitada

## Arquivo

```text
qa/generate_plan.py
```

## Código a destacar

```python
def _semantic_issues(plan:TestPlan,openapi:dict)->list[str]:
    ...
```

Cheque especificamente:

```python
if operation is None:
    issues.append(...)

if str(step.expect_status) not in documented:
    issues.append(...)

if operation.get('requestBody',{}).get('required') and step.json_body is None:
    issues.append(...)
```

E o bounded retry:

```python
for _ in range(3):
    ...
    if not issues:
        return plan
    messages.extend([...])
raise ValueError(...)
```

## O que explicar

- Autocorreção é bounded: no máximo 3 tentativas.
- O sistema informa problemas concretos; não pede “tente de novo melhor”.
- Se falhar, falha explicitamente.
- Essa é uma forma controlada de self-healing: corrigir representação, não esconder um bug do produto.

## Demonstração

Não force o modelo a errar ao vivo. Em vez disso, mostre o código e conte a evidência da validação: uma versão inicial gerou plano schema-valid mas semanticamente inválido; a validação semântica foi adicionada para detectar status/body/path inconsistentes.

## Checkpoint

A turma consegue explicar diferença entre:

```text
JSON válido
vs
TestPlan executável
```

## Gancho

> “Temos a mesma pipeline funcionando em código. Agora vamos levá-la para uma interface low-code e observar onde o n8n ajuda — e onde ele não substitui nossas políticas.”

---

# 35–40 min — Abrir o workflow n8n

## Arquivo

```text
n8n/qa_test_generator.json
```

## Fluxo real

```text
Manual Trigger
→ Requirement
→ Fetch OpenAPI
→ Fetch Products
→ Generate TestPlan
   ├─ Ollama Chat Model
   └─ Structured Output Parser
→ Validation
→ Execute Plan
→ Report
```

## O que explicar

- O node central é **Basic LLM Chain**, não AI Agent.
- Motivo: não precisamos que o modelo escolha tools. Precisamos mapear contexto → estrutura.
- Structured Output Parser é apropriado porque a saída é um contrato.
- `Validation` continua JavaScript determinístico.
- `Execute Plan` chama `/qa/execute-plan`; o executor Python continua sendo a fronteira segura.

## Demonstração

Abra a execução validada no n8n e percorra os outputs:

1. Requirement;
2. Fetch Products;
3. Generate TestPlan;
4. Validation;
5. Execute Plan;
6. Report.

## Checkpoint final

O aluno deve conseguir verbalizar:

> “O n8n orquestra visualmente a mesma arquitetura. Ele não remove o schema, a policy nem o executor.”

## Gancho para teoria

> “Agora que vimos a pipeline inteira, podemos formalizar o que low-code testing realmente é, o papel de um test oracle e por que self-healing pode se tornar perigoso.”

