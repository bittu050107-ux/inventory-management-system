"""
Domain Entity: Order
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure Python dataclass — NO SQLAlchemy, NO Pydantic.
This is the core business object of the Order domain.

An Order:
  - Belongs to a user (user_id from JWT)
  - Contains one or more OrderItems
  - Progresses through a status lifecycle:
      PENDING → CONFIRMED → SHIPPED → DELIVERED → CANCELLED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class OrderStatus(str, Enum):
    """
    Order lifecycle statuses.

    Transitions:
        PENDING    → Created but not yet confirmed by admin
        CONFIRMED  → Admin has confirmed and inventory reserved
        SHIPPED    → Order dispatched to delivery
        DELIVERED  → Order received by customer
        CANCELLED  → Order cancelled (by admin or user before shipping)
    """
    PENDING   = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED   = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItem:
    """
    A single line item within an Order.

    Attributes:
        product_id:  FK to Product Service product
        quantity:    Units ordered
        unit_price:  Price per unit at time of order (snapshot)
        id:          Assigned after DB persistence
        order_id:    Assigned after parent order is saved
        total_price: Derived field (quantity × unit_price)
    """
    product_id: int
    quantity: int
    unit_price: float
    id: Optional[int] = None
    order_id: Optional[int] = None

    @property
    def total_price(self) -> float:
        """Computed total for this line item."""
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    """
    Core Order aggregate root.

    Attributes:
        user_id:       ID of the placing user (from JWT sub claim)
        items:         List of OrderItem objects
        status:        Current lifecycle status
        notes:         Optional customer instructions or notes
        id:            Assigned after DB persistence
        total_amount:  Sum of all item totals (computed)
        created_at:    Timestamp of creation
        updated_at:    Timestamp of last update
    """
    user_id: str
    items: List[OrderItem] = field(default_factory=list)
    status: str = OrderStatus.PENDING.value
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def total_amount(self) -> float:
        """Sum of all line item totals."""
        return round(sum(item.total_price for item in self.items), 2)
