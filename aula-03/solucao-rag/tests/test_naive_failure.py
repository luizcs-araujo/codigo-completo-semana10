from supportops.rag.naive import naive_search


def test_naive_search_reproduces_obsolete_document_failure():
    results = naive_search("erro 403 role dashboard cache analytics-api")
    assert results[0]["is_current"] is False
    assert "OBSOLETO" in results[0]["source"]
