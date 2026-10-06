"""
API Gateway Proxy Routes: proxy.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Defines explicit proxy routes for forwarding incoming client
requests to the respective downstream microservices.

Current Scope:
  - POST /api/auth/login      → Forward to Auth Service /auth/login
  - GET  /api/auth/me         → Forward to Auth Service /auth/me
  - GET  /api/auth/admin-test → Forward to Auth Service /auth/admin-test

Future Scope (scaffolded, not yet active):
  - /api/users/*
  - /api/products/*
  - /api/inventory/*
  - /api/orders/*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.middleware.auth import extract_forward_headers, forward_request

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication Proxy"],
)


# ─────────────────────────────────────────────────────────────
# Pydantic Schemas for Swagger Documentation on the Gateway
# ─────────────────────────────────────────────────────────────

class GatewayLoginRequest(BaseModel):
    """
    Login request schema for API Gateway client requests.
    """
    email: EmailStr = Field(
        ...,
        description="Registered user email",
        example="admin@inventory.com",
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
        example="admin123",
    )


class GatewayLoginResponse(BaseModel):
    """
    Login response schema returned from Auth Service.
    """
    access_token: str = Field(..., description="JWT Bearer token")
    token_type: str = Field(default="bearer", description="Token type")
    role: str = Field(..., description="Assigned user role")


class GatewayUserMeResponse(BaseModel):
    """
    Current user identity info returned from Auth Service.
    """
    user_id: str = Field(..., description="User unique identifier")
    role: str = Field(..., description="User role")


class GatewayAdminTestResponse(BaseModel):
    """
    Admin verification message returned from Auth Service.
    """
    message: str = Field(default="Welcome Admin", description="Status message")
    role: str = Field(..., description="User role")


# ─────────────────────────────────────────────────────────────
# Proxy Endpoints
# ─────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=GatewayLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Proxy: User Login",
    description=(
        "Forwards login credentials to the Auth Service at `POST /auth/login`. "
        "Returns the signed JWT access token and role."
    ),
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid email or password"},
        503: {"description": "Auth service unavailable"},
    }
)
async def proxy_login(request: Request, body: GatewayLoginRequest):
    """
    Forward client login request to Auth Service.
    """
    target_url = f"{settings.AUTH_SERVICE_URL}/auth/login"
    headers = extract_forward_headers(request)

    return await forward_request(
        target_url=target_url,
        method="POST",
        headers=headers,
        json_data=body.model_dump(),
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Proxy: User Registration",
    description="Forwards registration request to Auth Service at POST /auth/register.",
)
async def proxy_register(request: Request):
    """Forward client registration request to Auth Service."""
    target_url = f"{settings.AUTH_SERVICE_URL}/auth/register"
    headers = extract_forward_headers(request)
    body = await request.json() if await request.body() else {}

    return await forward_request(
        target_url=target_url,
        method="POST",
        headers=headers,
        json_data=body,
    )



@router.get(
    "/me",
    response_model=GatewayUserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Proxy: Get Current User",
    description=(
        "Forwards current user identity check to Auth Service at `GET /auth/me`. "
        "Must include `Authorization: Bearer <JWT>` header."
    ),
    responses={
        200: {"description": "User identity resolved"},
        401: {"description": "Missing, invalid, or expired token"},
        503: {"description": "Auth service unavailable"},
    }
)
async def proxy_get_me(request: Request):
    """
    Forward token verification request to Auth Service.
    Preserves Authorization header.
    """
    target_url = f"{settings.AUTH_SERVICE_URL}/auth/me"
    headers = extract_forward_headers(request)

    return await forward_request(
        target_url=target_url,
        method="GET",
        headers=headers,
    )


@router.get(
    "/admin-test",
    response_model=GatewayAdminTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Proxy: Admin Privilege Test",
    description=(
        "Forwards admin privilege check to Auth Service at `GET /auth/admin-test`. "
        "Requires valid JWT with role 'ADMIN'. Returns 403 Forbidden for non-admins."
    ),
    responses={
        200: {"description": "Admin access granted"},
        401: {"description": "Unauthenticated or invalid token"},
        403: {"description": "Forbidden — user lacks ADMIN role"},
        503: {"description": "Auth service unavailable"},
    }
)
async def proxy_admin_test(request: Request):
    """
    Forward admin role verification request to Auth Service.
    Preserves Authorization header.
    """
    target_url = f"{settings.AUTH_SERVICE_URL}/auth/admin-test"
    headers = extract_forward_headers(request)

    return await forward_request(
        target_url=target_url,
        method="GET",
        headers=headers,
    )
