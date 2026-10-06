"""
Domain Repository Interface: CategoryRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract interface defining category data access contracts.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.category import Category


class CategoryRepository(ABC):
    """Abstract category persistence contract."""

    @abstractmethod
    def create(self, category: Category) -> Category:
        """Persist a new category and return saved entity with id."""
        ...

    @abstractmethod
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Fetch category by its integer primary key."""
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Category]:
        """Fetch category by exact name (for uniqueness validation)."""
        ...

    @abstractmethod
    def get_all(self) -> List[Category]:
        """Fetch all categories."""
        ...

    @abstractmethod
    def update(self, category: Category) -> Optional[Category]:
        """Update existing category details and return updated entity."""
        ...

    @abstractmethod
    def delete(self, category_id: int) -> bool:
        """Delete category by id. Returns True if deleted, False if not found."""
        ...
