"""
API Gateway Proxy Routes: inventory_proxy.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reverse proxy endpoints for the Inventory Microservice:
  - GET  /api/inventory
  - GET  /api/inventory/low-stock
  - GET  /api/inventory/{product_id}
  - POST /api/inventory/stock-in
  - POST /api/inventory/stock-out
  - POST /api/inventory/adjust
  - GET  /api/inventory/{product_id}/transactions

Forwards all requests with Authorization header to INVENTORY_SERVICE_URL (:8004).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, Request, status
from app.core.config import settings
from app.middleware.auth import extract_forward_headers, forward_request

router = APIRouter(prefix="/api/inventory", tags=["Inventory Service Proxy"])

SERVICE_NAME = "Inventory service"


@router.get("", summary="Proxy: Get all inventory")
async def proxy_get_all_inventory(request: Request):
    """Forward list inventory to Inventory Service."""
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory",
        method="GET",
        headers=extract_forward_headers(request),
        params=dict(request.query_params),
        service_name=SERVICE_NAME,
    )


@router.get("/low-stock", summary="Proxy: Get low stock alerts")
async def proxy_get_low_stock(request: Request):
    """Forward low stock check to Inventory Service."""
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/low-stock",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.get("/{product_id}", summary="Proxy: Get inventory for product")
async def proxy_get_inventory_by_product_id(request: Request, product_id: int):
    """Forward product inventory retrieval to Inventory Service."""
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/{product_id}",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.get("/{product_id}/transactions", summary="Proxy: Get transaction history")
async def proxy_get_transactions(request: Request, product_id: int):
    """Forward transaction history retrieval to Inventory Service."""
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/{product_id}/transactions",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.post("/stock-in", summary="Proxy: Stock-In")
async def proxy_stock_in(request: Request):
    """Forward stock-in request to Inventory Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/stock-in",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.post("/stock-out", summary="Proxy: Stock-Out")
async def proxy_stock_out(request: Request):
    """Forward stock-out request to Inventory Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/stock-out",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.post("/adjust", summary="Proxy: Stock Adjustment")
async def proxy_adjust_stock(request: Request):
    """Forward stock adjustment request to Inventory Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.INVENTORY_SERVICE_URL}/inventory/adjust",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )
