from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from supportops.config import settings
from supportops.rag.index import index_count, open_store


@dataclass(frozen=True)
class SearchRequest:
    query: str
    service_id: str
    environment: str
    source_types: tuple[str, ...] = ("runbook", "adr", "postmortem", "policy", "guide", "standard", "checklist", "architecture", "known_errors", "slo", "api")
    top_k: int = 5


def build_filter(request: SearchRequest) -> dict:
    return {
        "$and": [
            {"service_id": {"$in": [request.service_id, "shared"]}},
            {"environment": {"$in": [request.environment, "all"]}},
            {"is_current": {"$eq": True}},
            {"source_type": {"$in": list(request.source_types)}},
            {"trust_level": {"$in": ["authoritative", "validated"]}},
            {"access_scope": {"$eq": "internal"}},
        ]
    }


class ChromaRagService:
    def __init__(self, embeddings: Embeddings | None = None, persist_directory: Path | None = None, collection_name: str | None = None):
        self.store: Chroma = open_store(embeddings, persist_directory, collection_name)

    def search(self, request: SearchRequest) -> dict:
        if index_count(self.store) == 0:
            raise RuntimeError("Índice Chroma vazio. Execute python -m supportops.rebuild_index")
        k = max(1, min(request.top_k, 8))
        results = self.store.similarity_search_with_relevance_scores(
            request.query,
            k=k,
            filter=build_filter(request),
        )
        evidence = []
        for document, relevance in results:
            relevance = max(0.0, min(1.0, float(relevance)))
            if relevance < settings.min_relevance:
                continue
            md = document.metadata
            evidence.append({
                "chunk_id": md["chunk_id"],
                "title": md["title"],
                "source": md["source_path"],
                "heading": md.get("heading", "Documento"),
                "version": str(md["version"]),
                "updated_at": md["updated_at"],
                "source_type": md["source_type"],
                "trust_level": md["trust_level"],
                "service_id": md["service_id"],
                "environment": md["environment"],
                "current": bool(md["is_current"]),
                "citation": f"{md['source_path']}#{md.get('heading', 'Documento')}",
                "excerpt": document.page_content[:700],
                "relevance": round(relevance, 4),
            })
        sources = {row["source"] for row in evidence}
        types = {row["source_type"] for row in evidence}
        has_operational = bool(types & {"runbook", "policy", "standard", "known_errors"})
        sufficient = len(sources) >= 2 and has_operational
        return {
            "query": request.query,
            "filters": build_filter(request),
            "count": len(evidence),
            "sufficient": sufficient,
            "sufficiency_reason": (
                "Há fonte operacional e pelo menos duas fontes independentes."
                if sufficient else
                "Faltam fonte operacional, relevância mínima ou fontes independentes."
            ),
            "evidence": evidence,
        }
