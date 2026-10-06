"""
Domain Repository Interface: InventoryRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract contract for Inventory and StockTransaction persistence.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from app.domain.entities.inventory import Inventory
from app.domain.entities.stock_transaction import StockTransaction


class InventoryRepository(ABC):
    """Abstract persistence interface for inventory and transaction logs."""

    @abstractmethod
    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        """Fetch inventory record by product_id."""
        ...

    @abstractmethod
    def get_all(self) -> List[Inventory]:
        """Fetch all inventory records."""
        ...

    @abstractmethod
    def get_low_stock(self) -> List[Inventory]:
        """Fetch inventory records where quantity <= reorder_level."""
        ...

    @abstractmethod
    def create_or_update(self, inventory: Inventory) -> Inventory:
        """Create new inventory record or update existing one."""
        ...

    @abstractmethod
    def record_transaction(self, transaction: StockTransaction) -> StockTransaction:
        """Log a stock movement event."""
        ...

    @abstractmethod
    def get_transactions_by_product_id(self, product_id: int) -> List[StockTransaction]:
        """Retrieve audit history for a specific product."""
        ...

    @abstractmethod
    def apply_stock_change_atomic(
        self, inventory: Inventory, transaction: StockTransaction
    ) -> Tuple[Inventory, StockTransaction]:
        """
        Atomically save/update inventory and record stock transaction in a single DB commit.
        Rolls back both if either fails.
        """
        ...
