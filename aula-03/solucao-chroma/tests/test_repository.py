from supportops import repository


def test_expanded_backend():
    assert repository.get_ticket("TCK-4826")["service_id"] == "reports-worker"
    assert repository.get_metric_snapshot("reports-worker", "prod")["queue_depth"] == 1840
    assert repository.get_recent_incidents("payments-api", "prod")[0]["incident_id"] == "INC-2026-0714"
