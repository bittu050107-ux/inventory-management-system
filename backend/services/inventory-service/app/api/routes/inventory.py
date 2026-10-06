"""
API Routes: inventory.py (Inventory Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Exposes all inventory and stock movement endpoints:
  - GET  /inventory
  - GET  /inventory/low-stock
  - GET  /inventory/{product_id}
  - POST /inventory/stock-in
  - POST /inventory/stock-out
  - POST /inventory/adjust
  - GET  /inventory/{product_id}/transactions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_inventory_service,
    get_current_user,
    require_read_access,
    require_stock_movement,
    require_stock_adjustment,
)
from app.application.dto.inventory_dto import (
    StockInRequest,
    StockOutRequest,
    StockAdjustRequest,
    InventoryResponse,
    LowStockResponse,
    StockTransactionResponse,
)
from app.application.services.inventory_service import InventoryService
from app.core.exceptions import (
    NotFoundError,
    ProductNotFoundError,
    InsufficientStockError,
    BusinessRuleError,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ─────────────────────────────────────────────────────────────
# 1. READ Operations (ADMIN, MANAGER, STAFF, USER)
# ─────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=List[InventoryResponse],
    summary="Get all inventory records",
)
async def get_all_inventory(
    service: InventoryService = Depends(get_inventory_service),
    _user: Dict[str, Any] = Depends(require_read_access),
) -> List[InventoryResponse]:
    """Return all product inventory records. Requires authentication."""
    return await service.get_all_inventory()


@router.get(
    "/low-stock",
    response_model=List[LowStockResponse],
    summary="Get low-stock products (quantity <= reorder_level)",
)
async def get_low_stock(
    service: InventoryService = Depends(get_inventory_service),
    _user: Dict[str, Any] = Depends(require_read_access),
) -> List[LowStockResponse]:
    """Return items whose current stock is at or below their reorder threshold."""
    return await service.get_low_stock()


@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
    summary="Get inventory for a specific product",
)
async def get_inventory_by_product_id(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service),
    _user: Dict[str, Any] = Depends(require_read_access),
) -> InventoryResponse:
    """Retrieve stock level for the given product ID."""
    try:
        return await service.get_by_product_id(product_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get(
    "/{product_id}/transactions",
    response_model=List[StockTransactionResponse],
    summary="Get transaction history for a product",
)
async def get_transactions(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service),
    _user: Dict[str, Any] = Depends(require_read_access),
) -> List[StockTransactionResponse]:
    """Retrieve all stock movements (IN, OUT, ADJUSTMENT) logged for this product."""
    return await service.get_transaction_history(product_id)


# ─────────────────────────────────────────────────────────────
# 2. STOCK-IN (ADMIN, MANAGER, STAFF)
# ─────────────────────────────────────────────────────────────

@router.post(
    "/stock-in",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Stock-In: Increase product inventory",
)
async def stock_in(
    request: StockInRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Dict[str, Any] = Depends(require_stock_movement),
) -> InventoryResponse:
    """
    Increase product inventory.
    Permitted roles: ADMIN, MANAGER, STAFF.
    Verifies product existence via Product Service.
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    try:
        return await service.stock_in(request, user_id=user_id, auth_token=token)
    except ProductNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


# ─────────────────────────────────────────────────────────────
# 3. STOCK-OUT (ADMIN, MANAGER, STAFF)
# ─────────────────────────────────────────────────────────────

@router.post(
    "/stock-out",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Stock-Out: Dispatch product inventory",
)
async def stock_out(
    request: StockOutRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Dict[str, Any] = Depends(require_stock_movement),
) -> InventoryResponse:
    """
    Decrease product inventory.
    Permitted roles: ADMIN, MANAGER, STAFF.
    Fails with 400 if requested quantity exceeds available stock.
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    try:
        return await service.stock_out(request, user_id=user_id, auth_token=token)
    except ProductNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except InsufficientStockError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


# ─────────────────────────────────────────────────────────────
# 4. ADJUSTMENT (ADMIN, MANAGER)
# ─────────────────────────────────────────────────────────────

@router.post(
    "/adjust",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Stock Adjustment: Correct inventory quantity",
)
async def adjust_stock(
    request: StockAdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Dict[str, Any] = Depends(require_stock_adjustment),
) -> InventoryResponse:
    """
    Set inventory quantity directly.
    Permitted roles: ADMIN, MANAGER only.
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    try:
        return await service.adjust_stock(request, user_id=user_id, auth_token=token)
    except ProductNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
