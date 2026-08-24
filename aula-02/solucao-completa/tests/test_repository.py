from supportops import repository


def test_ticket_exists():
    ticket = repository.get_ticket("TCK-4821")
    assert ticket["error_code"] == 403
    assert ticket["service_id"] == "analytics-api"


def test_runbook_search():
    results = repository.search_runbooks("analytics-api", "erro 403 role cache")
    assert results
    assert results[0]["runbook_id"] == "RB-AN-403"
