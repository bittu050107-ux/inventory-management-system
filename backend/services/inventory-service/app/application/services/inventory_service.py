"""
Application Service: InventoryService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Encapsulates all Inventory business workflows:
  - Product verification via Product Service HTTP API
  - Stock-in, stock-out, and stock adjustments
  - Atomic persistence (inventory + transaction log)
  - Low stock calculation and transaction audits
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional
from app.application.dto.inventory_dto import (
    StockInRequest,
    StockOutRequest,
    StockAdjustRequest,
    InventoryResponse,
    LowStockResponse,
    StockTransactionResponse,
)
from app.core.exceptions import (
    NotFoundError,
    ProductNotFoundError,
    InsufficientStockError,
    BusinessRuleError,
)
from app.domain.entities.inventory import Inventory
from app.domain.entities.stock_transaction import StockTransaction, TransactionType
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.external.product_client import ProductServiceClient


class InventoryService:
    """Service orchestrating inventory and stock management."""

    def __init__(
        self,
        inventory_repository: InventoryRepository,
        product_client: ProductServiceClient,
    ) -> None:
        self._inventory_repo = inventory_repository
        self._product_client = product_client

    async def get_all_inventory(self) -> List[InventoryResponse]:
        """Fetch all inventory records."""
        items = self._inventory_repo.get_all()
        return [
            InventoryResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                reorder_level=item.reorder_level,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def get_by_product_id(self, product_id: int) -> InventoryResponse:
        """Fetch inventory for a specific product."""
        item = self._inventory_repo.get_by_product_id(product_id)
        if not item:
            raise NotFoundError(f"Inventory record for product {product_id} not found")

        return InventoryResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            reorder_level=item.reorder_level,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def get_low_stock(self) -> List[LowStockResponse]:
        """Retrieve all items where current quantity <= reorder_level."""
        low_stock_items = self._inventory_repo.get_low_stock()
        return [
            LowStockResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                reorder_level=item.reorder_level,
            )
            for item in low_stock_items
        ]

    async def stock_in(
        self, request: StockInRequest, user_id: str, auth_token: Optional[str] = None
    ) -> InventoryResponse:
        """
        Increase stock for a product:
          1. Verify product exists in Product Service
          2. Find or initialize inventory record
          3. Increase quantity
          4. Record 'IN' transaction atomically
        """
        # Step 1: Verify product exists
        product_exists = await self._product_client.verify_product_exists(
            request.product_id, auth_token=auth_token
        )
        if not product_exists:
            raise ProductNotFoundError("Product not found")

        # Step 2: Retrieve or initialize inventory
        inventory = self._inventory_repo.get_by_product_id(request.product_id)
        if not inventory:
            inventory = Inventory(
                product_id=request.product_id,
                quantity=request.quantity,
                reorder_level=10,
            )
        else:
            inventory.quantity += request.quantity

        # Step 3: Create transaction record
        transaction = StockTransaction(
            product_id=request.product_id,
            transaction_type=TransactionType.IN.value,
            quantity=request.quantity,
            reference=request.reference,
            notes=request.notes,
            created_by=user_id,
        )

        # Step 4: Atomic commit
        saved_inv, _ = self._inventory_repo.apply_stock_change_atomic(
            inventory, transaction
        )

        return InventoryResponse(
            id=saved_inv.id,
            product_id=saved_inv.product_id,
            quantity=saved_inv.quantity,
            reorder_level=saved_inv.reorder_level,
            created_at=saved_inv.created_at,
            updated_at=saved_inv.updated_at,
        )

    async def stock_out(
        self, request: StockOutRequest, user_id: str, auth_token: Optional[str] = None
    ) -> InventoryResponse:
        """
        Decrease stock for a product:
          1. Verify product exists
          2. Check available stock
          3. Reject if requested > available
          4. Decrease quantity
          5. Record 'OUT' transaction atomically
        """
        # Step 1: Verify product exists
        product_exists = await self._product_client.verify_product_exists(
            request.product_id, auth_token=auth_token
        )
        if not product_exists:
            raise ProductNotFoundError("Product not found")

        # Step 2: Retrieve inventory
        inventory = self._inventory_repo.get_by_product_id(request.product_id)
        if not inventory or inventory.quantity < request.quantity:
            available = inventory.quantity if inventory else 0
            raise InsufficientStockError(
                f"Insufficient stock. Available: {available}, requested: {request.quantity}"
            )

        # Step 3: Decrease quantity
        inventory.quantity -= request.quantity

        # Step 4: Create transaction record
        transaction = StockTransaction(
            product_id=request.product_id,
            transaction_type=TransactionType.OUT.value,
            quantity=request.quantity,
            reference=request.reference,
            notes=request.notes,
            created_by=user_id,
        )

        # Step 5: Atomic commit
        saved_inv, _ = self._inventory_repo.apply_stock_change_atomic(
            inventory, transaction
        )

        return InventoryResponse(
            id=saved_inv.id,
            product_id=saved_inv.product_id,
            quantity=saved_inv.quantity,
            reorder_level=saved_inv.reorder_level,
            created_at=saved_inv.created_at,
            updated_at=saved_inv.updated_at,
        )

    async def adjust_stock(
        self, request: StockAdjustRequest, user_id: str, auth_token: Optional[str] = None
    ) -> InventoryResponse:
        """
        Set inventory quantity directly:
          1. Admin/Manager only
          2. Verify product exists
          3. Set quantity to specified value
          4. Record 'ADJUSTMENT' transaction atomically
        """
        # Step 1: Verify product exists
        product_exists = await self._product_client.verify_product_exists(
            request.product_id, auth_token=auth_token
        )
        if not product_exists:
            raise ProductNotFoundError("Product not found")

        # Step 2: Retrieve or initialize inventory
        inventory = self._inventory_repo.get_by_product_id(request.product_id)
        if not inventory:
            inventory = Inventory(
                product_id=request.product_id,
                quantity=request.quantity,
                reorder_level=10,
            )
        else:
            inventory.quantity = request.quantity

        # Step 3: Create transaction record
        transaction = StockTransaction(
            product_id=request.product_id,
            transaction_type=TransactionType.ADJUSTMENT.value,
            quantity=request.quantity,
            reference="PHYSICAL-CORRECTION",
            notes=request.notes or "Physical stock adjustment",
            created_by=user_id,
        )

        # Step 4: Atomic commit
        saved_inv, _ = self._inventory_repo.apply_stock_change_atomic(
            inventory, transaction
        )

        return InventoryResponse(
            id=saved_inv.id,
            product_id=saved_inv.product_id,
            quantity=saved_inv.quantity,
            reorder_level=saved_inv.reorder_level,
            created_at=saved_inv.created_at,
            updated_at=saved_inv.updated_at,
        )

    async def get_transaction_history(
        self, product_id: int
    ) -> List[StockTransactionResponse]:
        """Fetch audit log for a product."""
        txs = self._inventory_repo.get_transactions_by_product_id(product_id)
        return [
            StockTransactionResponse(
                id=tx.id,
                product_id=tx.product_id,
                transaction_type=tx.transaction_type,
                quantity=tx.quantity,
                reference=tx.reference,
                notes=tx.notes,
                created_by=tx.created_by,
                created_at=tx.created_at,
            )
            for tx in txs
        ]
