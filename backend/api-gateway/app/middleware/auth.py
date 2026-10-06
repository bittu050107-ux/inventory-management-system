"""
Middleware: auth.py (API Gateway)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handles header extraction, propagation, and client request
forwarding for the API Gateway.

Key Principles:
  - The Gateway does NOT verify or sign JWTs itself.
  - The Gateway NEVER strips or alters the 'Authorization' header.
  - Passes client identity headers directly downstream to Auth Service.
  - Centralizes httpx error handling (connection failure, timeouts).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, Optional
import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.config import settings


def extract_forward_headers(request: Request) -> Dict[str, str]:
    """
    Extract headers from incoming client request that should be
    forwarded to the downstream microservice.

    Preserves:
      - Authorization (Bearer <JWT>)
      - Content-Type (application/json)
      - Accept
    """
    forward_headers: Dict[str, str] = {}

    auth_header = request.headers.get("Authorization")
    if auth_header:
        forward_headers["Authorization"] = auth_header

    content_type = request.headers.get("Content-Type")
    if content_type:
        forward_headers["Content-Type"] = content_type

    accept = request.headers.get("Accept")
    if accept:
        forward_headers["Accept"] = accept

    return forward_headers


async def forward_request(
    target_url: str,
    method: str,
    headers: Dict[str, str],
    json_data: Optional[Any] = None,
    params: Optional[Dict[str, Any]] = None,
    service_name: str = "Downstream service",
) -> JSONResponse:
    """
    Forward an HTTP request to a downstream microservice using httpx.

    Handles:
      - httpx.ConnectError / ConnectTimeout → HTTP 503 "{service_name} unavailable"
      - Downstream non-2xx responses → forwarded with exact status & payload
      - httpx.HTTPError → HTTP 503 "{service_name} communication error"

    No internal stack traces are leaked to the client.
    """
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                json=json_data,
                params=params,
            )

            # Try parsing JSON response from downstream service
            try:
                data = response.json()
            except Exception:
                data = {"detail": response.text}

            return JSONResponse(
                status_code=response.status_code,
                content=data,
            )

        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.NetworkError):
            # Target service is offline, down, or unreachable
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{service_name} unavailable",
            )
        except httpx.TimeoutException:
            # Downstream service took too long to respond
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"{service_name} request timed out",
            )
        except httpx.HTTPError:
            # Any other transport/HTTP exception
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{service_name} unavailable",
            )

