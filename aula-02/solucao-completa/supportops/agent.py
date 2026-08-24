from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_ollama import ChatOllama
from langgraph.errors import GraphRecursionError

from supportops.config import settings
from supportops.models import TicketDiagnosis
from supportops.tools import TOOLS
from supportops.tracing import save_trace, summarize_messages


SYSTEM_PROMPT = """
Você é um agente de investigação de incidentes de suporte técnico.

CONTRATO OPERACIONAL
- Use somente as tools fornecidas. Todas são somente leitura.
- Sempre consulte get_ticket_context antes de concluir qualquer diagnóstico.
- Use os IDs retornados pelo ticket; não invente IDs ou fatos.
- Colete evidências independentes: dados do ticket, acesso do usuário, mudança de role,
  saúde do serviço e runbook quando forem relevantes.
- Não repita a mesma tool com os mesmos argumentos.
- Não proponha que você executou ações de escrita. Se a correção exigir escrita,
  marque requires_human=true e status=needs_human.
- Pare quando houver evidência suficiente ou quando não houver progresso.
- Não exponha raciocínio interno. Produza apenas tool calls e o diagnóstico final estruturado.

CRITÉRIO DE QUALIDADE
O diagnóstico deve separar evidências observadas de hipótese. Uma causa provável sem
suporte nas tools deve ter confiança baixa ou ser marcada como evidência insuficiente.
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
        num_ctx=settings.num_ctx,
        validate_model_on_init=True,
    )


def build_agent():
    return create_agent(
        model=build_model(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(
            schema=TicketDiagnosis,
            handle_errors=(
                "Retorne exatamente um diagnóstico válido. Use somente evidências das tools "
                "e respeite os valores permitidos pelo schema."
            ),
        ),
        name="supportops_investigator",
    )


def run_agent(ticket_id: str) -> AgentRun:
    agent = build_agent()
    user_message = (
        f"Investigue o ticket {ticket_id}. Use as tools necessárias, evite chamadas "
        "redundantes e finalize com TicketDiagnosis. /no_think"
    )

    try:
        result: dict[str, Any] = agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            config={"recursion_limit": settings.max_graph_steps},
        )
    except GraphRecursionError as exc:
        raise RuntimeError(
            "O agente atingiu o limite de passos. Aumente AGENT_MAX_GRAPH_STEPS "
            "apenas para diagnóstico; o ideal é revisar prompt e tools."
        ) from exc

    diagnosis = result.get("structured_response")
    if not isinstance(diagnosis, TicketDiagnosis):
        diagnosis = TicketDiagnosis.model_validate(diagnosis)

    events, tools_used = summarize_messages(result.get("messages", []))
    trace_path = save_trace(settings.runs_dir, ticket_id, events)

    return AgentRun(
        diagnosis=diagnosis,
        tools_used=tools_used,
        trace_path=str(trace_path),
    )
