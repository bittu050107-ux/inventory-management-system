"""
Infrastructure External: InventoryServiceClient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTTP adapter for communicating with the Inventory Service.
The Order Service uses this client to:
  1. Verify a product exists (via Product Service proxy)
  2. Check whether enough stock is available
  3. Deduct stock when creating an order (stock-out)
  4. Restore stock when cancelling an order (stock-in)

Design:
  - Raises domain exceptions (not HTTP exceptions) so business
    logic in OrderService stays framework-agnostic.
  - Uses httpx for async HTTP calls.
  - Auth token is forwarded so Inventory Service can validate roles.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional
import httpx

from app.core.config import settings
from app.core.exceptions import InsufficientStockError, ProductNotFoundError


class InventoryServiceClient:
    """
    Async HTTP client for the Inventory Microservice.
    All methods are async — must be awaited.
    """

    def __init__(self) -> None:
        self._inventory_url = settings.INVENTORY_SERVICE_URL
        self._product_url = settings.PRODUCT_SERVICE_URL

    def _auth_headers(self, auth_token: Optional[str]) -> dict:
        """Build Authorization header if token is present."""
        if auth_token:
            return {"Authorization": f"Bearer {auth_token}"}
        return {}

    async def verify_product_exists(
        self, product_id: int, auth_token: Optional[str] = None
    ) -> bool:
        """
        Check whether a product exists in the Product Service.

        Args:
            product_id: The product's primary key.
            auth_token: JWT token to forward for authentication.

        Returns:
            True if product exists, False otherwise.
        """
        url = f"{self._product_url}/products/{product_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    url, headers=self._auth_headers(auth_token)
                )
            return response.status_code == 200
        except httpx.RequestError:
            # Product Service unreachable → treat as not found
            return False

    async def check_stock_available(
        self,
        product_id: int,
        quantity: int,
        auth_token: Optional[str] = None,
    ) -> bool:
        """
        Check whether the Inventory Service has enough stock for a product.

        Calls GET /inventory/product/{product_id} and compares quantity.

        Args:
            product_id: The product to check.
            quantity:   Required units.
            auth_token: JWT token to forward.

        Returns:
            True if available stock >= requested quantity.
        """
        url = f"{self._inventory_url}/inventory/product/{product_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    url, headers=self._auth_headers(auth_token)
                )
            if response.status_code == 404:
                # No inventory record → 0 stock
                return False
            if response.status_code == 200:
                data = response.json()
                available = data.get("quantity", 0)
                return available >= quantity
            return False
        except httpx.RequestError:
            return False

    async def deduct_stock(
        self,
        product_id: int,
        quantity: int,
        reference: str,
        notes: str,
        auth_token: Optional[str] = None,
    ) -> None:
        """
        Perform a stock-out in the Inventory Service (reserve stock for order).

        Calls POST /inventory/stock-out.

        Raises:
            InsufficientStockError: If Inventory Service returns 400.
        """
        url = f"{self._inventory_url}/inventory/stock-out"
        payload = {
            "product_id": product_id,
            "quantity": quantity,
            "reference": reference,
            "notes": notes,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._auth_headers(auth_token),
                )
            if response.status_code == 400:
                raise InsufficientStockError(
                    f"Insufficient stock for product {product_id}: "
                    + response.json().get("detail", "")
                )
            response.raise_for_status()
        except InsufficientStockError:
            raise
        except httpx.RequestError as exc:
            raise InsufficientStockError(
                f"Could not reach Inventory Service to deduct stock: {str(exc)}"
            )

    async def restore_stock(
        self,
        product_id: int,
        quantity: int,
        reference: str,
        notes: str,
        auth_token: Optional[str] = None,
    ) -> None:
        """
        Restore stock back to Inventory Service (on order cancellation).

        Calls POST /inventory/stock-in.
        Errors here are logged but do not fail the cancellation — the
        order is already being cancelled.
        """
        url = f"{self._inventory_url}/inventory/stock-in"
        payload = {
            "product_id": product_id,
            "quantity": quantity,
            "reference": reference,
            "notes": notes,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._auth_headers(auth_token),
                )
            response.raise_for_status()
        except Exception as exc:
            # Log warning — stock restoration is best-effort on cancellation
            print(
                f"⚠️  WARNING: Failed to restore stock for product {product_id}: {exc}"
            )
