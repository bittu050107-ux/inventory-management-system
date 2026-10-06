"""
API Dependencies: dependencies.py (Inventory Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provides:
  - Database session dependency (get_db)
  - JWT Bearer extraction and validation (get_current_user)
  - Role-based access control (require_roles)
  - InventoryService dependency injection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.inventory_repository_impl import InventoryRepositoryImpl
from app.infrastructure.external.product_client import ProductServiceClient
from app.application.services.inventory_service import InventoryService


bearer_scheme = HTTPBearer(
    auto_error=True,
    description="JWT Bearer token. Enter as: Bearer <token>",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Decode JWT and identify user_id, role, and pass token.
    Raises 401 if missing, invalid, or expired.
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


def require_roles(allowed_roles: List[str]) -> Callable:
    """RBAC dependency factory checking user role."""
    def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        role = current_user.get("role")
        if role not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of {allowed_roles}, but caller has '{role}'",
            )
        return current_user

    return role_checker


# Preconfigured RBAC guards:
# 1. READ: ADMIN, MANAGER, STAFF, USER
require_read_access = require_roles(["ADMIN", "MANAGER", "STAFF", "USER"])

# 2. STOCK-IN and STOCK-OUT: ADMIN, MANAGER, STAFF
require_stock_movement = require_roles(["ADMIN", "MANAGER", "STAFF"])

# 3. ADJUSTMENT: ADMIN, MANAGER
require_stock_adjustment = require_roles(["ADMIN", "MANAGER"])


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Dependency injecting repository and product client into service."""
    repo = InventoryRepositoryImpl(db)
    client = ProductServiceClient()
    return InventoryService(repo, client)
