"""
Infrastructure Repository: InventoryRepositoryImpl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL implementation of InventoryRepository via SQLAlchemy.
Translates between ORM models and domain entities.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.domain.entities.inventory import Inventory
from app.domain.entities.stock_transaction import StockTransaction
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.database.models import InventoryModel, StockTransactionModel


class InventoryRepositoryImpl(InventoryRepository):
    """PostgreSQL implementation of InventoryRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain_inventory(self, model: InventoryModel) -> Inventory:
        return Inventory(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            reorder_level=model.reorder_level,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_domain_transaction(self, model: StockTransactionModel) -> StockTransaction:
        return StockTransaction(
            id=model.id,
            product_id=model.product_id,
            transaction_type=model.transaction_type,
            quantity=model.quantity,
            reference=model.reference,
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
        )

    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        model = (
            self._db.query(InventoryModel)
            .filter(InventoryModel.product_id == product_id)
            .first()
        )
        return self._to_domain_inventory(model) if model else None

    def get_all(self) -> List[Inventory]:
        models = (
            self._db.query(InventoryModel)
            .order_by(InventoryModel.product_id)
            .all()
        )
        return [self._to_domain_inventory(m) for m in models]

    def get_low_stock(self) -> List[Inventory]:
        models = (
            self._db.query(InventoryModel)
            .filter(InventoryModel.quantity <= InventoryModel.reorder_level)
            .order_by(InventoryModel.product_id)
            .all()
        )
        return [self._to_domain_inventory(m) for m in models]

    def create_or_update(self, inventory: Inventory) -> Inventory:
        model = (
            self._db.query(InventoryModel)
            .filter(InventoryModel.product_id == inventory.product_id)
            .first()
        )
        if not model:
            model = InventoryModel(
                product_id=inventory.product_id,
                quantity=inventory.quantity,
                reorder_level=inventory.reorder_level,
            )
            self._db.add(model)
        else:
            model.quantity = inventory.quantity
            model.reorder_level = inventory.reorder_level

        self._db.commit()
        self._db.refresh(model)
        return self._to_domain_inventory(model)

    def record_transaction(self, transaction: StockTransaction) -> StockTransaction:
        tx_model = StockTransactionModel(
            product_id=transaction.product_id,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            reference=transaction.reference,
            notes=transaction.notes,
            created_by=transaction.created_by,
        )
        self._db.add(tx_model)
        self._db.commit()
        self._db.refresh(tx_model)
        return self._to_domain_transaction(tx_model)

    def get_transactions_by_product_id(self, product_id: int) -> List[StockTransaction]:
        models = (
            self._db.query(StockTransactionModel)
            .filter(StockTransactionModel.product_id == product_id)
            .order_by(StockTransactionModel.created_at.desc())
            .all()
        )
        return [self._to_domain_transaction(m) for m in models]

    def apply_stock_change_atomic(
        self, inventory: Inventory, transaction: StockTransaction
    ) -> Tuple[Inventory, StockTransaction]:
        """
        Atomically updates inventory quantity and logs the transaction.
        If an error occurs, both are rolled back.
        """
        try:
            # 1. Update or create inventory model
            inv_model = (
                self._db.query(InventoryModel)
                .filter(InventoryModel.product_id == inventory.product_id)
                .first()
            )
            if not inv_model:
                inv_model = InventoryModel(
                    product_id=inventory.product_id,
                    quantity=inventory.quantity,
                    reorder_level=inventory.reorder_level,
                )
                self._db.add(inv_model)
            else:
                inv_model.quantity = inventory.quantity
                inv_model.reorder_level = inventory.reorder_level

            # 2. Record transaction model
            tx_model = StockTransactionModel(
                product_id=transaction.product_id,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity,
                reference=transaction.reference,
                notes=transaction.notes,
                created_by=transaction.created_by,
            )
            self._db.add(tx_model)

            # 3. Commit both atomically
            self._db.commit()
            self._db.refresh(inv_model)
            self._db.refresh(tx_model)

            return (
                self._to_domain_inventory(inv_model),
                self._to_domain_transaction(tx_model),
            )
        except Exception:
            self._db.rollback()
            raise
