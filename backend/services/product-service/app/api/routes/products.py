"""
API Routes: products.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product CRUD endpoints.
Admin only: POST, PUT, DELETE
Authenticated users: GET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_product_service,
    get_current_user,
    require_admin,
)
from app.application.dto.product_dto import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from app.application.services.product_service import ProductService
from app.core.exceptions import (
    NotFoundError,
    DuplicateResourceError,
    BusinessRuleError,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product (Admin only)",
)
def create_product(
    request: ProductCreateRequest,
    service: ProductService = Depends(get_product_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> ProductResponse:
    """
    Create a new product.
    Requires ADMIN role.
    Validates category, supplier, and SKU uniqueness.
    """
    try:
        return service.create_product(request)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="List all products (Authenticated)",
)
def list_products(
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    limit: int = Query(default=100, ge=1, le=500, description="Page limit"),
    service: ProductService = Depends(get_product_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[ProductResponse]:
    """List products with pagination. Accessible by any authenticated user."""
    return service.get_all_products(skip=skip, limit=limit)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID (Authenticated)",
)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> ProductResponse:
    """Get single product details. Accessible by any authenticated user."""
    try:
        return service.get_product_by_id(product_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product (Admin only)",
)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    service: ProductService = Depends(get_product_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> ProductResponse:
    """Update product details. Requires ADMIN role."""
    try:
        return service.update_product(product_id, request)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product (Admin only)",
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> None:
    """Delete a product. Requires ADMIN role."""
    try:
        service.delete_product(product_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
