from __future__ import annotations

import json
from langchain.tools import tool
from supportops import repository
from supportops.rag_tools import search_technical_docs


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


@tool
def get_ticket_context(ticket_id: str) -> str:
    """Consulte primeiro os dados completos de um ticket técnico pelo ID."""
    return _json(repository.get_ticket(ticket_id))


@tool
def get_user_access(user_id: str, resource: str) -> str:
    """Compare acesso autorizado e cache de roles de um usuário. Somente leitura."""
    user = repository.get_user(user_id)
    return _json({
        "user_id": user_id,
        "resource": resource,
        "authorized_in_source_of_truth": resource in user["allowed_resources"],
        "roles_source_of_truth": user["roles_source_of_truth"],
        "roles_in_permission_cache": user["roles_in_permission_cache"],
        "cache_diverges_from_source": user["roles_source_of_truth"] != user["roles_in_permission_cache"],
        "last_role_change": user.get("last_role_change"),
    })


@tool
def get_service_health(service_id: str) -> str:
    """Consulte status básico e configuração operacional de um serviço."""
    return _json(repository.get_service(service_id))


@tool
def get_metric_snapshot(service_id: str, environment: str) -> str:
    """Consulte erro, latência, saturação e tráfego atuais de um serviço."""
    return _json(repository.get_metric_snapshot(service_id, environment))


@tool
def get_recent_incidents(service_id: str, environment: str, limit: int = 3) -> str:
    """Busque incidentes recentes do mesmo serviço e ambiente."""
    return _json(repository.get_recent_incidents(service_id, environment, limit))


@tool
def get_recent_deployments(service_id: str, environment: str, limit: int = 3) -> str:
    """Busque deploys recentes do mesmo serviço e ambiente."""
    return _json(repository.get_recent_deployments(service_id, environment, limit))


@tool
def get_audit_events(subject_id: str, limit: int = 8) -> str:
    """Consulte eventos de auditoria recentes de um usuário, mudança ou recurso."""
    return _json(repository.get_audit_events(subject_id, limit))


TOOLS = [
    get_ticket_context,
    get_user_access,
    get_service_health,
    get_metric_snapshot,
    get_recent_incidents,
    get_recent_deployments,
    get_audit_events,
    search_technical_docs,
]
