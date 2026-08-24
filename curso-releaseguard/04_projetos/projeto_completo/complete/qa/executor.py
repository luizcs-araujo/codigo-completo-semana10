from __future__ import annotations
from dataclasses import dataclass, asdict
import httpx
from qa.schemas import TestPlan
from qa.policy import validate_plan_policy

@dataclass
class StepResult:
    name:str; method:str; path:str; status:int; expected_status:int; passed:bool; body:object

@dataclass
class TestReport:
    name:str; passed:bool; steps:list[StepResult]
    def as_dict(self): return {'name':self.name,'passed':self.passed,'steps':[asdict(s) for s in self.steps]}

def run_plan(plan:TestPlan, base_url:str='http://127.0.0.1:8000', client:httpx.Client|None=None)->TestReport:
    validate_plan_policy(plan,base_url)
    own=client is None; client=client or httpx.Client(base_url=base_url,timeout=3.0)
    context={} ; results=[]
    try:
        for step in plan.steps:
            path=step.path.format(**context)
            r=client.request(step.method,path,json=step.json_body)
            body=r.json() if 'application/json' in r.headers.get('content-type','') else r.text
            if step.path=='/cart' and isinstance(body,dict) and 'id' in body: context['cart_id']=body['id']
            if step.path=='/checkout' and isinstance(body,dict) and 'id' in body: context['order_id']=body['id']
            results.append(StepResult(step.name,step.method,path,r.status_code,step.expect_status,r.status_code==step.expect_status,body))
        return TestReport(plan.name, all(s.passed for s in results), results)
    finally:
        if own: client.close()
