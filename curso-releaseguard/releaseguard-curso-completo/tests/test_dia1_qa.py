import httpx, pytest
from fastapi.testclient import TestClient
from app.main import app
from qa.schemas import TestPlan
from qa.sample_plans import insufficient_stock_plan
from qa.executor import run_plan
from qa.policy import validate_plan_policy

class HttpClientAdapter:
    def __init__(self,tc): self.tc=tc
    def request(self,method,path,json=None): return self.tc.request(method,path,json=json)

def test_schema_rejects_bad_method():
    with pytest.raises(Exception):
        TestPlan.model_validate({'name':'abc','intent':'valid intent','risk':'risk','oracle':'valid oracle','steps':[{'name':'bad','method':'TRACE','path':'/x','expect_status':200}]})

def test_policy_rejects_external_host():
    with pytest.raises(ValueError): validate_plan_policy(insufficient_stock_plan(),'https://example.com')

def test_plan_executes_real_fastapi_flow():
    report=run_plan(insufficient_stock_plan(),client=HttpClientAdapter(TestClient(app)))
    assert report.passed
    assert report.steps[-1].status==409
    assert report.steps[-1].body['detail']=='insufficient stock'
