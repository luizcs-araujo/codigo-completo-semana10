# Guia incremental — Aula 2

## Live coding: agente local de investigação com LangChain, Ollama e Qwen

**Duração planejada:** 2h30, com intervalo de 15 minutos  
**Formato:** o professor implementa; os alunos acompanham, executam e comparam resultados.  
**Projeto:** SupportOps Agent.

---

# 1. Resultado da aula

Ao final, a turma terá um agente que:

1. recebe o ID de um ticket;
2. decide quais tools de leitura usar;
3. consulta dados locais que simulam APIs internas;
4. executa um loop até obter evidência suficiente;
5. encerra com diagnóstico estruturado;
6. escala para humano quando a correção exige escrita;
7. grava uma trilha resumida da execução.

O cenário principal é o ticket `TCK-4821`: erro 403 depois de uma mudança de role. A solução esperada deve descobrir que o serviço está saudável, que a fonte de verdade autoriza o acesso, que o cache possui uma role antiga e que o runbook exige aprovação humana para invalidar o cache.

---

# 2. Arquitetura construída

```text
Usuário
  ↓
LangChain create_agent
  ↓
Qwen 3 no Ollama
  ↓ escolhe tools
get_ticket_context
get_user_access
get_recent_role_change
get_service_health
search_service_runbook
  ↓
TicketDiagnosis validado com Pydantic
  ↓
Trace local em JSON
```

Decisão pedagógica: todas as tools são **somente leitura**. O agente pode investigar e recomendar, mas não pode invalidar cache, alterar role ou reiniciar serviço.

---

# 3. Preparação antes da aula

Faça isso antes de compartilhar a tela:

```bash
ollama pull qwen3:4b
cd codigo_inicial
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m supportops.doctor
pytest -q
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Use `qwen3:4b` como padrão. Em máquinas mais fortes, `qwen3:8b` tende a selecionar tools com mais consistência. Em máquinas mais limitadas, `qwen3:1.7b` pode rodar, mas a confiabilidade do agente cai.

Tenha a pasta `codigo_solucao` aberta apenas como referência de recuperação. Não comece por ela.

---

# 4. Distribuição do tempo

| Etapa | Tempo |
|---|---:|
| Preparação e explicação do cenário | 10 min |
| Baseline sem tools | 8 min |
| Implementação das tools | 20 min |
| Inspeção de uma tool call | 12 min |
| Construção do agente e primeiro loop | 20 min |
| Intervalo | 15 min |
| Contrato operacional e diagnóstico | 15 min |
| Structured output com Pydantic | 18 min |
| Limite de loop e tracing | 20 min |
| Variações e comparação | 7 min |
| Fechamento | 5 min |
| **Total** | **150 min** |

---

# 5. Etapa 0 — Apresentar o problema

**Tempo:** 10 minutos

Mostre os dados disponíveis sem abrir ainda o código da solução:

```text
Ticket → usuário → acesso → mudança de role → saúde do serviço → runbook
```

Perguntas para a turma:

- O modelo consegue descobrir a causa usando apenas o ID do ticket?
- Quais informações são independentes e poderiam ser consultadas em paralelo?
- Qual ação não deve ser exposta ao agente?
- Em que ponto a investigação deve parar?

Explique que o backend simulado já existe em `supportops/repository.py`. O trabalho da aula começa na transformação dessas funções em capabilities para o agente.

---

# 6. Etapa 1 — Executar a baseline sem tools

**Tempo:** 8 minutos

Execute:

```bash
python -m supportops.baseline TCK-4821
```

A resposta pode admitir que não possui os dados ou pode inventar uma hipótese. Ambos os resultados servem à aula.

## Fala sugerida

> O modelo conhece conceitos gerais sobre erro 403, mas não conhece este ticket. Sem tools, qualquer diagnóstico específico é palpite.

Conecte ao conceito:

```text
LLM sem tools = conhecimento paramétrico
LLM com tools = acesso controlado ao estado real
```

---

# 7. Etapa 2 — Transformar funções em tools seguras

**Tempo:** 20 minutos

Abra `supportops/tools.py`.

A primeira tool já está pronta:

```python
@tool
def get_ticket_context(ticket_id: str) -> str:
    """Consulte primeiro os dados completos de um ticket técnico pelo ID."""
    return json.dumps(repository.get_ticket(ticket_id), ensure_ascii=False)
```

Use-a para mostrar três partes do contrato:

1. nome semântico;
2. tipos dos argumentos;
3. docstring dizendo quando usar.

Implemente as quatro tools restantes. A implementação esperada é:

```python
@tool
def get_user_access(user_id: str, resource: str) -> str:
    """Compare acesso autorizado e cache de roles de um usuário. Somente leitura."""
    user = repository.get_user(user_id)
    return json.dumps({
        "user_id": user_id,
        "resource": resource,
        "authorized_in_source_of_truth": resource in user["allowed_resources"],
        "roles_source_of_truth": user["roles_source_of_truth"],
        "roles_in_permission_cache": user["roles_in_permission_cache"],
        "cache_diverges_from_source": (
            user["roles_source_of_truth"] != user["roles_in_permission_cache"]
        ),
    }, ensure_ascii=False)
```

Faça as outras três seguindo o mesmo padrão. Depois atualize:

```python
TOOLS = [
    get_ticket_context,
    get_user_access,
    get_recent_role_change,
    get_service_health,
    search_service_runbook,
]
```

## Ponto de mediação

Compare:

```text
get_data(query)
```

com:

```text
get_user_access(user_id, resource)
```

A segunda tool reduz ambiguidade, limita escopo e facilita auditoria.

## Checagem rápida

No terminal:

```bash
python -c "from supportops.tools import get_ticket_context; print(get_ticket_context.invoke({'ticket_id':'TCK-4821'}))"
```

---

# 8. Etapa 3 — Ver a intenção de tool call antes do agente

**Tempo:** 12 minutos

Antes de usar `create_agent`, mostre o mecanismo isolado.

Crie temporariamente `supportops/probe_tool_call.py` ou copie o arquivo correspondente da solução:

```python
model_with_tools = build_model().bind_tools(TOOLS)
response = model_with_tools.invoke(
    "Descubra o que aconteceu no ticket TCK-4821. Comece consultando o ticket. /no_think"
)
print(response.tool_calls)
```

Execute:

```bash
python -m supportops.probe_tool_call
```

Explique:

- o Qwen não executou Python;
- ele produziu nome e argumentos;
- o runtime ainda precisaria validar e executar;
- `create_agent` automatizará o ciclo chamada → resultado → nova decisão.

Se o modelo responder em texto em vez de chamar a tool, repita com `qwen3:8b` ou torne a instrução mais direta. Essa variação é um bom exemplo de comportamento probabilístico.

---

# 9. Etapa 4 — Construir o loop com `create_agent`

**Tempo:** 20 minutos

Abra `supportops/agent.py` e importe:

```python
from langchain.agents import create_agent
from supportops.tools import TOOLS
```

Implemente inicialmente sem structured output:

```python
def build_agent():
    return create_agent(
        model=build_model(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="supportops_investigator",
    )
```

Implemente a primeira versão de `run_agent`:

```python
def run_agent(ticket_id: str):
    agent = build_agent()
    return agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Investigue o ticket {ticket_id}. /no_think",
        }]
    })
```

No `main.py`, imprima a última mensagem:

```python
result = run_agent(args.ticket_id)
print(result["messages"][-1].content)
```

Execute:

```bash
python -m supportops.main TCK-4821
```

Neste primeiro momento, aceite uma resposta textual. O objetivo é observar se aparecem múltiplas chamadas de tools.

## Perguntas durante a execução

- Qual tool foi chamada primeiro?
- O agente utilizou IDs retornados pelo ticket?
- Alguma consulta foi redundante?
- O agente parou cedo demais?

---

# 10. Intervalo

**Tempo:** 15 minutos

Antes do intervalo, deixe na tela o fluxo observado:

```text
Qwen → get_ticket_context → resultado → nova decisão → ... → resposta
```

---

# 11. Etapa 5 — Escrever o contrato operacional

**Tempo:** 15 minutos

Substitua o `SYSTEM_PROMPT` genérico pelo contrato da solução.

Os trechos essenciais são:

```text
- Sempre consulte get_ticket_context antes de concluir.
- Use os IDs retornados; não invente IDs.
- Não repita a mesma tool com os mesmos argumentos.
- Todas as tools são somente leitura.
- Se a correção exigir escrita, marque requires_human=true.
- Pare quando houver evidência suficiente ou ausência de progresso.
```

Execute novamente e compare:

```bash
python -m supportops.main TCK-4821
```

## Ponto de discussão

O prompt orienta o comportamento, mas não cria segurança absoluta. A segurança principal vem do catálogo: nenhuma função de invalidação de cache foi exposta.

---

# 12. Etapa 6 — Adicionar saída estruturada

**Tempo:** 18 minutos

Mostre `supportops/models.py`. Explique que Pydantic representa o contrato de integração com o restante do sistema.

Importe:

```python
from langchain.agents.structured_output import ToolStrategy
from supportops.models import TicketDiagnosis
```

Altere `build_agent`:

```python
return create_agent(
    model=build_model(),
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    response_format=ToolStrategy(
        schema=TicketDiagnosis,
        handle_errors="Retorne um único diagnóstico válido e use somente evidências das tools.",
    ),
)
```

Depois, em `run_agent`:

```python
diagnosis = result["structured_response"]
```

Explique que, para modelos sem structured output nativo selecionado pelo provider, a estratégia usa tool calling para produzir e validar a estrutura.

## Resultado esperado para `TCK-4821`

Os textos podem variar, mas a semântica deve ser próxima de:

```json
{
  "status": "needs_human",
  "probable_cause": "cache de permissões desatualizado",
  "confidence": "high",
  "requires_human": true,
  "stop_reason": "needs_write_action"
}
```

Evidências esperadas:

- role da fonte de verdade difere da role em cache;
- o usuário está autorizado ao recurso;
- o serviço está saudável;
- o runbook relaciona 403 pós-role a cache desatualizado.

---

# 13. Etapa 7 — Limitar o loop e registrar a execução

**Tempo:** 20 minutos

Adicione limite de grafo na invocação:

```python
result = agent.invoke(
    {"messages": [...]},
    config={"recursion_limit": settings.max_graph_steps},
)
```

Explique que o limite de recursão conta passos do grafo, não exatamente tools. O valor `14` é suficiente para o caso didático, mas não deve ser tratado como número universal.

Depois copie ou implemente `supportops/tracing.py` da solução. Ele registra somente:

- tool escolhida;
- argumentos;
- resumo do resultado;
- ordem dos eventos;
- `run_id`.

Não grave raciocínio interno do modelo.

Execute:

```bash
python -m supportops.main TCK-4821 --json
```

Abra o arquivo criado em `runs/` e reconstrua a investigação com a turma.

## Pergunta-chave

> Se o agente entregou uma resposta errada, conseguimos descobrir quais dados ele consultou e em que ordem?

Sem tracing, a resposta costuma ser “não”.

---

# 14. Etapa 8 — Variações rápidas

**Tempo:** 7 minutos

## Variação A — outro incidente

```bash
python -m supportops.main TCK-4822
```

A causa provável deve se relacionar ao serviço degradado e ao deploy recente. O agente deve usar um conjunto diferente de tools, apesar de compartilhar a mesma arquitetura.

## Variação B — ticket inexistente

```bash
python -m supportops.main TCK-9999
```

Observe como uma exceção da tool chega ao loop. Discuta onde colocar retries e quando transformar a falha em `blocked`.

## Variação C — tool perigosa

Pergunte sem implementar:

> O que mudaria se adicionássemos `invalidate_permission_cache()` ao catálogo?

Respostas esperadas:

- autorização;
- aprovação humana;
- idempotência;
- logs adicionais;
- ambiente permitido;
- política de retry;
- confirmação do alvo.

---

# 15. Fechamento

**Tempo:** 5 minutos

Reconstrua a progressão:

```text
função Python
→ tool com contrato
→ intenção estruturada do modelo
→ agente em loop
→ saída Pydantic
→ limite e tracing
```

Feche com três conclusões:

1. o modelo escolhe; a aplicação executa;
2. tools bem desenhadas reduzem o espaço de erro;
3. um agente só é depurável quando possui limites, estado de parada e rastros.

---

# 16. Caminho de corte

Se a aula atrasar:

1. não implemente o `probe_tool_call.py`; explique usando o retorno do próprio agente;
2. copie `tracing.py` pronto em vez de construí-lo linha a linha;
3. execute somente `TCK-4821`;
4. não remova structured output nem limite do loop, pois são o fechamento pedagógico da aula.

---

# 17. Problemas comuns

## Ollama não responde

```bash
python -m supportops.doctor
```

Em Linux, abra outro terminal e rode:

```bash
ollama serve
```

## Modelo não encontrado

```bash
ollama pull qwen3:4b
ollama list
```

## Tool não é chamada

- confirme que o modelo oferece suporte a tools;
- use `qwen3:8b` quando houver memória suficiente;
- torne a docstring e a instrução mais específicas;
- reduza tools sobrepostas;
- mantenha `temperature=0`.

## Loop atinge o limite

Não aumente o limite imediatamente. Primeiro verifique:

- tool repetida;
- resultado de tool pouco informativo;
- prompt sem critério de parada;
- schema final difícil demais para o modelo;
- catálogo com tools ambíguas.

## Structured output falha repetidamente

Simplifique campos e descrições, use valores literais curtos e confirme que o Qwen selecionado está chamando tools de forma estável.

---

# 18. Critérios para considerar o exercício concluído

- `pytest -q` passa;
- `python -m supportops.doctor` confirma o modelo;
- o agente chama `get_ticket_context` primeiro;
- o diagnóstico usa evidências reais;
- `TCK-4821` termina com necessidade de humano;
- nenhuma ação de escrita é executada;
- um trace é salvo em `runs/`;
- a saída final valida como `TicketDiagnosis`.

---

# 19. Referências técnicas usadas

- LangChain Agents: `https://docs.langchain.com/oss/python/langchain/agents`
- LangChain ChatOllama: `https://docs.langchain.com/oss/python/integrations/chat/ollama`
- LangChain Structured Output: `https://docs.langchain.com/oss/python/langchain/structured-output`
- Ollama Tool Calling: `https://docs.ollama.com/capabilities/tool-calling`
- Qwen 3 no Ollama: `https://ollama.com/library/qwen3`
