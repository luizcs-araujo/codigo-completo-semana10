def test_health(client):
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_catalog_uses_canonical_ids(client):
    ids={p['id'] for p in client.get('/products').json()}; assert ids=={'sku-001','sku-002','sku-003'}

def test_cart_stock_guard(client):
    cart=client.post('/cart').json()
    r=client.post(f"/cart/{cart['id']}/items",json={'product_id':'sku-001','quantity':99})
    assert r.status_code==409; assert r.json()['detail']=='insufficient stock'

def test_happy_checkout_and_payment(client):
    cart=client.post('/cart').json()
    assert client.post(f"/cart/{cart['id']}/items",json={'product_id':'sku-001','quantity':1}).status_code==200
    order=client.post('/checkout',json={'cart_id':cart['id'],'address':'Rua Exemplo 123'}).json()
    pay=client.post('/payments',json={'order_id':order['id'],'amount':order['total']})
    assert pay.status_code==200
    assert client.get(f"/orders/{order['id']}").json()['status']=='paid'

def test_scenario_activation_and_reset(client):
    assert client.post('/lab/scenarios/payment_latency/activate').json()['active']=='payment_latency'
    assert client.get('/health').json()['scenario']=='payment_latency'
    assert client.post('/lab/scenarios/reset').json()['active']=='normal'

def test_ui_routes_exist(client):
    assert client.get('/store').status_code==200
    r=client.get('/store/checkout'); assert r.status_code==200; assert 'Finalizar compra' in r.text

def test_visual_scenario_changes_real_html(client):
    normal=client.get('/store/checkout').text
    client.post('/lab/scenarios/visual_missing_cta/activate')
    changed=client.get('/store/checkout').text
    assert 'Finalizar compra' in normal and 'Finalizar compra' not in changed
