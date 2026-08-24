from __future__ import annotations
import time
from fastapi import APIRouter, HTTPException
from app.domain.models import Cart, AddCartItem, CheckoutRequest, PaymentRequest, Order
from app.state.store import state
from app.scenarios.catalog import SCENARIOS

router=APIRouter()

@router.get('/health')
def health(): return {'status':'ok','scenario':state.scenario}

@router.get('/products')
def products():
    if state.scenario=='inventory_500': raise HTTPException(500,'inventory unavailable')
    if state.scenario=='inventory_slow': time.sleep(0.15)
    return list(state.products.values())

@router.get('/products/{product_id}')
def product(product_id:str):
    p=state.products.get(product_id)
    if not p: raise HTTPException(404,'product not found')
    return p

@router.post('/cart', response_model=Cart)
def create_cart():
    cid=f'cart-{len(state.carts)+1:03d}'
    c=Cart(id=cid,items=[]); state.carts[cid]=c; return c

@router.get('/cart/{cart_id}', response_model=Cart)
def get_cart(cart_id:str):
    c=state.carts.get(cart_id)
    if not c: raise HTTPException(404,'cart not found')
    return c

@router.post('/cart/{cart_id}/items', response_model=Cart, responses={409:{'description':'Insufficient stock'}})
def add_item(cart_id:str, item:AddCartItem):
    c=state.carts.get(cart_id)
    if not c: raise HTTPException(404,'cart not found')
    p=state.products.get(item.product_id)
    if not p: raise HTTPException(404,'product not found')
    if item.quantity>p.stock: raise HTTPException(409,'insufficient stock')
    c.items.append(item); return c

@router.post('/checkout', response_model=Order, responses={409:{'description':'Insufficient stock'}})
def checkout(req:CheckoutRequest):
    c=state.carts.get(req.cart_id)
    if not c: raise HTTPException(404,'cart not found')
    if not c.items: raise HTTPException(422,'cart is empty')
    total=0.0
    for item in c.items:
        p=state.products[item.product_id]
        if item.quantity>p.stock: raise HTTPException(409,'insufficient stock')
        total += p.price*item.quantity
    oid=f'ord-{state.order_seq:03d}'; state.order_seq+=1
    o=Order(id=oid,cart_id=c.id,total=round(total,2)); state.orders[oid]=o; return o

@router.post('/payments')
def payment(req:PaymentRequest):
    o=state.orders.get(req.order_id)
    if not o: raise HTTPException(404,'order not found')
    if abs(o.total-req.amount)>0.01: raise HTTPException(400,'amount mismatch')
    if state.scenario=='payment_latency': time.sleep(0.25)
    if state.scenario=='payment_timeout': time.sleep(0.5); raise HTTPException(504,'payment provider timeout')
    o.status='paid'; return {'status':'approved','order_id':o.id}

@router.get('/orders/{order_id}', response_model=Order)
def order(order_id:str):
    o=state.orders.get(order_id)
    if not o: raise HTTPException(404,'order not found')
    return o

@router.post('/lab/scenarios/{scenario}/activate')
def activate_scenario(scenario:str):
    if scenario not in SCENARIOS: raise HTTPException(404,'scenario not found')
    state.scenario=scenario; return {'active':scenario}

@router.post('/lab/scenarios/reset')
def reset_scenario():
    state.reset(); return {'active':'normal'}
