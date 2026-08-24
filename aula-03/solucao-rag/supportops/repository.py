from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _by_id(filename: str, item_id: str, label: str) -> dict[str, Any]:
    data = _load_json(filename)
    if item_id not in data:
        raise ValueError(f"{label} inexistente: {item_id}")
    return data[item_id]


def get_ticket(ticket_id: str) -> dict[str, Any]:
    return _by_id("tickets.json", ticket_id, "Ticket")


def get_user(user_id: str) -> dict[str, Any]:
    return _by_id("users.json", user_id, "Usuário")


def get_service(service_id: str) -> dict[str, Any]:
    return _by_id("services.json", service_id, "Serviço")


def get_recent_incidents(service_id: str, environment: str, limit: int = 5) -> list[dict[str, Any]]:
    matches = [i for i in _load_json("incidents.json") if i["service_id"] == service_id and i["environment"] == environment]
    matches.sort(key=lambda item: item["started_at"], reverse=True)
    return matches[:limit]


def get_recent_deployments(service_id: str, environment: str, limit: int = 5) -> list[dict[str, Any]]:
    matches = [d for d in _load_json("deployments.json") if d["service_id"] == service_id and d["environment"] == environment]
    matches.sort(key=lambda item: item["deployed_at"], reverse=True)
    return matches[:limit]
