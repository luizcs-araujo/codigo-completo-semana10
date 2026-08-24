from __future__ import annotations

import argparse
import json

from rich.console import Console

from supportops.agent import run_agent
from supportops.console import render_agent_result

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="SupportOps Agent — Aula 3 com Chroma")
    parser.add_argument("ticket_id", nargs="?", default="TCK-4821")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        run = run_agent(args.ticket_id)
    except Exception as exc:
        console.print(f"[bold red]Falha:[/bold red] {exc}")
        raise SystemExit(1) from exc

    payload = run.diagnosis.model_dump()
    payload.update({"tools_used": run.tools_used, "trace_path": run.trace_path})
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    render_agent_result(
        {"messages": run.messages},
        ticket_id=args.ticket_id,
        structured_response=payload,
        console=console,
    )


if __name__ == "__main__":
    main()
