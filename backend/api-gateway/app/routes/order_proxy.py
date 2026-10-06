"""
API Gateway Proxy Routes: order_proxy.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reverse proxy endpoints for the Order Microservice:
  - POST   /api/orders
  - GET    /api/orders
  - GET    /api/orders/my
  - GET    /api/orders/{order_id}
  - PATCH  /api/orders/{order_id}/status
  - PUT    /api/orders/{order_id}/status
  - POST   /api/orders/{order_id}/cancel
  - DELETE /api/orders/{order_id}

Forwards all requests with Authorization header to ORDER_SERVICE_URL (:8005).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, Request
from app.core.config import settings
from app.middleware.auth import extract_forward_headers, forward_request

router = APIRouter(prefix="/api/orders", tags=["Order Service Proxy"])

SERVICE_NAME = "Order service"


@router.post("", summary="Proxy: Create Order")
async def proxy_create_order(request: Request):
    """Forward order creation to Order Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.get("", summary="Proxy: List Orders")
async def proxy_list_orders(request: Request):
    """Forward order listing to Order Service."""
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders",
        method="GET",
        headers=extract_forward_headers(request),
        params=dict(request.query_params),
        service_name=SERVICE_NAME,
    )


@router.get("/my", summary="Proxy: List Caller's Own Orders")
async def proxy_my_orders(request: Request):
    """Forward my orders listing to Order Service."""
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders/my",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.get("/{order_id}", summary="Proxy: Get Order Details")
async def proxy_get_order(request: Request, order_id: str):
    """Forward get order by ID to Order Service."""
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders/{order_id}",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.patch("/{order_id}/status", summary="Proxy: Update Order Status (PATCH)")
@router.put("/{order_id}/status", summary="Proxy: Update Order Status (PUT)")
async def proxy_update_order_status(request: Request, order_id: str):
    """Forward status update to Order Service (accepts both PATCH and PUT)."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders/{order_id}/status",
        method="PATCH",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.post("/{order_id}/cancel", summary="Proxy: Cancel Order")
async def proxy_cancel_order(request: Request, order_id: str):
    """Forward cancel order to Order Service."""
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders/{order_id}/cancel",
        method="POST",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.delete("/{order_id}", summary="Proxy: Delete Order")
async def proxy_delete_order(request: Request, order_id: str):
    """Forward delete order to Order Service."""
    return await forward_request(
        target_url=f"{settings.ORDER_SERVICE_URL}/orders/{order_id}",
        method="DELETE",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )
