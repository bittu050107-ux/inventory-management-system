"""
Domain Entity: Product
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure Python representation of a product.
Contains zero database or ORM dependencies.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union


@dataclass
class Product:
    """Product domain entity."""
    name: str
    sku: str
    price: Union[float, Decimal]
    category_id: int
    supplier_id: int
    id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
