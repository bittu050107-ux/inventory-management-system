"""
Domain Entity: Inventory
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure Python representation of product stock levels.
Contains zero database or ORM dependencies.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Inventory:
    """Inventory domain entity representing stock for a single product."""
    product_id: int
    quantity: int = 0
    reorder_level: int = 10
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_low_stock(self) -> bool:
        """Return True if current stock is at or below reorder threshold."""
        return self.quantity <= self.reorder_level
