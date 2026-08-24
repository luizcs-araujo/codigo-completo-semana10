from __future__ import annotations

import json

from langchain.tools import tool

from supportops import repository


@tool
def get_ticket_context(ticket_id: str) -> str:
    """Consulte primeiro os dados completos de um ticket técnico pelo ID."""
    try:
        return json.dumps(repository.get_ticket(ticket_id), ensure_ascii=False)
    except Exception as e:
        return e

@tool
def get_user_access(user_id: str, resource: str) -> str:
    """"
    Compare acesso escrito para o usuário de acordo com sua role no source of truth e a role dentro do cache.
    Também verifica se a resource alvo está dentro da lista de resources permitidas para este usuário.
    """
    try:
        user = repository.get_user(user_id)
        return json.dumps(
            {
                "user_id": user_id,
                "resource": resource,
                "authorized_in_source_of_truth": resource in user["allowed_resources"],
                "roles_source_of_truth": user["roles_source_of_truth"],
                "cache_diverges_from_truth": user["roles_source_of_truth"] != user["roles_in_permission_cache"]
            }, ensure_ascii=False)
    except Exception as e:
        return e

@tool
def get_recent_role_change(user_id: str) -> str:
    """"
    Verifica se o usuário teve ou não uma mudança nas suas roles recentemente.
    """
    try:
        user = repository.get_user(user_id)
        return json.dumps(
            {
                "user_id": user_id,
                "role_recently_changed": user["last_role_change"]
            }, ensure_ascii=False)
    except Exception as e:
        return e

@tool
def get_service_health(service_id: str) -> str:
    """
    Faz um healthcheck no serviço desejado.
    """
    try:
        service = repository.get_service(service_id)
        return json.dumps(
            {
                "service_id": service_id,
                "helath": service["status"]
            }, ensure_ascii=False)
    except Exception as e:
        return e

@tool
def search_service_runbook(service_id: str, symptom: str) -> str:
    """
    Dada uma questão relacionada ao sistema no geral, retorna métodos para lidar com essas situações adversas.
    Segue um sintoma para achar o runbook mais próximo que o responda.
    """
    try:
        runbook = repository.search_runbooks(service_id, symptom)
        return json.dumps(
            {
                "service_id": service_id,
                "symptom": symptom,
                "top1_runbook": {
                    "keywords": runbook[0]["keywords"],
                    "content": runbook[0]["contents"]
                }
            }
        )
    except Exception as e:
        return e


@tool
def invalidate_permission_cache(user_id: str)->str:
    """
    This function invalidates cached data for user roles.
    """
    return "Cache invalidated."

TOOLS = [get_ticket_context, get_user_access, get_recent_role_change, get_service_health, search_service_runbook, invalidate_permission_cache]

