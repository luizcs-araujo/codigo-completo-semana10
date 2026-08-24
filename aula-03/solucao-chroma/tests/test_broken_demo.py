from pathlib import Path
from langchain_core.embeddings import DeterministicFakeEmbedding
from supportops.rag.broken import broken_first_match
from supportops.rag.index import rebuild_index


def test_broken_configuration_returns_obsolete_source(tmp_path: Path):
    embedding = DeterministicFakeEmbedding(size=64)
    rebuild_index(embedding, tmp_path, "broken")
    result = broken_first_match(embedding, tmp_path, "broken")
    assert result["metadata"]["is_current"] is False
    assert "obsoleto" in result["metadata"]["source_path"].lower()
