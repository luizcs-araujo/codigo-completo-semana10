from pathlib import Path
from langchain_core.embeddings import DeterministicFakeEmbedding
from supportops.rag.index import rebuild_index, open_store, index_count
from supportops.rag.service import ChromaRagService, SearchRequest, build_filter


def test_persistent_chroma_index(tmp_path: Path):
    embedding = DeterministicFakeEmbedding(size=96)
    manifest = rebuild_index(embedding, tmp_path, "test_index")
    assert manifest["source_documents"] >= 25
    store = open_store(embedding, tmp_path, "test_index")
    assert index_count(store) == manifest["chunks"]


def test_filter_excludes_obsolete_staging_and_unverified(tmp_path: Path):
    embedding = DeterministicFakeEmbedding(size=96)
    rebuild_index(embedding, tmp_path, "filtered")
    service = ChromaRagService(embedding, tmp_path, "filtered")
    result = service.search(SearchRequest("403 role cache", "analytics-api", "prod", top_k=8))
    assert result["evidence"]
    assert all(item["current"] for item in result["evidence"])
    assert all(item["environment"] in {"prod", "all"} for item in result["evidence"])
    assert all(item["trust_level"] in {"authoritative", "validated"} for item in result["evidence"])
    assert not any("obsoleto" in item["source"].lower() for item in result["evidence"])


def test_filter_shape_uses_chroma_operators():
    where = build_filter(SearchRequest("x", "analytics-api", "prod"))
    assert "$and" in where
    assert {"is_current": {"$eq": True}} in where["$and"]
