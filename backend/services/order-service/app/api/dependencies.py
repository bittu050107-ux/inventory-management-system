"""
API Dependencies: dependencies.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI dependency functions providing:
  - JWT Bearer extraction and validation (get_current_user)
  - Role-based access control (require_roles)
  - OrderService dependency injection (get_order_service)

These are injected into route handlers via FastAPI's
Depends() mechanism — no business logic lives here.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Any, Callable, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services.order_service import OrderService
from app.core.security import decode_access_token
from app.infrastructure.database.database import get_db
from app.infrastructure.external.inventory_client import InventoryServiceClient
from app.infrastructure.repositories.order_repository_impl import (
    PostgreSQLOrderRepository,
)


# ─────────────────────────────────────────────────────────────
# Bearer Token Extraction
# ─────────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer(
    auto_error=True,
    description="JWT Bearer token. Format: Bearer <token>",
)


# ─────────────────────────────────────────────────────────────
# Current User from JWT
# ─────────────────────────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Extract and validate JWT from the Authorization header.

    Returns a dict with:
        - user_id (str)  → JWT 'sub' claim
        - role    (str)  → JWT 'role' claim (uppercased)
        - token   (str)  → raw JWT (forwarded to downstream services)

    Raises:
        HTTPException 401 if token is missing, expired, or invalid.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing required claims (sub or role)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": str(user_id),
            "role": str(role).upper(),
            "token": token,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────────────────────
# Role-Based Access Control
# ─────────────────────────────────────────────────────────────
def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Factory that returns a FastAPI dependency enforcing role access.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_admin)])
    """
    def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        role = current_user.get("role", "")
        if role not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Forbidden: Action requires one of {allowed_roles}, "
                    f"but caller has role '{role}'"
                ),
            )
        return current_user

    return role_checker


# ─────────────────────────────────────────────────────────────
# Preconfigured RBAC guards
# ─────────────────────────────────────────────────────────────

# Any authenticated user can create an order or view their own
require_authenticated = require_roles(["ADMIN", "MANAGER", "STAFF", "USER"])

# Only ADMIN and MANAGER can view all orders or change status
require_manager_or_admin = require_roles(["ADMIN", "MANAGER"])

# Only ADMIN can delete orders
require_admin = require_roles(["ADMIN"])


# ─────────────────────────────────────────────────────────────
# Service Dependency Injection
# ─────────────────────────────────────────────────────────────
def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """
    Build and return an OrderService with all dependencies injected.

    Wires together:
      - PostgreSQLOrderRepository (concrete DB implementation)
      - InventoryServiceClient    (HTTP adapter)
    """
    repo = PostgreSQLOrderRepository(db)
    inventory_client = InventoryServiceClient()
    return OrderService(repo, inventory_client)
