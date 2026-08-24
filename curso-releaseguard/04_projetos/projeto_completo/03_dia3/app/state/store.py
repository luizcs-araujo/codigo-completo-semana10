from __future__ import annotations
from dataclasses import dataclass, field
from app.domain.models import Product, Cart, Order

PRODUCT_FIXTURES = {
 'sku-001': Product(id='sku-001', name='Notebook Pro', price=5499.0, stock=3),
 'sku-002': Product(id='sku-002', name='Mouse Ergo', price=249.0, stock=12),
 'sku-003': Product(id='sku-003', name='Monitor 27', price=1799.0, stock=5),
}

@dataclass
class AppState:
    products: dict[str, Product] = field(default_factory=dict)
    carts: dict[str, Cart] = field(default_factory=dict)
    orders: dict[str, Order] = field(default_factory=dict)
    scenario: str = 'normal'
    order_seq: int = 1

    def reset(self):
        self.products = {k:v.model_copy(deep=True) for k,v in PRODUCT_FIXTURES.items()}
        self.carts = {}
        self.orders = {}
        self.scenario = 'normal'
        self.order_seq = 1

state = AppState()
state.reset()
