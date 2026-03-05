"""Database connection and session management using SQLModel + PostgreSQL."""

from sqlmodel import Session, create_engine, SQLModel
from settings import settings


engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Session:
    """Create a new database session."""
    return Session(engine)


def init_db():
    """Create all tables (used for testing / initial setup)."""
    SQLModel.metadata.create_all(engine)
