"""
API Routes: suppliers.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Supplier CRUD endpoints.
Admin only: POST, PUT, DELETE
Authenticated users: GET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_supplier_service,
    get_current_user,
    require_admin,
)
from app.application.dto.supplier_dto import (
    SupplierCreateRequest,
    SupplierUpdateRequest,
    SupplierResponse,
)
from app.application.services.supplier_service import SupplierService
from app.core.exceptions import (
    NotFoundError,
    DuplicateResourceError,
    BusinessRuleError,
)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new supplier (Admin only)",
)
def create_supplier(
    request: SupplierCreateRequest,
    service: SupplierService = Depends(get_supplier_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> SupplierResponse:
    """Create a new supplier. Requires ADMIN role."""
    try:
        return service.create_supplier(request)
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get(
    "",
    response_model=List[SupplierResponse],
    summary="List all suppliers (Authenticated)",
)
def list_suppliers(
    service: SupplierService = Depends(get_supplier_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[SupplierResponse]:
    """List all suppliers. Accessible by any authenticated user."""
    return service.get_all_suppliers()


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Get supplier by ID (Authenticated)",
)
def get_supplier(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> SupplierResponse:
    """Get single supplier details. Accessible by any authenticated user."""
    try:
        return service.get_supplier_by_id(supplier_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Update supplier (Admin only)",
)
def update_supplier(
    supplier_id: int,
    request: SupplierUpdateRequest,
    service: SupplierService = Depends(get_supplier_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> SupplierResponse:
    """Update supplier details. Requires ADMIN role."""
    try:
        return service.update_supplier(supplier_id, request)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete supplier (Admin only)",
)
def delete_supplier(
    supplier_id: int,
    service: SupplierService = Depends(get_supplier_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> None:
    """Delete a supplier. Fails if products are linked. Requires ADMIN role."""
    try:
        service.delete_supplier(supplier_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
