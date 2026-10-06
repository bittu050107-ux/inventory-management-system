"""
Domain Entity: StockTransaction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure Python representation of an inventory transaction event.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    """Permitted stock transaction types."""
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"


@dataclass
class StockTransaction:
    """Stock transaction log domain entity."""
    product_id: int
    transaction_type: str
    quantity: int
    created_by: str
    id: Optional[int] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
