import os
from pathlib import Path
import pytest

os.environ['OPSPILOT_DB_PATH'] = '/tmp/opspilot_test.sqlite3'
from opspilot.seed import reseed
from opspilot.repository import Repository
from opspilot.policies import DEMO_APPROVAL_TOKEN

@pytest.fixture(autouse=True)
def seed_db():
    p = Path(os.environ['OPSPILOT_DB_PATH'])
    if p.exists(): p.unlink()
    reseed()


def test_read_service_health():
    repo = Repository()
    health = repo.get_service_health('checkout-api')
    assert health['status'] == 'degraded'
    assert health['error_rate'] > 0.1


def test_dangerous_action_requires_approval_for_real_execution():
    repo = Repository()
    with pytest.raises(PermissionError):
        repo.set_feature_flag_rollout('checkout_new_router', 0, 'test-req-1', 'mitigar regressão', dry_run=False)


def test_dry_run_does_not_change_state():
    repo = Repository()
    before = repo.get_feature_flag('checkout_new_router')['percentage']
    result = repo.set_feature_flag_rollout('checkout_new_router', 0, 'test-req-2', 'simular rollback', dry_run=True)
    after = repo.get_feature_flag('checkout_new_router')['percentage']
    assert result.status == 'dry_run'
    assert before == after == 30


def test_real_write_changes_state_with_approval():
    repo = Repository()
    result = repo.set_feature_flag_rollout('checkout_new_router', 0, 'test-req-3', 'rollback aprovado', dry_run=False, approval_token=DEMO_APPROVAL_TOKEN)
    assert result.status == 'executed'
    assert repo.get_feature_flag('checkout_new_router')['percentage'] == 0


def test_idempotency_prevents_duplicate_real_writes():
    repo = Repository()
    a = repo.restart_service('checkout-api', 'same-req', 'primeira execução', dry_run=False, approval_token=DEMO_APPROVAL_TOKEN)
    b = repo.restart_service('checkout-api', 'same-req', 'segunda execução', dry_run=False, approval_token=DEMO_APPROVAL_TOKEN)
    assert a.status == 'executed'
    assert b.status == 'duplicate'
