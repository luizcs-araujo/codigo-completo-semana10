import json
from supportops.tools import get_ticket_context, get_recent_incidents, get_recent_deployments


def test_expanded_mock_services():
    ticket = json.loads(get_ticket_context.invoke({"ticket_id":"TCK-4821"}))
    assert ticket["environment"] == "prod"
    incidents = json.loads(get_recent_incidents.invoke({"service_id":"analytics-api","environment":"prod","limit":3}))
    assert incidents[0]["incident_id"] == "INC-2026-0618"
    deployments = json.loads(get_recent_deployments.invoke({"service_id":"payments-api","environment":"prod","limit":3}))
    assert deployments[0]["deployment_id"] == "DEP-PAY-204"
