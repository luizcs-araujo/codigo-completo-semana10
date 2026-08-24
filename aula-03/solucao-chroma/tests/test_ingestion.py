from supportops.rag.ingestion import load_source_documents, split_documents


def test_corpus_is_deep_and_catalogued():
    docs = load_source_documents()
    assert len(docs) >= 25
    assert all(doc.metadata.get("title") for doc in docs)
    assert all(doc.metadata.get("trust_level") for doc in docs)


def test_framework_splitters_preserve_metadata():
    chunks = split_documents(load_source_documents())
    assert len(chunks) > len(load_source_documents())
    assert all(chunk.metadata.get("heading") for chunk in chunks)
    assert all(chunk.metadata.get("chunk_id") for chunk in chunks)
