from fastapi.testclient import TestClient
from app.main import app
from qa.executor import run_plan
from qa.sample_plans import insufficient_stock_plan

class Adapter:
    def __init__(self,c): self.c=c
    def request(self,m,p,json=None): return self.c.request(m,p,json=json)

def main():
    report=run_plan(insufficient_stock_plan(),client=Adapter(TestClient(app)))
    assert report.passed and report.steps[-1].status==409
    print('SMOKE DIA1 PASS: expected 409 observed')
if __name__=='__main__': main()
