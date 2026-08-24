import time
from fastapi.testclient import TestClient
from app.main import app
from app.state.store import state
def main():
 state.reset(); c=TestClient(app); cart=c.post('/cart').json(); c.post(f"/cart/{cart['id']}/items",json={'product_id':'sku-001','quantity':1}); order=c.post('/checkout',json={'cart_id':cart['id'],'address':'Rua Demo 123'}).json(); c.post('/lab/scenarios/payment_latency/activate'); t=time.perf_counter(); c.post('/payments',json={'order_id':order['id'],'amount':order['total']}); elapsed=time.perf_counter()-t; assert elapsed>=.20; m=c.get('/metrics').text; assert 'payment_provider' in m; print(f'SMOKE DIA3 PASS: real latency {elapsed:.3f}s recorded in /metrics')
if __name__=='__main__': main()
