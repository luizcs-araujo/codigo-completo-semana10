from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class HttpStep(BaseModel):
    name: str = Field(min_length=3)
    method: Literal['GET','POST','PUT','PATCH','DELETE']
    path: str = Field(pattern=r'^/.*$')
    json_body: dict | None = None
    expect_status: int = Field(ge=100, le=599)

class TestPlan(BaseModel):
    __test__ = False
    name: str = Field(min_length=3)
    intent: str = Field(min_length=5)
    risk: str = Field(min_length=3)
    oracle: str = Field(min_length=5)
    steps: list[HttpStep] = Field(min_length=1, max_length=8)
