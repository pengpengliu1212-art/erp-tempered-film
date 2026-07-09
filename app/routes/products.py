"""Products route (Coder)"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Product, ProductCreate, ProductRead

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductRead])
def list_products(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> List[Product]:
    """List all products (US-001)."""
    products = session.exec(select(Product).offset(skip).limit(limit)).all()
    return list(products)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    session: Session = Depends(get_session),
) -> Product:
    """Add new product SKU (US-002)."""
    # Check if SKU already exists
    existing = session.exec(select(Product).where(Product.sku == product_in.sku)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SKU '{product_in.sku}' already exists",
        )
    db_product = Product.model_validate(product_in)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
) -> Product:
    """Get product by ID (US-003)."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    return product


@router.patch("/{product_id}/stock", response_model=ProductRead)
def update_stock(
    product_id: int,
    new_stock: int = Query(ge=0, le=1_000_000),
    session: Session = Depends(get_session),
) -> Product:
    """Update product stock (US-004)."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    product.stock = new_stock
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/special/low-stock", response_model=List[ProductRead])
def low_stock(
    threshold: int = Query(default=10, ge=0),
    session: Session = Depends(get_session),
) -> List[Product]:
    """List low-stock products (US-008)."""
    products = session.exec(
        select(Product).where(Product.stock <= threshold)
    ).all()
    return list(products)
