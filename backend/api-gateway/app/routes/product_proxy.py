"""
API Gateway Proxy Routes: product_proxy.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reverse proxy endpoints for the Product Microservice:
  - /api/categories
  - /api/suppliers
  - /api/products

Forwards all requests (with Authorization headers) to PRODUCT_SERVICE_URL (:8003).
Preserves HTTP status codes, error payloads, and query parameters.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional, Any, Dict
from fastapi import APIRouter, Request, status
from app.core.config import settings
from app.middleware.auth import extract_forward_headers, forward_request

router = APIRouter(prefix="/api", tags=["Product Service Proxy"])

SERVICE_NAME = "Product service"


# ─────────────────────────────────────────────────────────────
# Categories Proxy
# ─────────────────────────────────────────────────────────────

@router.post("/categories", status_code=status.HTTP_201_CREATED, summary="Proxy: Create Category")
async def proxy_create_category(request: Request):
    """Forward category creation to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/categories",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.get("/categories", summary="Proxy: List Categories")
async def proxy_list_categories(request: Request):
    """Forward list categories request to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/categories",
        method="GET",
        headers=extract_forward_headers(request),
        params=dict(request.query_params),
        service_name=SERVICE_NAME,
    )


@router.get("/categories/{category_id}", summary="Proxy: Get Category")
async def proxy_get_category(request: Request, category_id: int):
    """Forward get category by ID to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/categories/{category_id}",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.put("/categories/{category_id}", summary="Proxy: Update Category")
async def proxy_update_category(request: Request, category_id: int):
    """Forward category update to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/categories/{category_id}",
        method="PUT",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Proxy: Delete Category")
async def proxy_delete_category(request: Request, category_id: int):
    """Forward category deletion to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/categories/{category_id}",
        method="DELETE",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


# ─────────────────────────────────────────────────────────────
# Suppliers Proxy
# ─────────────────────────────────────────────────────────────

@router.post("/suppliers", status_code=status.HTTP_201_CREATED, summary="Proxy: Create Supplier")
async def proxy_create_supplier(request: Request):
    """Forward supplier creation to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/suppliers",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.get("/suppliers", summary="Proxy: List Suppliers")
async def proxy_list_suppliers(request: Request):
    """Forward list suppliers request to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/suppliers",
        method="GET",
        headers=extract_forward_headers(request),
        params=dict(request.query_params),
        service_name=SERVICE_NAME,
    )


@router.get("/suppliers/{supplier_id}", summary="Proxy: Get Supplier")
async def proxy_get_supplier(request: Request, supplier_id: int):
    """Forward get supplier by ID to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/suppliers/{supplier_id}",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.put("/suppliers/{supplier_id}", summary="Proxy: Update Supplier")
async def proxy_update_supplier(request: Request, supplier_id: int):
    """Forward supplier update to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/suppliers/{supplier_id}",
        method="PUT",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Proxy: Delete Supplier")
async def proxy_delete_supplier(request: Request, supplier_id: int):
    """Forward supplier deletion to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/suppliers/{supplier_id}",
        method="DELETE",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


# ─────────────────────────────────────────────────────────────
# Products Proxy
# ─────────────────────────────────────────────────────────────

@router.post("/products", status_code=status.HTTP_201_CREATED, summary="Proxy: Create Product")
async def proxy_create_product(request: Request):
    """Forward product creation to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/products",
        method="POST",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.get("/products", summary="Proxy: List Products")
async def proxy_list_products(request: Request):
    """Forward list products request to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/products",
        method="GET",
        headers=extract_forward_headers(request),
        params=dict(request.query_params),
        service_name=SERVICE_NAME,
    )


@router.get("/products/{product_id}", summary="Proxy: Get Product")
async def proxy_get_product(request: Request, product_id: int):
    """Forward get product by ID to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
        method="GET",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )


@router.put("/products/{product_id}", summary="Proxy: Update Product")
async def proxy_update_product(request: Request, product_id: int):
    """Forward product update to Product Service."""
    body = await request.json() if await request.body() else None
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
        method="PUT",
        headers=extract_forward_headers(request),
        json_data=body,
        service_name=SERVICE_NAME,
    )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Proxy: Delete Product")
async def proxy_delete_product(request: Request, product_id: int):
    """Forward product deletion to Product Service."""
    return await forward_request(
        target_url=f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
        method="DELETE",
        headers=extract_forward_headers(request),
        service_name=SERVICE_NAME,
    )
