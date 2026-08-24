import json

from supportops.tools import (
    get_service_health,
    get_ticket_context,
    get_user_access,
    search_service_runbook,
)


def test_ticket_tool():
    payload = json.loads(get_ticket_context.invoke({"ticket_id": "TCK-4821"}))
    assert payload["user_id"] == "USR-100"


def test_access_detects_cache_divergence():
    payload = json.loads(
        get_user_access.invoke(
            {"user_id": "USR-100", "resource": "dashboard:analytics"}
        )
    )
    assert payload["authorized_in_source_of_truth"] is True
    assert payload["cache_diverges_from_source"] is True


def test_service_is_healthy():
    payload = json.loads(get_service_health.invoke({"service_id": "analytics-api"}))
    assert payload["status"] == "healthy"


def test_runbook_mentions_manual_approval():
    payload = json.loads(
        search_service_runbook.invoke(
            {"service_id": "analytics-api", "symptom": "403 role cache"}
        )
    )
    assert payload["count"] >= 1
    assert "aprovação humana" in payload["results"][0]["content"]
