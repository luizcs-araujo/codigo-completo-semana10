from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from supportops.rag.index import open_store
from supportops.config import settings

@dataclass(frozen=True)
class SearchRequest:
    query: str
    service_id: str
    environment: str
    source_types: tuple[str, ...] = ("runbook", "adr", "postmortem", "policy", "guide", "standard", "checklist", "architecture", "known_errors", "slo", "api")
    top_k: int = 5


def build_filter(request: SearchRequest) -> dict:
    # TODO AULA 3: construir filtro Chroma com $and, $in e $eq.
    raise NotImplementedError


class ChromaRagService:
    def __init__(self, embeddings: Embeddings | None = None, persist_directory: Path | None = None, collection_name: str | None = None):
        self.store: Chroma = open_store(embeddings=embeddings, persist_directory=persist_directory, collection_name=collection_name)

    def search(self, request: SearchRequest) -> dict:
        results = self.store.similarity_search_with_relevance_scores(
            request.query,
            k=request.top_k
        )
        evidence = []
        for document, relevance in results:
            if relevance < settings.min_relevance:
                break
            md = document.metadata
            evidence.append(
                {
                    **md,
                    "excerpt": document.page_content,
                    "relevance": round(relevance, 4)
                }
            )
        return{
            "query": request.query,
            "count": len(evidence),
            "evidence": evidence
        }
            
               


