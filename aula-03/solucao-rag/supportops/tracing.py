from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
from langchain_core.messages import AIMessage, ToolMessage


def summarize_messages(messages: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    events, tools_used = [], []
    for index, message in enumerate(messages):
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                name = call.get("name", "unknown")
                tools_used.append(name)
                events.append({"step":index,"type":"tool_call","tool":name,"args":call.get("args", {})})
        elif isinstance(message, ToolMessage):
            content = str(message.content)
            events.append({"step":index,"type":"tool_result","tool":message.name,"status":getattr(message,"status",None),"content":content[:1800]})
    return events, list(dict.fromkeys(tools_used))


def save_trace(runs_dir: Path, ticket_id: str, events: list[dict[str, Any]]) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid4().hex[:12]
    path = runs_dir / f"{ticket_id}_{run_id}.json"
    path.write_text(json.dumps({"run_id":run_id,"ticket_id":ticket_id,"created_at":datetime.now(timezone.utc).isoformat(),"events":events}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
