"""Database setup (Data + Architect)"""
import os
from sqlmodel import Session, SQLModel, create_engine

DB_FILE = os.environ.get("ERP_DB", "erp.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """FastAPI dependency."""
    with Session(engine) as session:
        yield session
