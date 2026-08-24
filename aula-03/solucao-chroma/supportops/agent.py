from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langgraph.errors import GraphRecursionError

from supportops.config import settings
from supportops.models import EvidenceReference, TicketDiagnosis
from supportops.tools import TOOLS
from supportops.tracing import save_trace, summarize_messages

SYSTEM_PROMPT = """
Você é um agente local de investigação de incidentes técnicos.

ORDEM DE TRABALHO
1. Consulte get_ticket_context antes de concluir qualquer diagnóstico.
2. Use IDs, serviço e ambiente retornados pelo ticket; não invente identificadores.
3. Colete observações operacionais relevantes pelas tools de leitura.
4. Quando a conclusão depender de procedimento, política, arquitetura ou histórico interno,
   use search_technical_docs com o serviço e o ambiente exatos do ticket.
5. Aceite como evidência documental somente resultados current=true, trust_level apropriado
   e compatíveis com serviço e ambiente.
6. Se a busca retornar sufficient=false, reformule a consulta no máximo uma vez.
7. Não repita a mesma tool com os mesmos argumentos e pare quando não houver progresso.

GOVERNANÇA
- Todas as tools são somente leitura.
- Não afirme que executou rollback, restart, alteração de role ou invalidação de cache.
- Ações de escrita em produção exigem requires_human=true.
- Documento obsoleto, de outro ambiente ou fonte não validada não sustenta recomendação.
- Se não houver evidência citável suficiente, encerre como insufficient_evidence.
- Cite source_path#heading, versão, trecho e relevância.
- Não exponha raciocínio interno; produza apenas tool calls e o diagnóstico estruturado.
""".strip()


@dataclass
class AgentRun:
    diagnosis: TicketDiagnosis
    tools_used: list[str]
    trace_path: str


def build_model() -> ChatOllama:
    return ChatOllama(
        model=settings.model,
        base_url=settings.base_url,
        temperature=0,
        reasoning=settings.reasoning,
        num_ctx=settings.num_ctx,
        validate_model_on_init=True,
    )


def build_agent(model: BaseChatModel | None = None, tools=None, middleware=None):
    active_tools = tools or TOOLS
    active_middleware = middleware if middleware is not None else [
        ModelCallLimitMiddleware(run_limit=settings.max_model_calls, exit_behavior="end"),
        ToolCallLimitMiddleware(run_limit=settings.max_tool_calls, exit_behavior="continue"),
        ToolRetryMiddleware(max_retries=1, tools=[tool.name for tool in active_tools]),
    ]
    return create_agent(
        model=model or build_model(),
        tools=active_tools,
        middleware=active_middleware,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(
            schema=TicketDiagnosis,
            handle_errors="Retorne um TicketDiagnosis válido usando somente evidências observadas e citáveis.",
        ),
        name="supportops_chroma_investigator",
    )


def _blocked(ticket_id: str, reason: str, stop_reason: str) -> TicketDiagnosis:
    return TicketDiagnosis(
        ticket_id=ticket_id,
        status="blocked",
        probable_cause=reason,
        confidence="low",
        evidence=[EvidenceReference(
            claim="Execução interrompida por controle operacional",
            source="runtime#guardrail",
            version="1",
            relevance=1.0,
            excerpt=reason[:400],
        )],
        retrieval_queries=[],
        next_steps=["Revisar trace, disponibilidade das tools e limites antes de tentar novamente."],
        requires_human=True,
        stop_reason=stop_reason,
    )


def run_agent(ticket_id: str, model: BaseChatModel | None = None) -> AgentRun:
    if not settings.agent_enabled:
        return AgentRun(_blocked(ticket_id, "Kill switch AGENT_ENABLED=false", "kill_switch"), [], "")

    graph = build_agent(model=model)
    message = f"Investigue o ticket {ticket_id}. Use evidências atuais, pare sem progresso e finalize em TicketDiagnosis. /no_think"
    try:
        result: dict[str, Any] = graph.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"recursion_limit": settings.max_graph_steps},
        )
    except GraphRecursionError:
        diagnosis = _blocked(ticket_id, "O agente atingiu o limite do grafo", "step_limit")
        result = {"messages": []}
    else:
        diagnosis = result.get("structured_response")
        if diagnosis is None:
            diagnosis = _blocked(ticket_id, "A execução terminou sem saída estruturada", "step_limit")
        elif not isinstance(diagnosis, TicketDiagnosis):
            diagnosis = TicketDiagnosis.model_validate(diagnosis)

    events, tools_used = summarize_messages(result.get("messages", []))
    trace_path = save_trace(settings.runs_dir, ticket_id, events)
    return AgentRun(diagnosis=diagnosis, tools_used=tools_used, trace_path=str(trace_path))
