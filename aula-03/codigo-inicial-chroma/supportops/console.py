from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


@dataclass(frozen=True)
class UsageSummary:
    """Uso agregado de todas as chamadas ao modelo em uma execução."""

    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_source: str = "unavailable"
    duration_seconds: float = 0.0


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content) if content is not None else ""

    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, Mapping):
            text = block.get("text") or block.get("content")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def _reasoning_text(message: AIMessage) -> str:
    for key in ("reasoning_content", "reasoning", "thinking"):
        value = message.additional_kwargs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if isinstance(message.content, list):
        parts: list[str] = []
        for block in message.content:
            if not isinstance(block, Mapping):
                continue
            if block.get("type") not in {"reasoning", "thinking"}:
                continue
            text = block.get("text") or block.get("content")
            if isinstance(text, str):
                parts.append(text)
        return "\n".join(parts).strip()
    return ""


def _reasoning_detail(usage: Mapping[str, Any]) -> int | None:
    details = usage.get("output_token_details")
    if not isinstance(details, Mapping):
        return None
    for key in ("reasoning", "reasoning_tokens"):
        value = details.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _logprob_token(entry: Any) -> str | None:
    token = entry.get("token") if isinstance(entry, Mapping) else getattr(entry, "token", None)
    return token if isinstance(token, str) else None


def _reasoning_tokens_from_logprobs(message: AIMessage) -> int | None:
    """Conta o prefixo dos logprobs que corresponde exatamente ao trace visível."""

    reasoning = message.additional_kwargs.get("reasoning_content")
    logprobs = message.response_metadata.get("logprobs")
    if not isinstance(reasoning, str) or not reasoning:
        return None
    if not isinstance(logprobs, Sequence) or isinstance(logprobs, (str, bytes)):
        return None

    decoded = ""
    for index, entry in enumerate(logprobs, start=1):
        token = _logprob_token(entry)
        if token is None:
            return None
        decoded += token
        if decoded == reasoning:
            return index
        if not reasoning.startswith(decoded):
            return None
    return None


def collect_usage(messages: Sequence[BaseMessage]) -> UsageSummary:
    model_calls = input_tokens = output_tokens = total_tokens = 0
    provider_reasoning = trace_reasoning = 0
    provider_counts = trace_counts = 0
    duration_ns = 0

    for message in messages:
        if not isinstance(message, AIMessage):
            continue

        model_calls += 1
        usage = message.usage_metadata or {}
        input_tokens += _as_int(usage.get("input_tokens"))
        output_tokens += _as_int(usage.get("output_tokens"))
        total_tokens += _as_int(usage.get("total_tokens"))
        duration_ns += _as_int(message.response_metadata.get("total_duration"))

        exact_reasoning = _reasoning_detail(usage)
        if exact_reasoning is not None:
            provider_reasoning += exact_reasoning
            provider_counts += 1
            continue

        trace_count = _reasoning_tokens_from_logprobs(message)
        if trace_count is not None:
            trace_reasoning += trace_count
            trace_counts += 1

    if provider_counts == model_calls and model_calls:
        reasoning_tokens = provider_reasoning
        reasoning_source = "provider"
    elif provider_counts + trace_counts == model_calls and model_calls:
        reasoning_tokens = provider_reasoning + trace_reasoning
        reasoning_source = "mixed" if provider_counts else "trace_logprobs"
    else:
        reasoning_tokens = provider_reasoning + trace_reasoning
        reasoning_source = "partial" if reasoning_tokens else "unavailable"

    return UsageSummary(
        model_calls=model_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        reasoning_tokens=reasoning_tokens,
        reasoning_source=reasoning_source,
        duration_seconds=duration_ns / 1_000_000_000,
    )


def _number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _json_renderable(value: Any) -> Syntax | Text:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return Text(value)

    try:
        formatted = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    except (TypeError, ValueError):
        return Text(str(value))
    return Syntax(formatted, "json", word_wrap=True, background_color="default")


def _usage_panel(summary: UsageSummary) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(justify="right")
    table.add_row("Chamadas ao modelo", _number(summary.model_calls))
    table.add_row("Tokens de entrada", _number(summary.input_tokens))
    table.add_row("Tokens de saída (Ollama eval_count)", _number(summary.output_tokens))
    table.add_row("Tokens processados", _number(summary.total_tokens))

    reasoning_labels = {
        "provider": "Tokens de raciocínio (provedor)",
        "trace_logprobs": "Tokens do trace de raciocínio*",
        "mixed": "Tokens de raciocínio*",
        "partial": "Tokens de raciocínio identificados*",
        "unavailable": "Tokens de raciocínio",
    }
    reasoning_value = (
        _number(summary.reasoning_tokens)
        if summary.reasoning_source != "unavailable"
        else "não informado"
    )
    table.add_row(reasoning_labels[summary.reasoning_source], reasoning_value)
    if summary.duration_seconds:
        table.add_row("Tempo total do modelo", f"{summary.duration_seconds:.2f} s")

    notes: list[Text] = []
    if summary.reasoning_source in {"trace_logprobs", "mixed", "partial"}:
        notes.append(
            Text(
                "* Contagem do texto de raciocínio via logprobs. O Ollama "
                "informa apenas o total de saída.",
                style="dim",
            )
        )
    body = Group(table, *notes) if notes else table
    return Panel(body, title="Uso da execução", border_style="cyan")


def render_agent_result(
    result: Mapping[str, Any],
    ticket_id: str,
    *,
    structured_response: Mapping[str, Any] | None = None,
    console: Console | None = None,
) -> None:
    """Renderiza trace, tools, diagnóstico estruturado e uso da execução."""

    console = console or Console()
    messages = result.get("messages", [])
    if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes)):
        raise TypeError("O resultado do agente não contém uma lista de mensagens.")

    header = Group(
        Text("SupportOps Agent + Chroma", style="bold cyan"),
        Text.assemble(("Ticket: ", "bold"), (ticket_id, "white")),
    )
    console.print(Panel.fit(header, border_style="cyan"))

    final_message: AIMessage | None = None
    for message in reversed(messages):
        if isinstance(message, AIMessage) and _content_text(message.content).strip():
            final_message = message
            break

    model_call = 0
    tool_result = 0
    for message in messages:
        if isinstance(message, HumanMessage):
            continue

        if isinstance(message, AIMessage):
            model_call += 1
            reasoning = _reasoning_text(message)
            if reasoning:
                console.print(
                    Panel(
                        Text(reasoning),
                        title=f"Raciocínio · chamada {model_call}",
                        border_style="yellow",
                    )
                )

            if message.tool_calls:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Ferramenta", style="magenta", no_wrap=True)
                table.add_column("Argumentos")
                for tool_call in message.tool_calls:
                    name = str(tool_call.get("name", "ferramenta desconhecida"))
                    table.add_row(name, _json_renderable(tool_call.get("args", {})))
                console.print(
                    Panel(
                        table,
                        title=f"Ações · chamada {model_call}",
                        border_style="magenta",
                    )
                )

            content = _content_text(message.content).strip()
            if content and (structured_response is not None or message is not final_message):
                console.print(Panel(Markdown(content), title="Resposta intermediária"))
            continue

        if isinstance(message, ToolMessage):
            tool_result += 1
            name = message.name or "ferramenta"
            console.print(
                Panel(
                    _json_renderable(message.content),
                    title=f"Retorno {tool_result} · {escape(name)}",
                    border_style="green",
                )
            )

    if structured_response is not None:
        console.print(
            Panel(
                _json_renderable(structured_response),
                title="Diagnóstico final",
                border_style="bold green",
            )
        )
    elif final_message is not None:
        console.print(
            Panel(
                Markdown(_content_text(final_message.content).strip()),
                title="Diagnóstico final",
                border_style="bold green",
            )
        )
    else:
        console.print(
            Panel(
                Text("O agente terminou sem produzir uma resposta final."),
                title="Diagnóstico final",
                border_style="red",
            )
        )

    console.print(_usage_panel(collect_usage(messages)))
