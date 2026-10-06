"""
Infrastructure: SQLAlchemy ORM Models — orders & order_items tables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
These are DATABASE-SIDE representation objects.
They are NOT domain entities (those live in app/domain/entities/).

Tables created:
  - orders       → one row per order
  - order_items  → one row per line item, FK → orders.id

Design notes:
  - total_amount is stored as a denormalized column (sum of items)
    for fast query without re-computation.
  - status is a VARCHAR with application-level enum enforcement.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.database import Base


def _now() -> datetime:
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class OrderModel(Base):
    """
    SQLAlchemy ORM model for the 'orders' table.

    Columns:
        id           → Auto-incremented primary key
        user_id      → JWT sub claim (string, not FK — users are in auth-service)
        status       → Lifecycle status (PENDING / CONFIRMED / SHIPPED / DELIVERED / CANCELLED)
        notes        → Optional delivery or customer notes
        total_amount → Denormalized sum of all item totals
        created_at   → Auto-set on creation
        updated_at   → Auto-updated on modification
    """
    __tablename__ = "orders"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(String(255), nullable=False, index=True)
    status       = Column(String(50), nullable=False, default="PENDING", index=True)
    notes        = Column(Text, nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    created_at   = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at   = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    # Relationship: one order has many items
    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",    # Always load items alongside order (avoids N+1 queries)
    )


class OrderItemModel(Base):
    """
    SQLAlchemy ORM model for the 'order_items' table.

    Columns:
        id          → Auto-incremented primary key
        order_id    → FK → orders.id (cascade delete)
        product_id  → ID of product (references Product Service — no FK constraint)
        quantity    → Number of units ordered
        unit_price  → Price per unit at time of order (immutable snapshot)
        total_price → quantity × unit_price (denormalized for speed)
    """
    __tablename__ = "order_items"

    id          = Column(Integer, primary_key=True, index=True)
    order_id    = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id  = Column(Integer, nullable=False, index=True)
    quantity    = Column(Integer, nullable=False)
    unit_price  = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationship back to parent order
    order = relationship("OrderModel", back_populates="items")
