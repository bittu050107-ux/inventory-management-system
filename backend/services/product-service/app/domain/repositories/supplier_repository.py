"""
Domain Repository Interface: SupplierRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract interface defining supplier data access contracts.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.supplier import Supplier


class SupplierRepository(ABC):
    """Abstract supplier persistence contract."""

    @abstractmethod
    def create(self, supplier: Supplier) -> Supplier:
        """Persist a new supplier and return saved entity with id."""
        ...

    @abstractmethod
    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Fetch supplier by primary key."""
        ...

    @abstractmethod
    def get_all(self) -> List[Supplier]:
        """Fetch all suppliers."""
        ...

    @abstractmethod
    def update(self, supplier: Supplier) -> Optional[Supplier]:
        """Update existing supplier details and return updated entity."""
        ...

    @abstractmethod
    def delete(self, supplier_id: int) -> bool:
        """Delete supplier by id. Returns True if deleted, False if not found."""
        ...
