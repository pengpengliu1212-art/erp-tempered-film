"""Order model — 钢化膜 orders"""
from typing import Optional
from sqlmodel import Field, SQLModel


class OrderBase(SQLModel):
    product_id: int = Field(gt=0, description="Product ID being ordered")
    qty: int = Field(gt=0, le=10_000, description="Quantity ordered")


class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    total_cents: int = Field(default=0, ge=0, description="Price * qty at order time")
    status: str = Field(default="pending", max_length=20)  # pending/paid/cancelled


class OrderCreate(OrderBase):
    pass


class OrderRead(Order):
    id: int
