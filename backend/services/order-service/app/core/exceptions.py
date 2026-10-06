"""
Core Exceptions: exceptions.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Custom application-level exceptions.
Each maps to a specific HTTP status code in the API layer.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class OrderAppException(Exception):
    """Base exception for all order application errors."""
    pass


class NotFoundError(OrderAppException):
    """Order or related resource not found (HTTP 404)."""
    pass


class ProductNotFoundError(NotFoundError):
    """Product does not exist in Product Service (HTTP 404)."""
    pass


class InsufficientStockError(OrderAppException):
    """Requested order quantity exceeds available stock (HTTP 400)."""
    pass


class BusinessRuleError(OrderAppException):
    """General business rule violation (HTTP 400)."""
    pass


class OrderStatusError(OrderAppException):
    """Invalid order status transition (HTTP 400)."""
    pass
