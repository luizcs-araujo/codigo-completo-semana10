from __future__ import annotations

from supportops.config import settings
from supportops.rag.chunking import naive_whole_document_chunks
from supportops.rag.documents import load_documents
from supportops.rag.service import _lexical_score


def naive_search(query: str, limit: int = 3) -> list[dict]:
    """Busca propositalmente defeituosa: sem chunking útil, filtros ou controle de versão."""
    documents = naive_whole_document_chunks(load_documents(settings.docs_dir))
    ranked = sorted(documents, key=lambda doc: _lexical_score(query, doc), reverse=True)
    return [{
        "title": doc.metadata["title"],
        "source": doc.metadata["source_path"],
        "version": doc.metadata["version"],
        "is_current": doc.metadata["is_current"],
        "environment": doc.metadata["environment"],
        "excerpt": doc.page_content[:500],
    } for doc in ranked[:limit]]
