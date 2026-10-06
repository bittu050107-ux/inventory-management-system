"""
API Routes: orders.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI routes for order management.
Routes are THIN — they delegate all logic to OrderService.

Endpoints:
  POST   /orders                    → Create a new order (any authenticated user)
  GET    /orders                    → List all orders (Admin/Manager only)
  GET    /orders/my                 → List caller's own orders
  GET    /orders/{order_id}         → Get a specific order
  PATCH  /orders/{order_id}/status  → Update order status (Admin/Manager)
  POST   /orders/{order_id}/cancel  → Cancel an order (owner or Admin/Manager)
  DELETE /orders/{order_id}         → Hard delete order (Admin only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_current_user,
    get_order_service,
    require_admin,
    require_authenticated,
    require_manager_or_admin,
)
from app.application.dto.order_dto import (
    CreateOrderRequest,
    OrderListResponse,
    OrderResponse,
    UpdateOrderStatusRequest,
)
from app.application.services.order_service import OrderService
from app.core.exceptions import (
    BusinessRuleError,
    InsufficientStockError,
    NotFoundError,
    OrderStatusError,
    ProductNotFoundError,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


# ─────────────────────────────────────────────────────────────
# POST /orders — Create a new order
# ─────────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description=(
        "Create an order with one or more items. "
        "Stock is deducted from Inventory Service automatically. "
        "Order starts in PENDING status."
    ),
)
async def create_order(
    request: CreateOrderRequest,
    current_user: Dict[str, Any] = Depends(require_authenticated),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        return await service.create_order(
            request=request,
            user_id=current_user["user_id"],
            auth_token=current_user["token"],
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


# ─────────────────────────────────────────────────────────────
# GET /orders — Admin/Manager: list all orders
# ─────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
    summary="[Admin/Manager] List all orders",
    description="Returns all orders in the system. Restricted to Admin and Manager roles.",
)
async def get_all_orders(
    current_user: Dict[str, Any] = Depends(require_manager_or_admin),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    return await service.get_all_orders()


# ─────────────────────────────────────────────────────────────
# GET /orders/my — User: list own orders
# ─────────────────────────────────────────────────────────────
@router.get(
    "/my",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
    summary="List my orders",
    description="Returns all orders placed by the currently authenticated user.",
)
async def get_my_orders(
    current_user: Dict[str, Any] = Depends(require_authenticated),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    return await service.get_my_orders(user_id=current_user["user_id"])


# ─────────────────────────────────────────────────────────────
# GET /orders/{order_id} — Get a specific order
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get order by ID",
    description=(
        "Fetch a single order by its ID. "
        "Users can only view their own orders. "
        "Admins and Managers can view any order."
    ),
)
async def get_order(
    order_id: int,
    current_user: Dict[str, Any] = Depends(require_authenticated),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        return await service.get_order(
            order_id=order_id,
            user_id=current_user["user_id"],
            role=current_user["role"],
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except BusinessRuleError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# PATCH /orders/{order_id}/status — Update order status
# ─────────────────────────────────────────────────────────────
@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="[Admin/Manager] Update order status",
    description=(
        "Advance an order through its lifecycle. "
        "Valid transitions: PENDING→CONFIRMED→SHIPPED→DELIVERED or →CANCELLED. "
        "Invalid transitions are rejected."
    ),
)
async def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    current_user: Dict[str, Any] = Depends(require_manager_or_admin),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        return await service.update_status(
            order_id=order_id,
            request=request,
            user_id=current_user["user_id"],
            role=current_user["role"],
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OrderStatusError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# POST /orders/{order_id}/cancel — Cancel an order
# ─────────────────────────────────────────────────────────────
@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an order",
    description=(
        "Cancel a PENDING or CONFIRMED order. "
        "Stock is automatically restored to Inventory Service. "
        "Users can cancel their own PENDING orders. "
        "Admins/Managers can cancel any PENDING or CONFIRMED order."
    ),
)
async def cancel_order(
    order_id: int,
    current_user: Dict[str, Any] = Depends(require_authenticated),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        return await service.cancel_order(
            order_id=order_id,
            user_id=current_user["user_id"],
            role=current_user["role"],
            auth_token=current_user["token"],
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (OrderStatusError, BusinessRuleError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# DELETE /orders/{order_id} — Hard delete (Admin only)
# ─────────────────────────────────────────────────────────────
@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete an order",
    description="Permanently delete an order. Admin access only.",
)
async def delete_order(
    order_id: int,
    current_user: Dict[str, Any] = Depends(require_admin),
    service: OrderService = Depends(get_order_service),
) -> None:
    repo = service._order_repo
    deleted = repo.delete(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )
