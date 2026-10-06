"""
Core Exceptions: exceptions.py (Inventory Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Custom application exceptions mapped to standard HTTP statuses.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class InventoryAppException(Exception):
    """Base exception for inventory application logic."""
    pass


class NotFoundError(InventoryAppException):
    """Resource not found (HTTP 404)."""
    pass


class ProductNotFoundError(NotFoundError):
    """Product does not exist in Product Service (HTTP 404)."""
    pass


class InsufficientStockError(InventoryAppException):
    """Requested stock-out exceeds available stock (HTTP 400)."""
    pass


class BusinessRuleError(InventoryAppException):
    """General business validation failure (HTTP 400)."""
    pass
