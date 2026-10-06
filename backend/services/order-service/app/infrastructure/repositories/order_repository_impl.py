"""
Infrastructure Repository: PostgreSQLOrderRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Concrete implementation of the OrderRepository interface.
Uses SQLAlchemy ORM to talk to PostgreSQL.

This is the ONLY place in the service that contains SQL logic.
Business logic stays in OrderService (application layer).

Implements:
  - create       → Insert order + items atomically
  - get_by_id    → Fetch with joined items
  - get_all      → All orders (admin view)
  - get_by_user_id → Orders for a specific user
  - update_status  → Update status + updated_at
  - delete         → Hard delete by ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.order import Order, OrderItem
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.models import OrderItemModel, OrderModel


def _model_to_item(model: OrderItemModel) -> OrderItem:
    """Convert ORM OrderItemModel → domain OrderItem."""
    item = OrderItem(
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=model.unit_price,
    )
    item.id = model.id
    item.order_id = model.order_id
    return item


def _model_to_order(model: OrderModel) -> Order:
    """Convert ORM OrderModel → domain Order entity."""
    order = Order(
        user_id=model.user_id,
        status=model.status,
        notes=model.notes,
        items=[_model_to_item(i) for i in model.items],
    )
    order.id = model.id
    order.created_at = model.created_at
    order.updated_at = model.updated_at
    return order


class PostgreSQLOrderRepository(OrderRepository):
    """
    PostgreSQL-backed implementation of OrderRepository.

    Args:
        db: SQLAlchemy Session injected via FastAPI dependency.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, order: Order) -> Order:
        """
        Persist a new Order and all its OrderItems atomically.
        Computes total_amount as sum of item totals before saving.
        """
        # Build ORM model for the order
        order_model = OrderModel(
            user_id=order.user_id,
            status=order.status,
            notes=order.notes,
            total_amount=order.total_amount,
        )
        self._db.add(order_model)
        self._db.flush()  # Get order_model.id before adding items

        # Add each item linked to the parent order
        for item in order.items:
            item_model = OrderItemModel(
                order_id=order_model.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            self._db.add(item_model)

        self._db.commit()
        self._db.refresh(order_model)
        return _model_to_order(order_model)

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Fetch a single order with its items by primary key."""
        model = self._db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not model:
            return None
        return _model_to_order(model)

    def get_all(self) -> List[Order]:
        """Fetch all orders — ordered by newest first."""
        models = (
            self._db.query(OrderModel)
            .order_by(OrderModel.created_at.desc())
            .all()
        )
        return [_model_to_order(m) for m in models]

    def get_by_user_id(self, user_id: str) -> List[Order]:
        """Fetch all orders belonging to a specific user."""
        models = (
            self._db.query(OrderModel)
            .filter(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .all()
        )
        return [_model_to_order(m) for m in models]

    def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        """Update an order's status. Returns updated Order or None if not found."""
        model = self._db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not model:
            return None

        model.status = new_status
        self._db.commit()
        self._db.refresh(model)
        return _model_to_order(model)

    def delete(self, order_id: int) -> bool:
        """Hard-delete an order (and its items via cascade). Returns True if deleted."""
        model = self._db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not model:
            return False

        self._db.delete(model)
        self._db.commit()
        return True
