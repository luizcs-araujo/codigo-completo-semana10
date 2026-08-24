from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings

from supportops.config import settings
from supportops.rag.chunking import heading_aware_chunks
from supportops.rag.documents import load_documents
from supportops.rag.embeddings import HashEmbeddings


def _tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z0-9_:-]+", normalized))


def _lexical_score(query: str, document: Document) -> float:
    q = _tokens(query)
    d = _tokens(document.page_content + " " + str(document.metadata.get("title", "")))
    overlap = len(q & d) / max(len(q), 1)
    exact_codes = sum(1 for token in q if any(ch.isdigit() for ch in token) and token in d)
    return overlap + exact_codes * 0.35


def _rrf(ranks: Iterable[list[str]], constant: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranked in ranks:
        for index, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (constant + index)
    return scores


@dataclass(frozen=True)
class SearchFilters:
    service_id: str
    environment: str
    source_types: tuple[str, ...] = ("runbook", "adr", "postmortem", "policy")
    current_only: bool = True


class RagService:
    def __init__(self, embeddings: Embeddings | None = None):
        self.embeddings = embeddings or self._default_embeddings()
        self.documents = load_documents(settings.docs_dir)
        self.chunks = heading_aware_chunks(self.documents, settings.chunk_size, settings.chunk_overlap)
        self.vector_store = InMemoryVectorStore.from_documents(self.chunks, embedding=self.embeddings)
        self._by_id = {str(doc.id): doc for doc in self.chunks}

    @staticmethod
    def _default_embeddings() -> Embeddings:
        if settings.embedding_backend.lower() == "hash":
            return HashEmbeddings()
        return OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.base_url,
            validate_model_on_init=True,
        )

    @staticmethod
    def _matches(doc: Document, filters: SearchFilters) -> bool:
        md = doc.metadata
        service_ok = md.get("service_id") in {filters.service_id, "shared"}
        env_ok = md.get("environment") in {filters.environment, "all"}
        current_ok = (not filters.current_only) or md.get("is_current") is True
        type_ok = md.get("source_type") in filters.source_types
        return service_ok and env_ok and current_ok and type_ok and md.get("access_scope") == "internal"

    def search(self, query: str, filters: SearchFilters, top_k: int | None = None) -> dict:
        k = top_k or settings.rag_top_k
        filter_fn = lambda doc: self._matches(doc, filters)
        dense = self.vector_store.similarity_search_with_score(query, k=max(k * 3, 8), filter=filter_fn)
        filtered = [doc for doc in self.chunks if filter_fn(doc)]
        lexical = sorted(filtered, key=lambda doc: _lexical_score(query, doc), reverse=True)[: max(k * 3, 8)]

        dense_ids = [str(doc.id) for doc, _ in dense]
        lexical_ids = [str(doc.id) for doc in lexical if _lexical_score(query, doc) > 0]
        fused = _rrf([dense_ids, lexical_ids])
        ranked_ids = sorted(fused, key=fused.get, reverse=True)

        evidence = []
        sources_seen: dict[str, int] = {}
        for doc_id in ranked_ids:
            doc = self._by_id[doc_id]
            source = doc.metadata["source_path"]
            if sources_seen.get(source, 0) >= 2:
                continue
            sources_seen[source] = sources_seen.get(source, 0) + 1
            evidence.append({
                "chunk_id": doc_id,
                "title": doc.metadata["title"],
                "source": source,
                "heading": doc.metadata["heading"],
                "version": doc.metadata["version"],
                "updated_at": doc.metadata["updated_at"],
                "source_type": doc.metadata["source_type"],
                "service_id": doc.metadata["service_id"],
                "environment": doc.metadata["environment"],
                "is_current": doc.metadata["is_current"],
                "citation": f"{source}#{doc.metadata['heading']}",
                "excerpt": doc.page_content[:650],
                "fusion_score": round(fused[doc_id], 6),
            })
            if len(evidence) >= k:
                break

        source_types = {item["source_type"] for item in evidence}
        operational = bool(source_types & {"runbook", "policy"})
        independent = len({item["source"] for item in evidence}) >= 2
        sufficient = bool(evidence) and operational and independent
        reason = (
            "Há procedimento atual e ao menos duas fontes citáveis."
            if sufficient else
            "Faltam fontes atuais, operacionais ou independentes para sustentar a recomendação."
        )
        return {
            "query": query,
            "filters": {
                "service_id": filters.service_id,
                "environment": filters.environment,
                "source_types": list(filters.source_types),
                "current_only": filters.current_only,
            },
            "sufficient": sufficient,
            "sufficiency_reason": reason,
            "count": len(evidence),
            "evidence": evidence,
        }
