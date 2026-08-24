from __future__ import annotations

import json

from langchain.tools import tool

from supportops import repository


def _json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


@tool

def get_ticket_context(ticket_id: str) -> str:
    """Consulte primeiro os dados completos de um ticket técnico pelo ID."""
    return _json(repository.get_ticket(ticket_id))


@tool

def get_user_access(user_id: str, resource: str) -> str:
    """Compare acesso autorizado e cache de roles de um usuário. Somente leitura."""
    user = repository.get_user(user_id)
    source_roles = user["roles_source_of_truth"]
    cached_roles = user["roles_in_permission_cache"]
    return _json(
        {
            "user_id": user_id,
            "resource": resource,
            "authorized_in_source_of_truth": resource in user["allowed_resources"],
            "roles_source_of_truth": source_roles,
            "roles_in_permission_cache": cached_roles,
            "cache_diverges_from_source": source_roles != cached_roles,
        }
    )


@tool

def get_recent_role_change(user_id: str) -> str:
    """Recupere a mudança de role mais recente de um usuário. Somente leitura."""
    user = repository.get_user(user_id)
    return _json(
        {
            "user_id": user_id,
            "last_role_change": user.get("last_role_change"),
        }
    )


@tool

def get_service_health(service_id: str) -> str:
    """Consulte saúde, taxa de erro, latência p95 e último deploy de um serviço."""
    return _json(repository.get_service(service_id))


@tool

def search_service_runbook(service_id: str, symptom: str) -> str:
    """Busque runbooks do serviço por sintomas, erros ou termos técnicos."""
    results = repository.search_runbooks(service_id, symptom, limit=3)
    return _json(
        {
            "service_id": service_id,
            "query": symptom,
            "results": results,
            "count": len(results),
        }
    )


TOOLS = [
    get_ticket_context,
    get_user_access,
    get_recent_role_change,
    get_service_health,
    search_service_runbook,
]
