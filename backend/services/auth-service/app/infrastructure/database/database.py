"""
Infrastructure: Database Configuration — database.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SQLAlchemy engine, session factory, and Base class.

Responsibilities:
  - Create the PostgreSQL connection engine
  - Provide a session factory (SessionLocal)
  - Expose the declarative Base for all ORM models
  - Provide the get_db() FastAPI dependency

Clean Architecture Rule:
  This file lives in infrastructure/ because it is
  technology-specific (PostgreSQL via SQLAlchemy).
  The domain layer has NO knowledge of this file.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


# ─────────────────────────────────────────────────────────────
# SQLAlchemy Engine
# ─────────────────────────────────────────────────────────────
# pool_pre_ping=True → Tests connections before checkout.
# This prevents "server closed connection" errors after idle periods.
# ─────────────────────────────────────────────────────────────
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )


# ─────────────────────────────────────────────────────────────
# Session Factory
# ─────────────────────────────────────────────────────────────
# autocommit=False → We manually commit (safer, explicit)
# autoflush=False  → We control when changes are flushed to DB
# ─────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─────────────────────────────────────────────────────────────
# Declarative Base
# ─────────────────────────────────────────────────────────────
# All SQLAlchemy ORM models (UserModel, etc.) inherit from Base.
# Base.metadata.create_all(engine) creates tables on startup.
# ─────────────────────────────────────────────────────────────
Base = declarative_base()


# ─────────────────────────────────────────────────────────────
# FastAPI Database Session Dependency
# ─────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session per HTTP request.

    Usage in route:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...

    The try/finally guarantees the session is closed even on errors,
    returning the connection back to the pool.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Test whether the database is reachable.

    Used by GET /health/db endpoint.

    Returns:
        True if PostgreSQL responds to a simple query.
        False if the connection fails.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
