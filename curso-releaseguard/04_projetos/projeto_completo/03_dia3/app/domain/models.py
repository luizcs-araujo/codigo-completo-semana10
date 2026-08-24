from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

class Product(BaseModel):
    id: str
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class Cart(BaseModel):
    id: str
    items: list[CartItem] = []

class AddCartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class CheckoutRequest(BaseModel):
    cart_id: str
    address: str = Field(min_length=5)

class PaymentRequest(BaseModel):
    order_id: str
    amount: float = Field(gt=0)

class Order(BaseModel):
    id: str
    cart_id: str
    total: float
    status: Literal['pending','paid','fulfilled','cancelled'] = 'pending'
