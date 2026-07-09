"""Routes init"""
from .products import router as products_router
from .orders import router as orders_router

__all__ = ["products_router", "orders_router"]
