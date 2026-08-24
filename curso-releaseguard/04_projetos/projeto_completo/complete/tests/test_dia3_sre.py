import time
from fastapi.testclient import TestClient
from app.main import app
from app.state.store import state

def _make_order(c):
    cart=c.post('/cart').json(); c.post(f"/cart/{cart['id']}/items",json={'product_id':'sku-001','quantity':1}); return c.post('/checkout',json={'cart_id':cart['id'],'address':'Rua Teste 123'}).json()

def test_metrics_reflect_real_payment_latency():
    c=TestClient(app); o=_make_order(c); c.post('/lab/scenarios/payment_latency/activate')
    t=time.perf_counter(); r=c.post('/payments',json={'order_id':o['id'],'amount':o['total']}); elapsed=time.perf_counter()-t
    assert r.status_code==200 and elapsed>=0.20
    metrics=c.get('/metrics').text
    assert 'releaseguard_http_request_duration_seconds' in metrics
    assert 'releaseguard_dependency_duration_seconds' in metrics

def test_payment_timeout_is_real_effect():
    c=TestClient(app); o=_make_order(c); c.post('/lab/scenarios/payment_timeout/activate')
    assert c.post('/payments',json={'order_id':o['id'],'amount':o['total']}).status_code==504
