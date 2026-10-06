"""
API Routes: auth.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI route handlers for authentication endpoints.

Route Responsibilities (Clean Architecture Rule):
  ✅ Parse incoming HTTP request via DTOs
  ✅ Call application service methods
  ✅ Return HTTP response with appropriate status code
  ❌ No business logic (lives in AuthService)
  ❌ No database queries (lives in repository)

Endpoints:
  POST /auth/login         → Authenticate, return JWT
  POST /auth/register      → Create new USER account
  POST /auth/verify        → Validate a JWT token
  GET  /auth/me            → Get current user info from token
  GET  /auth/admin-test    → Admin-only protected route
  GET  /auth/user-only     → Any authenticated user
  GET  /health             → Service health check
  GET  /health/db          → Database connectivity check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_auth_service,
    get_current_user_token,
    require_admin,
    require_authenticated_user,
)
from app.application.dto.auth_dto import (
    AdminTestResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
    UserMeResponse,
)
from app.application.services.auth_service import AuthService
from app.infrastructure.database.database import check_db_connection

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Public Endpoints (no authentication required)
# ─────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and receive JWT token",
    tags=["Authentication"],
)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Authenticate with email and password.

    Returns a JWT Bearer token. Include in future requests as:
    `Authorization: Bearer <token>`
    """
    try:
        return auth_service.login(request)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    tags=["Authentication"],
)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    """
    Create a new user account.

    Role is always **USER** regardless of what is sent.
    Only admins can create ADMIN/MANAGER/STAFF accounts.
    """
    try:
        return auth_service.register(request)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        )


@router.post(
    "/verify",
    response_model=TokenVerifyResponse,
    summary="Verify a JWT token",
    tags=["Authentication"],
)
def verify_token(
    request: TokenVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenVerifyResponse:
    """
    Validate a JWT token and return its decoded claims.

    Used by the API Gateway to verify requests before forwarding.
    """
    try:
        return auth_service.verify_token(request.token)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        )


# ─────────────────────────────────────────────────────────────
# Authenticated Endpoints (valid JWT required)
# ─────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user info",
    tags=["User"],
)
def get_me(
    token_data: TokenVerifyResponse = Depends(get_current_user_token),
) -> UserMeResponse:
    """
    Decode token and return the currently authenticated user's info.

    Requires: Any valid JWT token.
    """
    return UserMeResponse(
        user_id=token_data.user_id,
        role=token_data.role,
    )


@router.get(
    "/user-only",
    summary="Any authenticated user endpoint",
    tags=["User"],
)
def user_only_endpoint(
    token_data: TokenVerifyResponse = Depends(require_authenticated_user),
):
    """
    Accessible by any authenticated user (USER, STAFF, MANAGER, ADMIN).

    Requires: Valid JWT token with any valid role.
    """
    return {
        "message": "You are a valid logged-in user",
        "user_id": token_data.user_id,
        "role": token_data.role,
    }


# ─────────────────────────────────────────────────────────────
# Admin-Only Endpoints
# ─────────────────────────────────────────────────────────────

@router.get(
    "/admin-test",
    response_model=AdminTestResponse,
    summary="Admin-only test route",
    tags=["Admin"],
)
def admin_test(
    token_data: TokenVerifyResponse = Depends(require_admin),
) -> AdminTestResponse:
    """
    Admin-only protected route.

    Requires: Valid JWT token with role == 'ADMIN'.
    Returns HTTP 403 for non-admins.
    """
    return AdminTestResponse(role=token_data.role)


# ─────────────────────────────────────────────────────────────
# Health Check Endpoints
# ─────────────────────────────────────────────────────────────

@router.get(
    "/health",
    summary="Auth Service health check",
    tags=["Health"],
)
def health_check():
    """Returns service liveness status."""
    return {"status": "healthy", "service": "auth-service"}


@router.get(
    "/health/db",
    summary="Database connectivity check",
    tags=["Health"],
)
def health_db():
    """
    Tests the connection to PostgreSQL.

    Returns HTTP 503 if the database is unreachable.
    """
    is_connected = check_db_connection()
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
    return {"status": "healthy", "database": "connected"}
