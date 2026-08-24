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


def get_ticket(ticket_id: str) -> dict[str, Any]:
    tickets = _load_json("tickets.json")
    if ticket_id not in tickets:
        raise ValueError(f"Ticket inexistente: {ticket_id}")
    return tickets[ticket_id]


def get_user(user_id: str) -> dict[str, Any]:
    users = _load_json("users.json")
    if user_id not in users:
        raise ValueError(f"Usuário inexistente: {user_id}")
    return users[user_id]


def get_service(service_id: str) -> dict[str, Any]:
    services = _load_json("services.json")
    if service_id not in services:
        raise ValueError(f"Serviço inexistente: {service_id}")
    return services[service_id]


def search_runbooks(service_id: str, symptom: str, limit: int = 3) -> list[dict[str, Any]]:
    query_terms = {term.lower().strip(".,:;()[]") for term in symptom.split() if term.strip()}
    scored: list[tuple[int, dict[str, Any]]] = []

    for runbook in _load_json("runbooks.json"):
        if runbook["service_id"] != service_id:
            continue
        haystack = " ".join(
            [runbook["title"], runbook["content"], *runbook["keywords"]]
        ).lower()
        score = sum(1 for term in query_terms if term in haystack)
        if score > 0:
            scored.append((score, runbook))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [runbook for _, runbook in scored[:limit]]
