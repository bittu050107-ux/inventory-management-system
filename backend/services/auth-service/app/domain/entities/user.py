"""
Domain Entity: User
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is a pure Python dataclass — it has ZERO dependency on
FastAPI, SQLAlchemy, or any framework. It simply represents
what a "User" means in our business domain.

Clean Architecture Rule:
  Domain layer does NOT import from infrastructure or framework.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass, field
from enum import Enum


class UserRole(str, Enum):
    """
    Supported user roles for RBAC (Role-Based Access Control).

    - ADMIN   : Full system access (manage all resources)
    - MANAGER : Can manage products, inventory, orders
    - STAFF   : Can view and update inventory
    - USER    : Basic access (own profile, own orders)
    """
    ADMIN   = "ADMIN"
    MANAGER = "MANAGER"
    STAFF   = "STAFF"
    USER    = "USER"


@dataclass
class User:
    """
    Domain entity representing a User in the system.

    This is the core business object — it does NOT know about
    databases, HTTP, or any external system. This makes it
    easy to test and reason about in isolation.

    Fields:
        id       : Unique identifier (UUID string or int)
        email    : User's email address (must be unique)
        password : Hashed password (plain-text for now, bcrypt-ready)
        role     : User's role (defaults to USER for safety)
    """
    id:       str
    email:    str
    password: str
    role:     UserRole = field(default=UserRole.USER)

    def has_role(self, role: UserRole) -> bool:
        """Check if this user has a specific role."""
        return self.role == role

    def is_admin(self) -> bool:
        """Convenience: check if user is an ADMIN."""
        return self.role == UserRole.ADMIN
