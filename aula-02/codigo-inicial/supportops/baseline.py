from __future__ import annotations

import argparse

from supportops.agent import build_model
from supportops.tools import TOOLS

def main() -> None:
    # parser = argparse.ArgumentParser(
    #     description="Baseline sem tools: demonstra por que o agente precisa de dados externos."
    # )
    # parser.add_argument("ticket_id", nargs="?", default="TCK-4821")
    # args = parser.parse_args()

    # model = build_model()
    # response = model.invoke(
    #     f"Analise o ticket {args.ticket_id} e diga a causa do problema."
    # )
    # print(response.content)
    model = build_model().bind_tools(TOOLS)
    response = model.invoke(
        "O que fazer quando há divergencia entre roles em estados diferentes para o mesmo usuário?"
        # "Que dia eh hoje."
    )
    reasoning = response.additional_kwargs.get("reasoning_content", "")
    print(reasoning)
    print(response)

if __name__ == "__main__":
    main()
