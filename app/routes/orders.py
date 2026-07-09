"""Orders route (Coder)"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Order, OrderCreate, OrderRead, Product

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=List[OrderRead])
def list_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> List[Order]:
    """List all orders (US-007)."""
    orders = session.exec(select(Order).offset(skip).limit(limit)).all()
    return list(orders)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    session: Session = Depends(get_session),
) -> Order:
    """Create order with auto-decrement stock (US-005)."""
    # Validate product exists and has enough stock (US-006)
    product = session.get(Product, order_in.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {order_in.product_id} not found",
        )
    if product.stock < order_in.qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock: have {product.stock}, need {order_in.qty}",
        )
    # Create order
    db_order = Order(
        product_id=order_in.product_id,
        qty=order_in.qty,
        total_cents=product.price_cents * order_in.qty,
        status="pending",
    )
    # Decrement stock
    product.stock -= order_in.qty
    # Persist both
    session.add(db_order)
    session.add(product)
    session.commit()
    session.refresh(db_order)
    return db_order
