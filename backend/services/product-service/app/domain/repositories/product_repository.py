"""
Domain Repository Interface: ProductRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract interface defining product data access contracts.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.product import Product


class ProductRepository(ABC):
    """Abstract product persistence contract."""

    @abstractmethod
    def create(self, product: Product) -> Product:
        """Persist a new product and return saved entity with id."""
        ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Fetch product by primary key."""
        ...

    @abstractmethod
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Fetch product by unique SKU."""
        ...

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Fetch all products with pagination."""
        ...

    @abstractmethod
    def update(self, product: Product) -> Optional[Product]:
        """Update existing product details and return updated entity."""
        ...

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Delete product by id. Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    def count_by_category(self, category_id: int) -> int:
        """Count products associated with a specific category."""
        ...

    @abstractmethod
    def count_by_supplier(self, supplier_id: int) -> int:
        """Count products associated with a specific supplier."""
        ...
