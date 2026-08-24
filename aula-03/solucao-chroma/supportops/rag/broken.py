from __future__ import annotations

from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from supportops.rag.index import open_store


def broken_first_match(embeddings: Embeddings, persist_directory: Path, collection_name: str) -> dict:
    """Baseline propositalmente ruim: full-text e filtro apenas de serviço.

    Depois, ainda ordena o documento mais antigo primeiro. Isso reproduz de forma
    determinística o risco de aceitar uma fonte obsoleta sem governança.
    """
    store: Chroma = open_store(embeddings, persist_directory, collection_name)
    rows = store.get(
        where={"service_id": "analytics-api"},
        where_document={"$contains": "403"},
        include=["documents", "metadatas"],
    )
    records = [
        {"id": row_id, "document": doc, "metadata": metadata}
        for row_id, doc, metadata in zip(rows["ids"], rows["documents"], rows["metadatas"])
    ]
    records.sort(key=lambda row: row["metadata"]["updated_at"])
    return records[0]
