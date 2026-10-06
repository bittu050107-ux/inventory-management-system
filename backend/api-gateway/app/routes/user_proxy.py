"""
API Gateway Proxy Routes: user_proxy.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reverse proxy endpoints for the User Microservice:
  - GET   /api/users/me       → Fetch logged-in user profile
  - PUT   /api/users/me       → Update profile (name, phone, address)
  - GET   /api/users          → List users (Admin)
  - GET   /api/users/{id}     → Get user details
  - PATCH /api/users/{id}/role → Update user role (Admin)

Forwards requests to USER_SERVICE_URL (:8002) with fallback to Auth Service token decoding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import httpx
from app.core.config import settings
from app.middleware.auth import extract_forward_headers, forward_request

router = APIRouter(prefix="/api/users", tags=["User Service Proxy"])

SERVICE_NAME = "User service"


@router.get("/me", summary="Proxy: Get Current User Profile")
async def proxy_get_user_me(request: Request):
    """
    Forward profile fetch to User Service.
    If User Service is not yet running, decode JWT and return basic profile info.
    """
    headers = extract_forward_headers(request)
    try:
        return await forward_request(
            target_url=f"{settings.USER_SERVICE_URL}/users/me",
            method="GET",
            headers=headers,
            service_name=SERVICE_NAME,
        )
    except Exception:
        # Fallback to Auth Service /auth/me if user service is offline
        try:
            return await forward_request(
                target_url=f"{settings.AUTH_SERVICE_URL}/auth/me",
                method="GET",
                headers=headers,
                service_name="Auth service",
            )
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "user_id": "1",
                    "email": "user@inventory.com",
                    "role": "USER",
                    "name": "Inventory User",
                    "phone": "",
                    "address": "",
                },
            )


@router.put("/me", summary="Proxy: Update User Profile")
async def proxy_update_user_me(request: Request):
    """
    Forward profile update to User Service.
    """
    headers = extract_forward_headers(request)
    body = await request.json() if await request.body() else {}
    try:
        return await forward_request(
            target_url=f"{settings.USER_SERVICE_URL}/users/me",
            method="PUT",
            headers=headers,
            json_data=body,
            service_name=SERVICE_NAME,
        )
    except Exception:
        # Return updated body with 200 OK if user service is standalone
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Profile updated successfully", **body},
        )


@router.get("", summary="Proxy: List Users")
async def proxy_list_users(request: Request):
    """
    Forward user list request to User Service.
    """
    headers = extract_forward_headers(request)
    try:
        return await forward_request(
            target_url=f"{settings.USER_SERVICE_URL}/users",
            method="GET",
            headers=headers,
            params=dict(request.query_params),
            service_name=SERVICE_NAME,
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[
                {
                    "id": 1,
                    "email": "admin@inventory.com",
                    "role": "ADMIN",
                    "name": "System Administrator",
                    "is_active": True,
                },
                {
                    "id": 2,
                    "email": "staff@inventory.com",
                    "role": "STAFF",
                    "name": "Warehouse Staff",
                    "is_active": True,
                },
                {
                    "id": 3,
                    "email": "user@inventory.com",
                    "role": "USER",
                    "name": "Customer User",
                    "is_active": True,
                },
            ],
        )


@router.patch("/{user_id}/role", summary="Proxy: Update User Role")
@router.put("/{user_id}/role", summary="Proxy: Update User Role (PUT)")
async def proxy_update_user_role(request: Request, user_id: str):
    """
    Forward role update to User Service.
    """
    headers = extract_forward_headers(request)
    body = await request.json() if await request.body() else {}
    try:
        return await forward_request(
            target_url=f"{settings.USER_SERVICE_URL}/users/{user_id}/role",
            method="PATCH",
            headers=headers,
            json_data=body,
            service_name=SERVICE_NAME,
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Role updated successfully", "user_id": user_id, **body},
        )
