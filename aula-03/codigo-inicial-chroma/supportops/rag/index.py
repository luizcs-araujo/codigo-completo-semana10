from __future__ import annotations

import shutil
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from supportops.config import settings
from supportops.rag.ingestion import load_source_documents, split_documents
from datetime import datetime, timezone
import json

def default_embeddings() -> Embeddings:
    return OllamaEmbeddings(model=settings.embedding_model, base_url=settings.base_url, validate_model_on_init=True)


def open_store(embeddings: Embeddings | None = None, persist_directory: Path | None = None, collection_name: str | None = None) -> Chroma:
    return Chroma(
        collection_name=collection_name or settings.collection_name,
        embedding_function=embeddings or default_embeddings(),
        persist_directory=str(persist_directory or settings.persist_dir)
    )


def rebuild_index(embeddings: Embeddings | None = None, persist_directory: Path | None = None, collection_name: str | None = None) -> dict:
    target = persist_directory or settings.persist_dir
    if target.exists():
        shutil.rmtree(target)
    
    source_documents = load_source_documents()
    chunks = split_documents(source_documents)
    store = open_store(embeddings=embeddings, persist_directory=target, collection_name=collection_name)
    store.add_documents(chunks, ids=[chunk.metadata["chunk_id"] for chunk in chunks])
    manifest ={
        "created_at": datetime.now(timezone.utc).isoformat(),
        "collection": collection_name or settings.collection_name,
        "source_documents": len(source_documents),
        "chunks": len(chunks),
        "embedding_model": settings.embedding_model
    }
    target.mkdir(parents=True, exist_ok=True)
    (target/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def index_count(store: Chroma) -> int:
    return store._collection.count()
