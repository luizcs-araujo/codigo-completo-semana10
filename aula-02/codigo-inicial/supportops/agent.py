from __future__ import annotations

from langchain_ollama import ChatOllama
from langchain.agents.middleware import HumanInTheLoopMiddleware, ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain.agents import create_agent
from supportops.config import settings
from supportops.tools import TOOLS


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
""".strip()

checkpointer = InMemorySaver()

# """
# Você vai receber um ID referente a um ticket técnico. Ele pode ter diversas naturezas e seu dever é interpretá-lo e decidir qual o melhor caminho.
# Para isso, seu primeiro passo é escrever um plano de ação.
# Feito isso, siga-o a risca, mantendo registro do passo atual para continuar seguindo com o processamento do ticket.
# Tenha em mente, que algumas ações podem e devem causar o direcionamento a um humano. Nesses casos, deixe explicita a limitação quanto a isso para sua resposta final.
# """.strip()


def build_model() -> ChatOllama:
    return ChatOllama(
        model=settings.model,
        base_url=settings.base_url,
        temperature=0,
        num_ctx=settings.num_ctx,
        # Ollama returns Qwen's thinking in a separate field. ChatOllama only
        # keeps that field in ``reasoning_content`` when reasoning is explicit.
        reasoning=True,
        # Besides being useful for inspection, logprobs let the console count
        # the tokens in the visible reasoning trace. Ollama itself only reports
        # one combined output-token total (``eval_count``).
        logprobs=True,
        validate_model_on_init=True,
    )


def build_agent():
    return create_agent(
        model=build_model(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="support agent",
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "invalidate_permission_cache": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "Invalidating the permission cache requires explicit human approval."
                    }
                }
            ),
            ModelCallLimitMiddleware(
                run_limit=settings.max_graph_steps,
                exit_behavior='end'
            ),
            ToolCallLimitMiddleware(
                run_limit=8,
                exit_behavior='continue'
            )
        ],
        checkpointer=checkpointer
    )


def run_agent(ticket_id: str):
    agent = build_agent()
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"This is the target ticket: {ticket_id}."
                }
            ]
        },
        config={
            "configurable": {"thread_id": ticket_id}
        }
    )
    
    if result.get("__interrupt__", None):
        request = result["__interrupt__"][0].value["action_requests"][0]

        approved = input("Approve execution? [y/N]").strip().lower() == 'y'

        if approved:
            decision = {"type": "approve"}
        else:
            decision = {
                "type": "reject",
                "message": "A human rejected cache invalidation. Do not retry this action."
            }

        result = agent.invoke(
            Command(resume={"decisions": [decision]}),
            config={
            "configurable": {"thread_id": ticket_id}
        }
        )

        return result
        