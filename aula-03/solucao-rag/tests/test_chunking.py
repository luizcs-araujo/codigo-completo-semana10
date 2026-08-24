from supportops.config import settings
from supportops.rag.chunking import heading_aware_chunks
from supportops.rag.documents import load_documents


def test_chunking_preserves_heading_and_source():
    chunks = heading_aware_chunks(load_documents(settings.docs_dir), chunk_size=500, chunk_overlap=60)
    assert len(chunks) > len(load_documents(settings.docs_dir))
    assert all(chunk.metadata.get("heading") for chunk in chunks)
    assert all(chunk.metadata.get("source_path") for chunk in chunks)
    assert max(len(chunk.page_content) for chunk in chunks) <= 560
