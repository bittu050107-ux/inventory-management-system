"""
API Dependencies: dependencies.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dependency injection wiring — the ONLY place that knows
which concrete repository implementation to use.

Current wiring:
  UserRepository interface ← PostgreSQLUserRepository (PostgreSQL)

To swap to a different DB, change ONLY this file.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.dto.auth_dto import TokenVerifyResponse
from app.application.services.auth_service import AuthService
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.user_repository_impl import PostgreSQLUserRepository


# HTTP Bearer scheme for Swagger UI Authorize button and header extraction
bearer_scheme = HTTPBearer(
    auto_error=True,
    description="JWT Bearer token. Obtain from POST /auth/login.",
)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    FastAPI dependency: provides a configured AuthService with PostgreSQL.

    Wiring:
        1. get_db() provides a fresh SQLAlchemy session per request
        2. PostgreSQLUserRepository wraps that session
        3. AuthService receives the repository interface

    Usage in routes:
        @router.post("/login")
        def login(auth_service: AuthService = Depends(get_auth_service)):
            ...
    """
    repository = PostgreSQLUserRepository(db)
    return AuthService(user_repository=repository)


def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenVerifyResponse:
    """
    Extract Bearer token from Authorization header and validate via AuthService.

    Returns:
        TokenVerifyResponse with user_id and role decoded from JWT.

    Raises:
        HTTP 401 if token is missing, invalid, or expired.
    """
    token = credentials.credentials
    try:
        return auth_service.verify_token(token)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    RBAC guard factory. Returns a FastAPI dependency that
    validates the current user's role against allowed_roles.
    """
    def role_checker(
        token_data: TokenVerifyResponse = Depends(get_current_user_token),
    ) -> TokenVerifyResponse:
        if token_data.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied: Required role '{', '.join(allowed_roles)}', "
                    f"but user has role '{token_data.role}'."
                ),
            )
        return token_data

    return role_checker


# Preconfigured RBAC guards
require_admin = require_roles(["ADMIN"])
require_authenticated_user = require_roles(["ADMIN", "MANAGER", "STAFF", "USER"])
