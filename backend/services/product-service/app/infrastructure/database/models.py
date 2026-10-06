"""
Infrastructure: SQLAlchemy ORM Models (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Defines tables for:
  - categories
  - suppliers
  - products

Includes relationships and database constraints.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.database import Base


class CategoryModel(Base):
    """
    SQLAlchemy model for the 'categories' table.
    """
    __tablename__ = "categories"

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    name: str = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )
    description: str = Column(
        Text,
        nullable=True,
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

    # Relationships
    products = relationship(
        "ProductModel",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CategoryModel id={self.id} name={self.name!r}>"


class SupplierModel(Base):
    """
    SQLAlchemy model for the 'suppliers' table.
    """
    __tablename__ = "suppliers"

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    name: str = Column(
        String(200),
        nullable=False,
        index=True,
    )
    email: str = Column(
        String(255),
        nullable=True,
    )
    phone: str = Column(
        String(50),
        nullable=True,
    )
    address: str = Column(
        Text,
        nullable=True,
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

    # Relationships
    products = relationship(
        "ProductModel",
        back_populates="supplier",
    )

    def __repr__(self) -> str:
        return f"<SupplierModel id={self.id} name={self.name!r}>"


class ProductModel(Base):
    """
    SQLAlchemy model for the 'products' table.
    """
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price_non_negative"),
    )

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    name: str = Column(
        String(255),
        nullable=False,
        index=True,
    )
    sku: str = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    description: str = Column(
        Text,
        nullable=True,
    )
    price: Decimal = Column(
        Numeric(10, 2),
        nullable=False,
    )
    category_id: int = Column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    supplier_id: int = Column(
        Integer,
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: bool = Column(
        Boolean,
        default=True,
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

    # Relationships
    category = relationship(
        "CategoryModel",
        back_populates="products",
    )
    supplier = relationship(
        "SupplierModel",
        back_populates="products",
    )

    def __repr__(self) -> str:
        return f"<ProductModel id={self.id} sku={self.sku!r} name={self.name!r}>"
