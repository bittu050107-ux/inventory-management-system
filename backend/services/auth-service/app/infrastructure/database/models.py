"""
Infrastructure: SQLAlchemy ORM Model — users table
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is the DATABASE-SIDE representation of a user row.

Why keep this separate from the domain User entity?
  → Domain entity (user.py) has ZERO DB awareness.
  → This model has ZERO business logic.
  → They are mapped to each other by the infrastructure
    repository, which acts as a translator.

Clean Architecture Rule:
  Domain entity  ← translated by repository → ORM model
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.infrastructure.database.database import Base


class UserModel(Base):
    """
    SQLAlchemy ORM model mapped to the 'users' table in PostgreSQL.

    Columns:
        id            : Auto-incrementing integer primary key
        email         : Unique user email (indexed for fast lookups)
        password_hash : bcrypt hash — NEVER a plain-text password
        role          : Role string: ADMIN | MANAGER | STAFF | USER
        created_at    : Timestamp when the row was first inserted
        updated_at    : Timestamp automatically updated on every change
    """
    __tablename__ = "users"

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    email: str = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,       # Index speeds up find_by_email() queries
    )

    password_hash: str = Column(
        String(255),
        nullable=False,
        comment="bcrypt hash — never store plain-text passwords",
    )

    role: str = Column(
        String(50),
        nullable=False,
        default="USER",
        comment="Role: ADMIN | MANAGER | STAFF | USER",
    )

    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by PostgreSQL on INSERT
        nullable=False,
    )

    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),        # Auto-updated by SQLAlchemy on UPDATE
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email!r} role={self.role!r}>"
