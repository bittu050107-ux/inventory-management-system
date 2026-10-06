"""
API Dependencies: dependencies.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dependency injection for:
  - Database sessions (SQLAlchemy)
  - Repositories and Application Services
  - JWT verification and RBAC guards (get_current_user, require_admin)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from app.infrastructure.repositories.supplier_repository_impl import SupplierRepositoryImpl
from app.infrastructure.repositories.product_repository_impl import ProductRepositoryImpl
from app.application.services.category_service import CategoryService
from app.application.services.supplier_service import SupplierService
from app.application.services.product_service import ProductService


# HTTP Bearer authentication scheme for OpenAPI / Swagger Authorize button
bearer_scheme = HTTPBearer(
    auto_error=True,
    description="JWT Bearer token. Enter as: Bearer <token>",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Validate JWT Bearer token and extract user credentials.

    Returns:
        Dict with 'user_id' and 'role'.

    Raises:
        HTTP 401 if missing, invalid, or expired.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing required claims (sub or role)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": str(user_id),
            "role": str(role),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Ensure the caller has the 'ADMIN' role.

    Raises:
        HTTP 403 Forbidden if user is authenticated but not an ADMIN.
    """
    role = current_user.get("role")
    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required",
        )
    return current_user


# ─────────────────────────────────────────────────────────────
# Service Dependency Providers
# ─────────────────────────────────────────────────────────────

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Provide CategoryService wired with repositories."""
    category_repo = CategoryRepositoryImpl(db)
    product_repo = ProductRepositoryImpl(db)
    return CategoryService(category_repo, product_repo)


def get_supplier_service(db: Session = Depends(get_db)) -> SupplierService:
    """Provide SupplierService wired with repositories."""
    supplier_repo = SupplierRepositoryImpl(db)
    product_repo = ProductRepositoryImpl(db)
    return SupplierService(supplier_repo, product_repo)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Provide ProductService wired with repositories."""
    product_repo = ProductRepositoryImpl(db)
    category_repo = CategoryRepositoryImpl(db)
    supplier_repo = SupplierRepositoryImpl(db)
    return ProductService(product_repo, category_repo, supplier_repo)
