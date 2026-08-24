from __future__ import annotations

import json
from langchain.tools import tool

from supportops.rag.service import RagService, SearchFilters
from supportops.resilience import CircuitBreaker, CircuitOpenError

_SERVICE: RagService | None = None
_BREAKER = CircuitBreaker()


def set_rag_service(service: RagService | None) -> None:
    global _SERVICE
    _SERVICE = service


def get_rag_service() -> RagService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = RagService()
    return _SERVICE


@tool
def search_technical_docs(
    query: str,
    service_id: str,
    environment: str,
    source_scope: str = "runbook,adr,postmortem,policy",
    top_k: int = 4,
) -> str:
    """Busque evidências atuais na documentação técnica.

    Use quando o diagnóstico ou a recomendação depender de procedimento interno,
    arquitetura, política ou histórico. Informe serviço e ambiente do ticket.
    A resposta contém citações e um indicador de suficiência.
    """
    source_types = tuple(part.strip() for part in source_scope.split(",") if part.strip())
    try:
        _BREAKER.before_call()
        result = get_rag_service().search(
            query=query,
            filters=SearchFilters(service_id=service_id, environment=environment, source_types=source_types),
            top_k=max(1, min(top_k, 6)),
        )
        _BREAKER.success()
        return json.dumps(result, ensure_ascii=False)
    except CircuitOpenError as exc:
        return json.dumps({"status":"blocked","reason":str(exc),"sufficient":False,"evidence":[]}, ensure_ascii=False)
    except Exception:
        _BREAKER.failure()
        raise
