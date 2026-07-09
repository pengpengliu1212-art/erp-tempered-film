"""Product model — 钢化膜 SKU"""
from typing import Optional
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=200, description="Product name")
    sku: str = Field(min_length=1, max_length=50, unique=True, description="Unique SKU")
    size: str = Field(min_length=1, max_length=50, description="Compatible device, e.g., 'iPhone 15'")
    material: str = Field(min_length=1, max_length=50, description="Material, e.g., '9H tempered glass'")
    price_cents: int = Field(ge=0, description="Price in cents (avoid float)")
    stock: int = Field(ge=0, default=0, description="Current stock count")


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
