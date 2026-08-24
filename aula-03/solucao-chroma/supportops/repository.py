from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _mapping(filename: str, item_id: str, label: str) -> dict[str, Any]:
    data = _load(filename)
    if item_id not in data:
        raise ValueError(f"{label} inexistente: {item_id}")
    return data[item_id]


def get_ticket(ticket_id: str) -> dict[str, Any]:
    return _mapping("tickets.json", ticket_id, "Ticket")


def get_user(user_id: str) -> dict[str, Any]:
    return _mapping("users.json", user_id, "Usuário")


def get_service(service_id: str) -> dict[str, Any]:
    return _mapping("services.json", service_id, "Serviço")


def recent_items(filename: str, service_id: str, environment: str, date_field: str, limit: int) -> list[dict[str, Any]]:
    rows = [
        row for row in _load(filename)
        if row["service_id"] == service_id and row["environment"] == environment
    ]
    rows.sort(key=lambda row: row[date_field], reverse=True)
    return rows[:limit]


def get_recent_incidents(service_id: str, environment: str, limit: int = 5) -> list[dict[str, Any]]:
    return recent_items("incidents.json", service_id, environment, "started_at", limit)


def get_recent_deployments(service_id: str, environment: str, limit: int = 5) -> list[dict[str, Any]]:
    return recent_items("deployments.json", service_id, environment, "deployed_at", limit)


def get_metric_snapshot(service_id: str, environment: str) -> dict[str, Any]:
    key = f"{service_id}:{environment}"
    return _mapping("metrics.json", key, "Métrica")


def get_audit_events(subject_id: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = [row for row in _load("audit_events.json") if row["subject_id"] == subject_id]
    rows.sort(key=lambda row: row["timestamp"], reverse=True)
    return rows[:limit]
