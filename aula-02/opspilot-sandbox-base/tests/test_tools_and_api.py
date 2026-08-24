import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

os.environ['OPSPILOT_DB_PATH'] = '/tmp/opspilot_test_api.sqlite3'
from opspilot.seed import reseed
from opspilot.api import app
from opspilot.tools import get_ticket, set_feature_flag_rollout, tool_specs

@pytest.fixture(autouse=True)
def seed_db():
    p = Path(os.environ['OPSPILOT_DB_PATH'])
    if p.exists(): p.unlink()
    reseed()


def test_langchain_tool_read():
    ticket = get_ticket.invoke({'ticket_id': 'TCK-5001'})
    assert ticket['service_id'] == 'checkout-api'


def test_tool_specs_include_dangerous_tools():
    names = {s['name']: s for s in tool_specs()}
    assert names['revoke_token']['risk'] == 'destructive'
    assert names['set_feature_flag_rollout']['requires_approval'] is True


def test_langchain_dangerous_tool_dry_run():
    result = set_feature_flag_rollout.invoke({
        'flag_key': 'checkout_new_router',
        'percentage': 0,
        'request_id': 'tool-dry-run',
        'reason': 'teste',
        'dry_run': True,
    })
    assert result['status'] == 'dry_run'


def test_fastapi_health_and_tools():
    client = TestClient(app)
    assert client.get('/health').json()['status'] == 'ok'
    tools = client.get('/tools').json()
    assert any(t['name'] == 'issue_credit_memo' for t in tools)


def test_fastapi_write_without_approval_is_blocked():
    client = TestClient(app)
    r = client.post('/api/security/tokens/tok-prod-778/revoke', json={
        'request_id': 'api-blocked',
        'reason': 'token vazado',
        'dry_run': False,
    })
    assert r.status_code == 403
