"""
Infrastructure: SQLAlchemy ORM Models (Inventory Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Defines tables:
  - inventory
  - stock_transactions

Rules:
  - product_id unique in inventory (one record per product)
  - quantity >= 0, reorder_level >= 0
  - stock_transactions quantity > 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.sql import func

from app.infrastructure.database.database import Base


class InventoryModel(Base):
    """SQLAlchemy model for 'inventory' table."""
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_inventory_quantity_non_negative"),
        CheckConstraint("reorder_level >= 0", name="check_inventory_reorder_level_non_negative"),
    )

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    product_id: int = Column(
        Integer,
        nullable=False,
        unique=True,
        index=True,
    )
    quantity: int = Column(
        Integer,
        default=0,
        nullable=False,
    )
    reorder_level: int = Column(
        Integer,
        default=10,
        nullable=False,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<InventoryModel id={self.id} product_id={self.product_id} qty={self.quantity}>"


class StockTransactionModel(Base):
    """SQLAlchemy model for 'stock_transactions' audit table."""
    __tablename__ = "stock_transactions"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_transaction_quantity_positive"),
    )

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    product_id: int = Column(
        Integer,
        nullable=False,
        index=True,
    )
    transaction_type: str = Column(
        String(20),
        nullable=False,
    )
    quantity: int = Column(
        Integer,
        nullable=False,
    )
    reference: str = Column(
        String(100),
        nullable=True,
    )
    notes: str = Column(
        Text,
        nullable=True,
    )
    created_by: str = Column(
        String(100),
        nullable=False,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<StockTransactionModel id={self.id} product_id={self.product_id} "
            f"type={self.transaction_type} qty={self.quantity}>"
        )
