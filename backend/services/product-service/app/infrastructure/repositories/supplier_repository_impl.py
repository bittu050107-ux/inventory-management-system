"""
Infrastructure Repository: SupplierRepositoryImpl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL implementation of SupplierRepository via SQLAlchemy.
Translates between SupplierModel (ORM) and Supplier (domain entity).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities.supplier import Supplier
from app.domain.repositories.supplier_repository import SupplierRepository
from app.infrastructure.database.models import SupplierModel


class SupplierRepositoryImpl(SupplierRepository):
    """PostgreSQL-backed Supplier repository implementation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: SupplierModel) -> Supplier:
        """Map ORM model to domain entity."""
        return Supplier(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            address=model.address,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def create(self, supplier: Supplier) -> Supplier:
        db_supplier = SupplierModel(
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
        )
        self._db.add(db_supplier)
        self._db.commit()
        self._db.refresh(db_supplier)
        return self._to_domain(db_supplier)

    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        model = (
            self._db.query(SupplierModel)
            .filter(SupplierModel.id == supplier_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_all(self) -> List[Supplier]:
        models = self._db.query(SupplierModel).order_by(SupplierModel.id).all()
        return [self._to_domain(m) for m in models]

    def update(self, supplier: Supplier) -> Optional[Supplier]:
        db_supplier = (
            self._db.query(SupplierModel)
            .filter(SupplierModel.id == supplier.id)
            .first()
        )
        if not db_supplier:
            return None

        db_supplier.name = supplier.name
        db_supplier.email = supplier.email
        db_supplier.phone = supplier.phone
        db_supplier.address = supplier.address
        self._db.commit()
        self._db.refresh(db_supplier)
        return self._to_domain(db_supplier)

    def delete(self, supplier_id: int) -> bool:
        db_supplier = (
            self._db.query(SupplierModel)
            .filter(SupplierModel.id == supplier_id)
            .first()
        )
        if not db_supplier:
            return False

        self._db.delete(db_supplier)
        self._db.commit()
        return True
