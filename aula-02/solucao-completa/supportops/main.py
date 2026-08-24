from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.panel import Panel

from supportops.agent import run_agent


console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="SupportOps Agent")
    parser.add_argument("ticket_id", nargs="?", default="TCK-4821")
    parser.add_argument("--json", action="store_true", help="Exibe somente JSON")
    args = parser.parse_args()

    try:
        run = run_agent(args.ticket_id)
    except Exception as exc:
        console.print(f"[bold red]Falha:[/bold red] {exc}")
        raise SystemExit(1) from exc

    payload = run.diagnosis.model_dump()
    payload["tools_used"] = run.tools_used
    payload["trace_path"] = run.trace_path

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    console.print(Panel.fit(f"[bold]Ticket {args.ticket_id}[/bold]", title="SupportOps"))
    console.print_json(data=payload)


if __name__ == "__main__":
    main()
