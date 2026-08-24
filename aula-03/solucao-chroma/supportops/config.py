from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    embedding_model: str = os.getenv("OLLAMA_EMBED_MODEL", "qwen3-embedding:0.6b")
    reasoning: bool = _bool("OLLAMA_REASONING", False)
    num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    collection_name: str = os.getenv("CHROMA_COLLECTION", "supportops_knowledge")
    persist_dir: Path = Path(os.getenv("CHROMA_PERSIST_DIR", ".chroma/supportops"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    rag_fetch_k: int = int(os.getenv("RAG_FETCH_K", "15"))
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
    min_relevance: float = float(os.getenv("RAG_MIN_RELEVANCE", "0.30"))
    max_graph_steps: int = int(os.getenv("AGENT_MAX_GRAPH_STEPS", "24"))
    max_model_calls: int = int(os.getenv("AGENT_MAX_MODEL_CALLS", "8"))
    max_tool_calls: int = int(os.getenv("AGENT_MAX_TOOL_CALLS", "12"))
    agent_enabled: bool = _bool("AGENT_ENABLED", True)
    runs_dir: Path = Path(os.getenv("RUNS_DIR", "runs"))
    docs_dir: Path = Path(__file__).resolve().parent.parent / "docs"
    catalog_path: Path = Path(__file__).resolve().parent.parent / "docs" / "catalog.json"


settings = Settings()
