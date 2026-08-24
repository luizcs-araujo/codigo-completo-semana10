from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.types import Command

from supportops.config import settings
from supportops.models import EvidenceReference, TicketDiagnosis
from supportops.tools import TOOLS
from supportops.tracing import save_trace, summarize_messages

SYSTEM_PROMPT = """
You'll receive an ID for a technical issue/ticket. It can be of many types and your duty is to interpret it and deccide which is the best path to 
get all required information to acchieve a good response to it. For that, every time, you'll first need to read the ticket's information.

keep in mind, that in some cases, your actions can and should cause deferring to humans. In these cases, keep it clear and explicit for the end user just on your final response.

## Plan Clause
For every ticket context you get, you'll write a plan with a step-by-step guide to accomplish this. Each step should be clear and use either one of the tools, or your own reasoning.

## Reflection Clause
In case you find errors when consuming from any of your tools, reflect on the error, then adjust your tool calls
 if that would solve it, then try the call again. 
 
## Execution Rules 
- Always use the plan clause.
- Ponder about using reflection clause.
- If you fail 3 times to make the same tool call, abort.


## RAG Clause
- In case the search doesn't return any documents, you can reformulate the search query ONCE.
- If there are no information retrieved, your answer should reflect that only. Do not invent information.

""".strip()


ApprovalHandler = Callable[[Mapping[str, Any]], bool]


@dataclass
class AgentRun:
    diagnosis: TicketDiagnosis
    tools_used: list[str]
    trace_path: str
    messages: list[Any]


checkpointer = InMemorySaver()


def build_model() -> ChatOllama:
    return ChatOllama(
        model=settings.model,
        base_url=settings.base_url,
        temperature=0,
        reasoning=settings.reasoning,
        num_ctx=settings.num_ctx,
        # Permite ao renderer estimar os tokens do trace de raciocínio quando
        # o Ollama não fornece uma separação específica em usage_metadata.
        logprobs=True,
        validate_model_on_init=True,
    )


def build_agent(model: BaseChatModel | None = None, middleware=None):
    retryable_tools = [
        tool.name for tool in TOOLS if tool.name != "invalidate_permission_cache"
    ]
    active_middleware = middleware if middleware is not None else [
        HumanInTheLoopMiddleware(
            interrupt_on={
                "invalidate_permission_cache": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": (
                        "A invalidação do cache de permissões altera estado e "
                        "requer aprovação humana explícita."
                    ),
                }
            }
        ),
        ModelCallLimitMiddleware(
            run_limit=settings.max_model_calls,
            exit_behavior="end",
        ),
        ToolCallLimitMiddleware(
            run_limit=settings.max_tool_calls,
            exit_behavior="continue",
        ),
        ToolRetryMiddleware(max_retries=1, tools=retryable_tools),
    ]
    return create_agent(
        model=model or build_model(),
        tools=TOOLS,
        middleware=active_middleware,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(
            schema=TicketDiagnosis,
            handle_errors=(
                "Retorne um TicketDiagnosis válido, citando apenas dados das tools."
            ),
        ),
        checkpointer=checkpointer,
        name="supportops_aula3_chroma",
    )


def _blocked(ticket_id: str, reason: str) -> TicketDiagnosis:
    return TicketDiagnosis(
        ticket_id=ticket_id,
        status="blocked",
        probable_cause=reason,
        confidence="low",
        evidence=[
            EvidenceReference(
                claim="Execução interrompida por limite",
                source="runtime#guardrail",
                version="1",
                relevance=1.0,
                excerpt=reason,
            )
        ],
        retrieval_queries=[],
        next_steps=["Revisar limites e trace."],
        requires_human=True,
        stop_reason="step_limit",
    )


def _ask_for_approval(action: Mapping[str, Any]) -> bool:
    name = str(action.get("name", "ferramenta desconhecida"))
    arguments = action.get("arguments", action.get("args", {}))
    print(f"\nAprovação necessária para: {name}")
    print(json.dumps(arguments, ensure_ascii=False, indent=2, default=str))
    return input("Aprovar execução? [s/N] ").strip().lower() in {"s", "sim", "y", "yes"}


def _resume_after_human_review(
    graph: Any,
    result: dict[str, Any],
    config: dict[str, Any],
    approval_handler: ApprovalHandler,
) -> dict[str, Any]:
    """Resolve cada lote HITL e retoma o mesmo checkpoint até o grafo terminar."""

    while interrupts := result.get("__interrupt__"):
        value = interrupts[0].value
        actions = value.get("action_requests", []) if isinstance(value, Mapping) else []
        if not actions:
            raise RuntimeError("Interrupt recebido sem action_requests para revisão.")

        decisions: list[dict[str, str]] = []
        for action in actions:
            approved = approval_handler(action)
            if approved:
                decisions.append({"type": "approve"})
                continue

            name = str(action.get("name", "ferramenta"))
            decisions.append(
                {
                    "type": "reject",
                    "message": (
                        f"Um humano rejeitou a execução de {name}. "
                        "Não tente executar novamente sem uma nova solicitação."
                    ),
                }
            )

        result = graph.invoke(
            Command(resume={"decisions": decisions}),
            config=config,
        )

    return result


def run_agent(
    ticket_id: str,
    model: BaseChatModel | None = None,
    approval_handler: ApprovalHandler | None = None,
) -> AgentRun:
    graph = build_agent(model=model)
    config = {
        "configurable": {"thread_id": f"{ticket_id}:{uuid4().hex}"},
        "recursion_limit": settings.max_graph_steps,
    }

    try:
        result: dict[str, Any] = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Investigue {ticket_id}.",
                    }
                ]
            },
            config=config,
        )
        result = _resume_after_human_review(
            graph,
            result,
            config,
            approval_handler or _ask_for_approval,
        )
        diagnosis = result.get("structured_response")
        if diagnosis is None:
            diagnosis = _blocked(
                ticket_id,
                "O agente encerrou antes de produzir o diagnóstico estruturado",
            )
        elif not isinstance(diagnosis, TicketDiagnosis):
            diagnosis = TicketDiagnosis.model_validate(diagnosis)
    except GraphRecursionError:
        diagnosis = _blocked(ticket_id, "O agente atingiu o limite do grafo")
        snapshot = graph.get_state(config)
        result = dict(snapshot.values) if snapshot.values else {"messages": []}

    messages = list(result.get("messages", []))
    events, tools_used = summarize_messages(messages)
    trace = save_trace(settings.runs_dir, ticket_id, events)
    return AgentRun(diagnosis, tools_used, str(trace), messages)
