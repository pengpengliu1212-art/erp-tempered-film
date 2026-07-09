"""QA: pytest fixtures (each test gets fresh DB)"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Use a unique temp DB per test session
_TEST_DB = tempfile.mktemp(suffix=".db", prefix="erp_test_")
os.environ["ERP_DB"] = _TEST_DB

from app.database import engine, init_db
from app.main import app  # noqa: E402  import after env var set


@pytest.fixture(autouse=True)
def fresh_db():
    """Reset DB before each test."""
    from sqlmodel import SQLModel
    init_db()
    # Clear all data from all tables (respect FK order)
    with engine.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient."""
    return TestClient(app)
