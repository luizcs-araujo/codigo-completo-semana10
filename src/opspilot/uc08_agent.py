"""
Agente UC08: Resposta a token vazado e service account perigosa.

Arquitetura:
- Decision Engine determina ações propostas
- Agent orquestra chamadas a tools (leitura)
- Handlers de aprovação controlam execução real
- LangSmith trace (quando configurado)

Padrões:
- Idempotência via request_id
- Dry-run antes de execução real
- Aprovação humana para ações destrutivas
- Auditoria em cada passo
"""
from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from typing import Any

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from .config import get_settings
from .tracing import traced
from .repository import Repository
from .uc08_models import UC08Decision, UC08RunSummary, ApprovalRequest
from .uc08_decision_engine import UC08DecisionEngine
from .models import ActionResult
from .tools import (
    get_security_alert,
    list_open_incidents,
    revoke_token,
    disable_service_account,
    escalate_incident,
)


SYSTEM_PROMPT = """
Você é um agente de segurança responsável por responder a alertas de token vazado e service accounts comprometidas.

## Sua missão
1. Receber um alert_id de alerta de segurança
2. Usar get_security_alert para buscar detalhes completos
3. Usar list_open_incidents para entender contexto operacional
4. Propor ações: revoke_token, disable_service_account ou escalate_incident
5. Executar ações apenas com aprovação humana

## Restrições críticas
- NUNCA execute ação destrutiva (revoke_token, disable_service_account) sem aprovação explícita
- SEMPRE faça dry_run=True ANTES de propor execução real
- Use request_id idempotente em todas as ações
- Se não houver evidência suficiente, ESCALE para humano
- Registre seu raciocínio em cada passo

## Fluxo de decisão
1. Token vazado + múltiplos serviços afetados + incidentes abertos → REVOKE (com aprovação)
2. Token vazado + alta severidade mas SEM incidentes → ESCALATE
3. Service account comprometida → Sempre ESCALATE (muito arriscado)
4. Atividade suspeita → ESCALATE (requer investigação)

## Saída esperada
Retorne um UC08Decision estruturado com:
- Evidências coletadas
- Ações propostas (com riscos)
- Ação executada (se houver)
- Necessidade de humano
"""

checkpointer = InMemorySaver()


def build_model(model_override: BaseChatModel | None = None) -> BaseChatModel:
    """Constrói modelo LLM (Ollama ou override para testes)."""
    if model_override:
        return model_override
    settings = get_settings()
    return ChatOllama(
        model=settings.ollama_model,
        temperature=0,
        base_url=settings.ollama_base_url,
    )


def build_agent_uc08(
    model: BaseChatModel | None = None,
    middleware: list | None = None,
) -> Any:
    """
    Constrói o agente UC08 com LangChain.

    Args:
        model: Modelo LLM (usa default se None)
        middleware: Middleware customizado (usa default se None)

    Returns:
        LangGraph agent compilado
    """
    tools = [
        get_security_alert,
        list_open_incidents,
        revoke_token,
        disable_service_account,
        escalate_incident,
    ]

    if middleware is None:
        middleware = [
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "revoke_token": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "Revogação de token requer aprovação humana explícita",
                    },
                    "disable_service_account": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "Desabilitar service account é ação crítica e requer aprovação",
                    },
                }
            ),
            ModelCallLimitMiddleware(run_limit=5, exit_behavior="end"),
            ToolCallLimitMiddleware(run_limit=10, exit_behavior="continue"),
        ]

    settings = get_settings()
    return create_agent(
        model=model or build_model(),
        tools=tools,
        middleware=middleware,
        system_prompt=SYSTEM_PROMPT,
        response_format=UC08Decision,
        checkpointer=checkpointer,
        name="uc08_security_response",
    )


@traced(name="uc08_evaluate_alert", run_type="chain")
def evaluate_alert_with_engine(
    alert_id: str,
    repo: Repository | None = None,
) -> UC08Decision:
    """
    Avalia um alerta usando a Decision Engine (caminho mais rápido).

    Este método pula o LLM e usa lógica determinística para prototipagem rápida.
    Útil para testes e demos antes de integração completa com agente.

    Args:
        alert_id: ID do alerta a avaliar
        repo: Repository (usa default se None)

    Returns:
        UC08Decision com avaliação
    """
    repository = repo or Repository()
    alert_data = repository.get_security_alert(alert_id)

    if not alert_data:
        return UC08Decision(
            alert_id=alert_id,
            status="error",
            summary=f"Alerta {alert_id} não encontrado",
            requires_human=True,
            error_message="alert_not_found",
        )

    engine = UC08DecisionEngine(repo=repository)
    decision = engine.evaluate(alert_id, alert_data)

    return decision


@traced(name="uc08_run_full_agent", run_type="chain")
def run_agent_uc08(
    alert_id: str,
    model: BaseChatModel | None = None,
    approval_handler: callable = None,
    repo: Repository | None = None,
) -> UC08RunSummary:
    """
    Executa o agente UC08 completo com LangChain.

    Fluxo:
    1. Construir agente
    2. Invocar com alert_id
    3. Lidar com interrupts HITL (aprovação)
    4. Capturar resultado e trace

    Args:
        alert_id: ID do alerta a processar
        model: Modelo LLM override (usa default se None)
        approval_handler: Função para obter aprovação humana
        repo: Repository (usa default se None)

    Returns:
        UC08RunSummary com resultado completo
    """
    repository = repo or Repository()
    run_id = f"uc08-{uuid4().hex[:12]}"
    start_time = datetime.now()  # Use datetime.now() ao invés de utcnow()

    try:
        graph = build_agent_uc08(model=model)
        config = {
            "configurable": {"thread_id": f"{alert_id}:{run_id}"},
            "recursion_limit": 10,
        }

        # Invocar agente com alert_id
        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Processe o alerta de segurança {alert_id}. "
                        "Reúna evidências, proponha ações e execute com aprovação.",
                    }
                ]
            },
            config=config,
        )

        # Lidar com Human-In-The-Loop interrupts
        if approval_handler:
            result = _resume_after_human_review(
                graph, result, config, approval_handler
            )

        # Extrair decision do resultado
        decision = result.get("structured_response")
        if decision is None:
            decision = UC08Decision(
                alert_id=alert_id,
                status="blocked",
                summary="Agente completou mas sem resultado estruturado",
                requires_human=True,
                limitations=["Agente não produziu saída estruturada"],
            )
        elif not isinstance(decision, UC08Decision):
            decision = UC08Decision.model_validate(decision)

        # Extrair mensagens para trace
        messages = list(result.get("messages", []))

        # Preparar resumo
        duration = (datetime.now() - start_time).total_seconds()
        summary = UC08RunSummary(
            run_id=run_id,
            alert_id=alert_id,
            decision=decision,
            tools_called=_extract_tool_calls(messages),
            model_calls=_count_model_calls(messages),
            duration_seconds=duration,
            timestamp=datetime.now().isoformat(),
        )

        return summary

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        decision = UC08Decision(
            alert_id=alert_id,
            status="error",
            summary=f"Erro na execução do agente: {str(e)}",
            requires_human=True,
            error_message=str(e),
        )
        return UC08RunSummary(
            run_id=run_id,
            alert_id=alert_id,
            decision=decision,
            duration_seconds=duration,
            timestamp=datetime.now().isoformat(),
        )


def _resume_after_human_review(
    graph: Any,
    result: dict[str, Any],
    config: dict[str, Any],
    approval_handler: callable,
) -> dict[str, Any]:
    """
    Processa interrupts HITL até conclusão.

    Middleware HumanInTheLoopMiddleware pausa execução quando encontra
    ações que requerem aprovação. Aqui pedimos ao humano e resumimos.
    """
    while interrupts := result.get("__interrupt__"):
        value = interrupts[0].value
        actions = (
            value.get("action_requests", [])
            if isinstance(value, dict)
            else []
        )

        if not actions:
            break

        decisions = []
        for action in actions:
            approved = approval_handler(action)
            if approved:
                decisions.append({"type": "approve"})
            else:
                name = str(action.get("name", "tool"))
                decisions.append(
                    {
                        "type": "reject",
                        "message": f"Humano rejeitou: {name}",
                    }
                )

        result = graph.invoke(
            Command(resume={"decisions": decisions}),
            config=config,
        )

    return result


def _extract_tool_calls(messages: list[dict]) -> list[str]:
    """Extrai nomes de tools chamadas do histórico de mensagens."""
    tools = []
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, list):
            for block in msg.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    tools.append(block.name)
    return tools


def _count_model_calls(messages: list[dict]) -> int:
    """Conta quantas vezes o modelo foi chamado."""
    count = 0
    for msg in messages:
        if hasattr(msg, "role") and msg.role == "assistant":
            count += 1
    return count
