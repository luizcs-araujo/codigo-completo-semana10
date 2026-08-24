from supportops.rag.embeddings import HashEmbeddings
from supportops.rag.service import RagService, SearchFilters


def service():
    return RagService(embeddings=HashEmbeddings())


def test_filtered_rag_excludes_obsolete_and_wrong_environment():
    result = service().search(
        "403 role cache dashboard",
        SearchFilters("analytics-api", "prod"),
        top_k=5,
    )
    assert result["evidence"]
    assert all(item["is_current"] for item in result["evidence"])
    assert all(item["environment"] in {"prod", "all"} for item in result["evidence"])
    assert not any("OBSOLETO" in item["source"] for item in result["evidence"])


def test_exact_error_code_and_runbook_are_retrieved():
    result = service().search(
        "HTTP 403 depois de mudança de role",
        SearchFilters("analytics-api", "prod"),
        top_k=4,
    )
    sources = {item["source"] for item in result["evidence"]}
    assert "analytics-api/runbook_permission_cache_v2.md" in sources
    assert result["sufficient"] is True


def test_unknown_service_returns_only_generic_policy_and_is_insufficient():
    result = service().search(
        "E-771 arquivo grande",
        SearchFilters("reports-worker", "prod"),
        top_k=4,
    )
    assert result["sufficient"] is False
    assert all(item["service_id"] == "shared" for item in result["evidence"])
    assert not any(item["source_type"] == "runbook" for item in result["evidence"])
