"""
Domain Repository Interface: OrderRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract interface (Port) defining ALL database operations
that the Order domain requires.

The infrastructure layer (PostgreSQLOrderRepository) provides
the concrete implementation. The application layer (OrderService)
depends on this interface — never on SQL directly.

This is the Dependency Inversion Principle (DIP) in practice:
  High-level business logic → Abstract interface → Database
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.order import Order


class OrderRepository(ABC):
    """Abstract repository contract for Order persistence."""

    @abstractmethod
    def create(self, order: Order) -> Order:
        """
        Persist a new order with all its items atomically.

        Args:
            order: Fully populated Order domain entity (no id yet).

        Returns:
            The saved Order with id, created_at, and updated_at filled in.
        """
        ...

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Fetch a single order by its primary key.

        Args:
            order_id: The order's primary key.

        Returns:
            The Order entity with items, or None if not found.
        """
        ...

    @abstractmethod
    def get_all(self) -> List[Order]:
        """
        Fetch all orders (admin view).

        Returns:
            List of all Order entities (each includes their items).
        """
        ...

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[Order]:
        """
        Fetch all orders placed by a specific user.

        Args:
            user_id: The user's sub claim string from JWT.

        Returns:
            List of orders belonging to the user.
        """
        ...

    @abstractmethod
    def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        """
        Update the status of an order.

        Args:
            order_id:   Primary key of the target order.
            new_status: One of PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED.

        Returns:
            Updated Order entity, or None if order was not found.
        """
        ...

    @abstractmethod
    def delete(self, order_id: int) -> bool:
        """
        Hard-delete an order by ID (admin-only).

        Args:
            order_id: Primary key of the order to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...
