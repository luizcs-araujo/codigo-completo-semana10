from io import StringIO

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from rich.console import Console

from supportops.console import collect_usage, render_agent_result


def _sample_messages():
    return [
        HumanMessage(content="Investigue o ticket TCK-4821."),
        AIMessage(
            content="",
            additional_kwargs={"reasoning_content": "Vou consultar o ticket."},
            tool_calls=[
                {
                    "name": "get_ticket_context",
                    "args": {"ticket_id": "TCK-4821"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 8,
                "total_tokens": 18,
            },
            response_metadata={
                "logprobs": [
                    {"token": "Vou"},
                    {"token": " consultar"},
                    {"token": " o"},
                    {"token": " ticket"},
                    {"token": "."},
                ],
                "total_duration": 1_500_000_000,
            },
        ),
        ToolMessage(
            content='{"ticket_id": "TCK-4821", "error_code": 403}',
            tool_call_id="call-1",
            name="get_ticket_context",
        ),
        AIMessage(
            content="O ticket falha com erro 403.",
            additional_kwargs={"reasoning_content": "Já tenho evidência suficiente."},
            usage_metadata={
                "input_tokens": 20,
                "output_tokens": 10,
                "total_tokens": 30,
            },
            response_metadata={
                "logprobs": [
                    {"token": "Já"},
                    {"token": " tenho"},
                    {"token": " evidência"},
                    {"token": " suficiente"},
                    {"token": "."},
                    {"token": "O"},
                ],
                "total_duration": 500_000_000,
            },
        ),
    ]


def test_collect_usage_counts_reasoning_trace_tokens():
    usage = collect_usage(_sample_messages())

    assert usage.model_calls == 2
    assert usage.input_tokens == 30
    assert usage.output_tokens == 18
    assert usage.total_tokens == 48
    assert usage.reasoning_tokens == 10
    assert usage.reasoning_source == "trace_logprobs"
    assert usage.duration_seconds == 2.0


def test_render_agent_result_has_readable_sections():
    output = StringIO()
    console = Console(file=output, color_system=None, width=120)

    render_agent_result(
        {"messages": _sample_messages()},
        ticket_id="TCK-4821",
        console=console,
    )

    rendered = output.getvalue()
    assert "Raciocínio · chamada 1" in rendered
    assert "get_ticket_context" in rendered
    assert '"error_code": 403' in rendered
    assert "Diagnóstico final" in rendered
    assert "Tokens do trace de raciocínio" in rendered
    assert "O ticket falha com erro 403." in rendered


def test_collect_usage_prefers_provider_reasoning_breakdown():
    message = AIMessage(
        content="Pronto.",
        usage_metadata={
            "input_tokens": 5,
            "output_tokens": 7,
            "total_tokens": 12,
            "output_token_details": {"reasoning": 4},
        },
    )

    usage = collect_usage([message])

    assert usage.reasoning_tokens == 4
    assert usage.reasoning_source == "provider"
