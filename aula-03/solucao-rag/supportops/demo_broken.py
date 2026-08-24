from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from supportops.rag.naive import naive_search

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demonstração propositalmente defeituosa"
    )
    parser.add_argument(
        "--query", default="erro 403 role dashboard cache analytics-api"
    )
    args = parser.parse_args()
    results = naive_search(args.query)
    console.print(
        Panel(
            "Busca por documento inteiro, sem filtros, sem versão e sem ambiente.",
            title="RAG quebrado",
        )
    )
    for index, item in enumerate(results, 1):
        status = "ATUAL" if item["is_current"] else "OBSOLETO"
        console.print(
            f"{index}. [{status}] {item['title']} — "
            f"{item['source']} v{item['version']}"
        )
    top = results[0]
    if not top["is_current"]:
        console.print(
            "\n[bold red]Falha reproduzida:[/bold red] o primeiro resultado "
            "é obsoleto e recomenda ação insegura."
        )
    console.print("\n[bold yellow]Loop sem progresso:[/bold yellow]")
    for step in range(1, 4):
        console.print(
            f"step {step}: search(query={args.query!r}) → "
            f"mesmo documento {top['source']}"
        )
    console.print(
        "Resultado: três chamadas, nenhuma evidência nova e nenhum critério de parada."
    )


if __name__ == "__main__":
    main()
