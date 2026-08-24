from __future__ import annotations

import json
from langchain.tools import tool
from supportops.rag.service import ChromaRagService, SearchRequest

_SERVICE: ChromaRagService | None = None


def set_rag_service(service: ChromaRagService | None) -> None:
    global _SERVICE
    _SERVICE = service


def get_rag_service() -> ChromaRagService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = ChromaRagService()
    return _SERVICE


@tool
def search_technical_docs(
    query: str,
    service_id: str,
    environment: str,
    source_scope: str = "runbook,adr,postmortem,policy,guide,standard,checklist,architecture,known_errors,slo,api",
    top_k: int = 5,
) -> str:
    """Busque evidências atuais e confiáveis na base técnica persistida em Chroma.

    Use quando diagnóstico ou recomendação depender de procedimento, arquitetura,
    política, API ou histórico. Informe serviço e ambiente exatos do ticket.
    A resposta contém citações, relevância e indicador de suficiência.
    """
    types = tuple(part.strip() for part in source_scope.split(",") if part.strip())
    result = get_rag_service().search(SearchRequest(
        query=query,
        service_id=service_id,
        environment=environment,
        source_types=types,
        top_k=top_k,
    ))
    return json.dumps(result, ensure_ascii=False)
