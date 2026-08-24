from supportops.agent import build_agent
from uuid import uuid4
from supportops.config import settings

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = build_agent()
ticket_id = "TEST"
# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in San Francisco?"}]},
    config = {
        "configurable": {"thread_id": f"{ticket_id}:{uuid4().hex}"},
        "recursion_limit": settings.max_graph_steps,
        "run_name": "Test_run_class",
        "tags": ["supportops", "qwen3-local"],
        "metadata": {"ticket_id": "TCK-4821"}
    }
)