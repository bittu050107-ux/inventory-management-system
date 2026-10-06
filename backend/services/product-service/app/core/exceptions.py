"""
Core Exceptions: exceptions.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Custom application exceptions mapped cleanly to HTTP status codes
in route handlers.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class ProductAppException(Exception):
    """Base exception for Product Service domain/application errors."""
    pass


class NotFoundError(ProductAppException):
    """Resource not found (HTTP 404)."""
    pass


class DuplicateResourceError(ProductAppException):
    """Duplicate unique constraint violation (HTTP 409)."""
    pass


class BusinessRuleError(ProductAppException):
    """Business rule validation failure (HTTP 400)."""
    pass
