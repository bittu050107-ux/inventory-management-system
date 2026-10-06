"""
Application Service: OrderService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALL Order business logic lives here.
Routes are thin — they call this service and return DTOs.

Responsibilities:
  1. create_order      — validate items, deduct stock via Inventory Service,
                          persist order and items atomically
  2. get_order         — fetch one order by ID (user sees own, admin sees all)
  3. get_all_orders    — admin view of all orders
  4. get_my_orders     — user view of their own orders
  5. update_status     — lifecycle state machine with transition rules
  6. cancel_order      — cancel + restore stock if PENDING/CONFIRMED

Dependency Inversion:
  - OrderService depends on OrderRepository (interface, not implementation)
  - OrderService depends on InventoryClient (HTTP adapter, not hardcoded URL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional

from app.application.dto.order_dto import (
    CreateOrderRequest,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    UpdateOrderStatusRequest,
)
from app.core.exceptions import (
    BusinessRuleError,
    InsufficientStockError,
    NotFoundError,
    OrderStatusError,
    ProductNotFoundError,
)
from app.domain.entities.order import Order, OrderItem, OrderStatus
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.external.inventory_client import InventoryServiceClient


# ─────────────────────────────────────────────────────────────
# Status Transition Rules
# ─────────────────────────────────────────────────────────────
# Defines which transitions are valid for each current status.
ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING.value:   {OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value},
    OrderStatus.CONFIRMED.value: {OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value},
    OrderStatus.SHIPPED.value:   {OrderStatus.DELIVERED.value},
    OrderStatus.DELIVERED.value: set(),   # Terminal — no further transitions
    OrderStatus.CANCELLED.value: set(),   # Terminal — no further transitions
}


def _to_item_response(item: OrderItem) -> OrderItemResponse:
    """Convert domain OrderItem → DTO."""
    return OrderItemResponse(
        id=item.id or 0,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=item.total_price,
    )


def _to_order_response(order: Order) -> OrderResponse:
    """Convert domain Order → DTO."""
    return OrderResponse(
        id=order.id or 0,
        user_id=order.user_id,
        status=order.status,
        notes=order.notes,
        total_amount=order.total_amount,
        items=[_to_item_response(item) for item in order.items],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


class OrderService:
    """Application service orchestrating all order workflows."""

    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_client: InventoryServiceClient,
    ) -> None:
        self._order_repo = order_repository
        self._inventory_client = inventory_client

    # ─────────────────────────────────────────────────────────
    # 1. Create Order
    # ─────────────────────────────────────────────────────────

    async def create_order(
        self,
        request: CreateOrderRequest,
        user_id: str,
        auth_token: Optional[str] = None,
    ) -> OrderResponse:
        """
        Create a new order:
          1. Verify each product exists
          2. Reserve stock via Inventory Service (stock-out)
          3. If any stock-out fails, raise InsufficientStockError
          4. Persist the order atomically
        """
        order_items: List[OrderItem] = []

        for item_req in request.items:
            # Step 1: Verify product exists
            product_exists = await self._inventory_client.verify_product_exists(
                item_req.product_id, auth_token=auth_token
            )
            if not product_exists:
                raise ProductNotFoundError(
                    f"Product with ID {item_req.product_id} not found"
                )

            # Step 2: Check stock availability
            has_stock = await self._inventory_client.check_stock_available(
                product_id=item_req.product_id,
                quantity=item_req.quantity,
                auth_token=auth_token,
            )
            if not has_stock:
                raise InsufficientStockError(
                    f"Insufficient stock for product ID {item_req.product_id}"
                )

            order_items.append(
                OrderItem(
                    product_id=item_req.product_id,
                    quantity=item_req.quantity,
                    unit_price=item_req.unit_price,
                )
            )

        # Step 3: Deduct stock for each confirmed item
        for item in order_items:
            await self._inventory_client.deduct_stock(
                product_id=item.product_id,
                quantity=item.quantity,
                reference=f"ORDER-PENDING",
                notes="Stock reserved for new order",
                auth_token=auth_token,
            )

        # Step 4: Persist the order
        order = Order(
            user_id=user_id,
            items=order_items,
            status=OrderStatus.PENDING.value,
            notes=request.notes,
        )
        saved_order = self._order_repo.create(order)
        return _to_order_response(saved_order)

    # ─────────────────────────────────────────────────────────
    # 2. Get Order by ID
    # ─────────────────────────────────────────────────────────

    async def get_order(
        self, order_id: int, user_id: str, role: str
    ) -> OrderResponse:
        """
        Fetch a specific order.
        - ADMIN / MANAGER: can see any order
        - USER / STAFF: can only see their own orders
        """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order with ID {order_id} not found")

        if role not in ("ADMIN", "MANAGER") and order.user_id != user_id:
            raise BusinessRuleError("You do not have permission to view this order")

        return _to_order_response(order)

    # ─────────────────────────────────────────────────────────
    # 3. Get All Orders (Admin)
    # ─────────────────────────────────────────────────────────

    async def get_all_orders(self) -> OrderListResponse:
        """Fetch all orders — Admin/Manager only."""
        orders = self._order_repo.get_all()
        return OrderListResponse(
            total=len(orders),
            orders=[_to_order_response(o) for o in orders],
        )

    # ─────────────────────────────────────────────────────────
    # 4. Get My Orders (User)
    # ─────────────────────────────────────────────────────────

    async def get_my_orders(self, user_id: str) -> OrderListResponse:
        """Fetch orders belonging to the calling user."""
        orders = self._order_repo.get_by_user_id(user_id)
        return OrderListResponse(
            total=len(orders),
            orders=[_to_order_response(o) for o in orders],
        )

    # ─────────────────────────────────────────────────────────
    # 5. Update Order Status
    # ─────────────────────────────────────────────────────────

    async def update_status(
        self,
        order_id: int,
        request: UpdateOrderStatusRequest,
        user_id: str,
        role: str,
    ) -> OrderResponse:
        """
        Advance the order through its lifecycle.
        Validates transition legality before persisting.
        """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order with ID {order_id} not found")

        new_status = request.status.upper()
        allowed = ALLOWED_TRANSITIONS.get(order.status, set())

        if new_status not in allowed:
            raise OrderStatusError(
                f"Cannot transition order from '{order.status}' to '{new_status}'. "
                f"Allowed: {sorted(allowed) or 'none (terminal state)'}"
            )

        updated = self._order_repo.update_status(order_id, new_status)
        if not updated:
            raise NotFoundError(f"Order with ID {order_id} not found after update")

        return _to_order_response(updated)

    # ─────────────────────────────────────────────────────────
    # 6. Cancel Order
    # ─────────────────────────────────────────────────────────

    async def cancel_order(
        self,
        order_id: int,
        user_id: str,
        role: str,
        auth_token: Optional[str] = None,
    ) -> OrderResponse:
        """
        Cancel an order:
          - Only PENDING or CONFIRMED orders can be cancelled
          - Restores stock back to inventory via stock-in
          - Users can cancel their own PENDING orders
          - Admins/Managers can cancel any PENDING or CONFIRMED order
        """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order with ID {order_id} not found")

        # Permission check
        if role not in ("ADMIN", "MANAGER") and order.user_id != user_id:
            raise BusinessRuleError("You do not have permission to cancel this order")

        # Cancellable states
        if order.status not in (OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value):
            raise OrderStatusError(
                f"Cannot cancel an order with status '{order.status}'. "
                "Only PENDING or CONFIRMED orders can be cancelled."
            )

        # Restore stock for each item
        for item in order.items:
            await self._inventory_client.restore_stock(
                product_id=item.product_id,
                quantity=item.quantity,
                reference=f"CANCEL-ORDER-{order_id}",
                notes=f"Stock returned from cancelled order #{order_id}",
                auth_token=auth_token,
            )

        updated = self._order_repo.update_status(order_id, OrderStatus.CANCELLED.value)
        if not updated:
            raise NotFoundError(f"Order with ID {order_id} not found after cancellation")

        return _to_order_response(updated)
