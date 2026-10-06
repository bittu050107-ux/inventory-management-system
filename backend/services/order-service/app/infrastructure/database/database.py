"""
Infrastructure: Database Configuration — database.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SQLAlchemy engine, session factory, declarative Base,
and a health-check helper for the /health/db endpoint.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

from app.core.config import settings


# ─────────────────────────────────────────────────────────────
# Engine
# pool_pre_ping=True  →  test connection health before reuse
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
# autocommit=False  → transactions must be committed explicitly
# autoflush=False   → prevents surprise flushes mid-transaction
# ─────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ─────────────────────────────────────────────────────────────
# Declarative Base
# All ORM models inherit from this Base.
# ─────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# Database Session Dependency (FastAPI)
# ─────────────────────────────────────────────────────────────
def get_db():
    """
    Yield a SQLAlchemy session for use in FastAPI route dependencies.
    Automatically closes session after each request.

    Usage in route:
        def my_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────
# Health Check Helper
# ─────────────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """
    Verify database connectivity by running a lightweight query.
    Used by GET /health/db endpoint.

    Returns:
        True if connection is alive, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False
