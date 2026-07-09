"""FastAPI app entry (Architect + Coder)"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routes import orders_router, products_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Init DB on startup."""
    init_db()
    yield


app = FastAPI(
    title="ERP 钢化膜电商",
    version="0.1.0",
    description="lobsterai-team v0.1.0 E2E test: 钢化膜电商 ERP",
    lifespan=lifespan,
)

# Health check (DevOps for CI)
@app.get("/api/health", tags=["health"])
def health() -> dict:
    """Health endpoint for CI smoke test."""
    return {"status": "ok", "version": "0.1.0"}


# Routers
app.include_router(products_router)
app.include_router(orders_router)
