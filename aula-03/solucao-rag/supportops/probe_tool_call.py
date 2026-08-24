from __future__ import annotations

from langchain_core.messages import AIMessage

from supportops.agent import build_model
from supportops.tools import TOOLS


def main() -> None:
    model_with_tools = build_model().bind_tools(TOOLS)
    response = model_with_tools.invoke(
        "Descubra o que aconteceu no ticket TCK-4821. Comece consultando o ticket. /no_think"
    )
    if isinstance(response, AIMessage) and response.tool_calls:
        print(response.tool_calls)
    else:
        print("O modelo não emitiu tool call:", response.content)


if __name__ == "__main__":
    main()
