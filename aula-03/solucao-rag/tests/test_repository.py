from supportops import repository


def test_ticket_and_expanded_sources_exist():
    ticket = repository.get_ticket("TCK-4821")
    assert ticket["error_code"] == 403
    assert ticket["environment"] == "prod"
    assert repository.get_recent_incidents("analytics-api", "prod")
    assert repository.get_recent_deployments("payments-api", "prod")
