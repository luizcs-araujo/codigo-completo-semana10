from fastapi.testclient import TestClient
from app.main import app
from app.state.store import state

def main():
    state.reset(); c=TestClient(app)
    assert c.get('/health').status_code==200
    assert c.get('/store/checkout').status_code==200
    cart=c.post('/cart').json()
    r=c.post(f"/cart/{cart['id']}/items",json={'product_id':'sku-001','quantity':99})
    assert r.status_code==409
    c.post('/lab/scenarios/visual_checkout_shift/activate')
    assert c.get('/health').json()['scenario']=='visual_checkout_shift'
    c.post('/lab/scenarios/reset')
    print('SMOKE BASE PASS')
if __name__=='__main__': main()
