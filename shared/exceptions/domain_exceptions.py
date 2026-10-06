"""
Shared Domain Exceptions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Custom exception classes used across microservices.
These are domain-level exceptions (no HTTP/FastAPI coupling).
The API layer is responsible for mapping these to HTTP codes.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""
    pass


class AuthorizationError(Exception):
    """Raised when a user lacks permission for an action."""
    pass


class TokenExpiredError(Exception):
    """Raised when a JWT token has expired."""
    pass


class TokenInvalidError(Exception):
    """Raised when a JWT token is malformed or tampered with."""
    pass


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: str) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id '{identifier}' not found.")


class DuplicateResourceError(Exception):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource: str, field: str, value: str) -> None:
        self.resource = resource
        self.field = field
        self.value = value
        super().__init__(f"{resource} with {field} '{value}' already exists.")
