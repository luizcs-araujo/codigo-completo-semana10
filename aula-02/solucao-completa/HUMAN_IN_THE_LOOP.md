# Human approval for sensitive tool execution

Prompt instructions alone cannot guarantee that an agent will wait for permission before executing a tool. Prompts influence model behavior, but they do not enforce an execution boundary.

This project uses LangChain 1.x, which provides `HumanInTheLoopMiddleware`. The middleware intercepts selected tool calls after the model proposes them but before the underlying Python function executes. The graph pauses until a human approves or rejects the request.

## Target tool

The sensitive operation in this project is:

```python
@tool
def invalidate_permission_cache(user_id: str) -> str:
    """Invalidate cached role data for a user."""
    return "Cache invalidated."
```

Read-only tools can continue automatically, while `invalidate_permission_cache` requires explicit approval.

## Configure the approval middleware

Update `supportops/agent.py` to configure the middleware and a checkpointer:

```python
from __future__ import annotations

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from supportops.config import settings
from supportops.tools import TOOLS


checkpointer = InMemorySaver()


def build_agent():
    return create_agent(
        model=build_model(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "invalidate_permission_cache": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": (
                            "Invalidating the permission cache requires "
                            "explicit human approval."
                        ),
                    }
                }
            )
        ],
        checkpointer=checkpointer,
        name="support agent",
    )
```

The key in `interrupt_on` must match the tool name. Functions decorated with `@tool` use their function name by default.

Tools not listed in `interrupt_on` are automatically allowed. They do not need entries with `False` unless making that policy explicit improves readability.

## Run until approval is required

An agent using human-in-the-loop execution must receive a stable thread ID. LangGraph uses it to associate the paused execution with its checkpoint.

```python
from langgraph.types import Command


agent = build_agent()

config = {
    "configurable": {"thread_id": ticket_id},
    "recursion_limit": settings.max_graph_steps,
}

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": f"This is the target ticket: {ticket_id}.",
            }
        ]
    },
    config=config,
    version="v2",
)
```

If the agent only uses read-only tools, it can finish normally. If it proposes `invalidate_permission_cache`, `result.interrupts` contains the pending request, and the tool has not yet run.

## Present the decision to a human

For a command-line interface, the pending tool and arguments can be displayed before asking for approval:

```python
if result.interrupts:
    request = result.interrupts[0].value["action_requests"][0]

    print(f"Requested tool: {request['name']}")
    print(f"Arguments: {request['arguments']}")

    approved = input("Approve execution? [y/N] ").strip().lower() == "y"

    if approved:
        decision = {"type": "approve"}
    else:
        decision = {
            "type": "reject",
            "message": (
                "A human rejected cache invalidation. "
                "Do not retry this action."
            ),
        }
```

The same decision could instead come from a web interface, approval queue, support dashboard, or another authorized human-review system.

## Resume the paused agent

Resume with a LangGraph `Command`, using the same agent/checkpointer and thread configuration:

```python
result = agent.invoke(
    Command(resume={"decisions": [decision]}),
    config=config,
    version="v2",
)

final_state = result.value
```

An `approve` decision executes the original tool call. A `reject` decision skips the tool and returns the rejection message to the model as feedback.

If the model proposes the sensitive tool again after rejection, the middleware creates another interrupt. The tool still cannot execute without approval.

## Execution flow

```text
Model proposes a tool call
          |
          v
Is the tool protected by interrupt_on?
          |
     +----+----+
     |         |
    No        Yes
     |         |
     v         v
Execute     Pause graph
tool        and save state
                 |
                 v
          Human reviews request
                 |
          +------+------+
          |             |
       Approve        Reject
          |             |
          v             v
       Execute       Skip tool and
       tool          return feedback
```

## Important considerations

- Keep prompt instructions describing when approval is appropriate, but treat the middleware as the enforcement mechanism.
- Show the reviewer the tool name and complete arguments before accepting a decision.
- Use `approve` and `reject` for a side-effecting operation. Editing arguments can be enabled with `"edit"` when the workflow genuinely needs it.
- The number and order of decisions must match the pending action requests when the model proposes multiple protected tools at once.
- `InMemorySaver` is suitable for local development and CLI demonstrations only.
- In production, use a persistent checkpointer such as PostgreSQL so a pending approval survives restarts or deployment changes.
- Store the reviewer identity, timestamp, original arguments, decision, and rejection reason in an audit log for production operations.
- Do not perform the real side effect anywhere before the protected tool function. The approval boundary only guards execution routed through the agent middleware.

## Limiting agent execution steps

The `recursion_limit` passed to `agent.invoke()` is a hard safety limit for the underlying LangGraph execution. It is intended to prevent an incorrectly routed or cyclic graph from running indefinitely.

When LangGraph exhausts this budget before reaching a normal end state, it raises `GraphRecursionError`. It does not ask the model to produce a final answer or return a partially completed result. An exception at this point is therefore expected behavior.

```python
return agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": f"This is the target ticket: {ticket_id}.",
            }
        ]
    },
    config={
        "recursion_limit": settings.max_graph_steps,
    },
)
```

### What counts as a step

A graph step is a LangGraph super-step, not necessarily one complete agent action or one tool call. A normal tool-using agent can alternate between graph nodes several times:

```text
Model node -> Tools node -> Model node -> Tools node -> Model node
```

Consequently, setting `recursion_limit` to a very small value can interrupt a healthy execution before the agent has a chance to form its final response.

### Recommended graceful limit

If the goal is to restrict how many times the model can be called during one run, use `ModelCallLimitMiddleware`. Its `exit_behavior="end"` option ends the agent normally and adds an explanatory AI message instead of raising an exception.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware


def build_agent():
    return create_agent(
        model=build_model(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=5,
                exit_behavior="end",
            ),
        ],
        name="support agent",
    )
```

The two limits can be used together:

- `ModelCallLimitMiddleware` provides the normal, user-facing execution limit.
- `recursion_limit` remains a more generous last-resort safeguard against graph loops.

For example, the agent could allow up to five model calls while retaining a graph recursion limit of 50.

### Limiting tool calls

If the real requirement is to limit tool use rather than model calls, use `ToolCallLimitMiddleware`:

```python
from langchain.agents.middleware import ToolCallLimitMiddleware


ToolCallLimitMiddleware(
    run_limit=8,
    exit_behavior="continue",
)
```

The available tool-limit exit behaviors are:

- `"continue"`: block calls beyond the limit with error messages and allow the model to continue.
- `"error"`: raise `ToolCallLimitExceededError` immediately.
- `"end"`: stop immediately with tool and AI messages; this is intended for single-tool-call scenarios and has restrictions when parallel calls are pending.

A tool-specific limit can be applied with `tool_name`:

```python
ToolCallLimitMiddleware(
    tool_name="search_service_runbook",
    run_limit=3,
    exit_behavior="continue",
)
```

### Handling the hard limit at the application boundary

The application can catch `GraphRecursionError` and return a controlled error message:

```python
from langchain.messages import AIMessage
from langgraph.errors import GraphRecursionError


def run_agent(ticket_id: str):
    agent = build_agent()

    try:
        return agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"This is the target ticket: {ticket_id}.",
                    }
                ]
            },
            config={
                "recursion_limit": settings.max_graph_steps,
            },
        )
    except GraphRecursionError:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "Execution stopped because the maximum graph-step "
                        "limit was reached before the analysis completed."
                    )
                )
            ]
        }
```

This makes the failure friendly to the caller, but it does not produce a genuine summary of the work completed before the exception. Producing a best-effort partial result requires proactively routing the graph to a finalization node before the hard limit is exhausted, or preserving intermediate state through checkpointing or streaming.

### Choosing the correct mechanism

| Requirement | Mechanism |
| --- | --- |
| Prevent an accidental infinite graph loop | `recursion_limit` |
| Gracefully limit model invocations or cost | `ModelCallLimitMiddleware` with `exit_behavior="end"` |
| Restrict all tool calls during a run | `ToolCallLimitMiddleware` |
| Restrict one particular tool | `ToolCallLimitMiddleware(tool_name=...)` |
| Display a friendly message after hard-limit failure | Catch `GraphRecursionError` |

## References

- [LangChain human-in-the-loop guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [HumanInTheLoopMiddleware API reference](https://reference.langchain.com/python/langchain/agents/middleware/human_in_the_loop/HumanInTheLoopMiddleware)
- [LangGraph recursion-limit error guide](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT)
- [LangGraph graph API: recursion limits](https://docs.langchain.com/oss/python/langgraph/graph-api#recursion-limit)
- [LangChain model and tool call limit middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#model-call-limit)
