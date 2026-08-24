from __future__ import annotations

import argparse

from supportops.agent import run_agent
from supportops.console import render_agent_result


def main() -> None:
    parser = argparse.ArgumentParser(description="SupportOps Agent")
    parser.add_argument("ticket_id", nargs="?", default="TCK-4821")
    args = parser.parse_args()

    result = run_agent(args.ticket_id)
    render_agent_result(result, ticket_id=args.ticket_id)


if __name__ == "__main__":
    main()
