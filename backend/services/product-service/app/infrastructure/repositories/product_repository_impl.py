"""
Infrastructure Repository: ProductRepositoryImpl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL implementation of ProductRepository via SQLAlchemy.
Translates between ProductModel (ORM) and Product (domain entity).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.database.models import ProductModel


class ProductRepositoryImpl(ProductRepository):
    """PostgreSQL-backed Product repository implementation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: ProductModel) -> Product:
        """Map ORM model to domain entity."""
        return Product(
            id=model.id,
            name=model.name,
            sku=model.sku,
            description=model.description,
            price=float(model.price),
            category_id=model.category_id,
            supplier_id=model.supplier_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def create(self, product: Product) -> Product:
        db_product = ProductModel(
            name=product.name,
            sku=product.sku,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            supplier_id=product.supplier_id,
            is_active=product.is_active,
        )
        self._db.add(db_product)
        self._db.commit()
        self._db.refresh(db_product)
        return self._to_domain(db_product)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        model = (
            self._db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_by_sku(self, sku: str) -> Optional[Product]:
        model = (
            self._db.query(ProductModel)
            .filter(ProductModel.sku == sku)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        models = (
            self._db.query(ProductModel)
            .order_by(ProductModel.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def update(self, product: Product) -> Optional[Product]:
        db_product = (
            self._db.query(ProductModel)
            .filter(ProductModel.id == product.id)
            .first()
        )
        if not db_product:
            return None

        db_product.name = product.name
        db_product.sku = product.sku
        db_product.description = product.description
        db_product.price = product.price
        db_product.category_id = product.category_id
        db_product.supplier_id = product.supplier_id
        db_product.is_active = product.is_active

        self._db.commit()
        self._db.refresh(db_product)
        return self._to_domain(db_product)

    def delete(self, product_id: int) -> bool:
        db_product = (
            self._db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        if not db_product:
            return False

        self._db.delete(db_product)
        self._db.commit()
        return True

    def count_by_category(self, category_id: int) -> int:
        return (
            self._db.query(ProductModel)
            .filter(ProductModel.category_id == category_id)
            .count()
        )

    def count_by_supplier(self, supplier_id: int) -> int:
        return (
            self._db.query(ProductModel)
            .filter(ProductModel.supplier_id == supplier_id)
            .count()
        )
