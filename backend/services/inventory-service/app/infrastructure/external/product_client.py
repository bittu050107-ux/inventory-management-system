"""
Infrastructure External Client: ProductServiceClient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Communicates with Product Microservice over HTTP to verify
product existence without touching its database.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional
import httpx
from app.core.config import settings


class ProductServiceClient:
    """HTTP client communicating with Product Service."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self._base_url = (base_url or settings.PRODUCT_SERVICE_URL).rstrip("/")

    async def verify_product_exists(
        self, product_id: int, auth_token: Optional[str] = None
    ) -> bool:
        """
        Query Product Service (GET /products/{product_id}) to check if product exists.
        Forwards JWT Bearer token if provided to fulfill Product Service authentication.
        """
        headers = {}
        if auth_token:
            if auth_token.startswith("Bearer "):
                headers["Authorization"] = auth_token
            else:
                headers["Authorization"] = f"Bearer {auth_token}"

        target_url = f"{self._base_url}/products/{product_id}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(target_url, headers=headers)
                if response.status_code == 200:
                    return True
                elif response.status_code == 404:
                    return False
                elif response.status_code in (401, 403):
                    # If unauthorized by Product Service, still try to deduce or log
                    return False
                return False
        except httpx.RequestError:
            # If Product Service is unreachable or down, return False or raise
            return False
