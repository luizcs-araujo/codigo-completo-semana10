from langchain.tools import tool
from supportops.rag.service import ChromaRagService, SearchRequest
import json

@tool
def search_technical_docs(query: str, service_id: str, environment: str, source_scope: str = "runbook,adr,postmortem,policy", top_k: int = 5) -> str:
    """Busque evidências atuais e confiáveis na base técnica persistida.
    - Any question that require runbook guidance should use the rag tool. It is there to base all your technical decisions, and has information about any workflow in the service you are working with."""
    
    rag_service = ChromaRagService()
    results = rag_service.search(
        SearchRequest(
            query=query,
            service_id=service_id,
            environment=environment,
            source_types=source_scope,
            top_k=top_k
        )
    )
    return json.dumps(results, ensure_ascii=False)