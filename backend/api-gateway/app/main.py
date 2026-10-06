"""
FastAPI Application Entry Point: main.py (API Gateway)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The API Gateway is the single point of entry for clients
(e.g., the React frontend).

Responsibilities:
  - Reverse proxy client requests to internal microservices
  - Maintain CORS policies for frontend origins
  - Centralize service health checking
  - Preserve Authorization headers during downstream transit

Architecture:
  React Frontend (:5173)
        ↓
  API Gateway (:8000)
        ↓
  ┌─────┼──────────┬─────────────┐
  ↓     ↓          ↓             ↓
  Auth  User    Product      Inventory
  :8001 :8002   :8003         :8004
                                  ↓
                              Order Service
                                :8005
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.proxy import router as proxy_router
from app.routes.product_proxy import router as product_proxy_router
from app.routes.inventory_proxy import router as inventory_proxy_router
from app.routes.order_proxy import router as order_proxy_router
from app.routes.user_proxy import router as user_proxy_router

# Validate gateway configuration on startup
settings.validate()

# ─────────────────────────────────────────────────────────────
# Create FastAPI Gateway Application
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Inventory Management - API Gateway",
    version="1.0.0",
    description=(
        "Reverse proxy and API Gateway for the Inventory Management System.\n\n"
        "## Responsibilities\n"
        "- **Single Entry Point**: Routes `/api/*` requests to internal microservices\n"
        "- **CORS Management**: Permitted origins for frontend communication\n"
        "- **Resilience**: 503 error handling when downstream services are offline\n\n"
        "## Active Proxies\n"
        "- `POST /api/auth/login` → `POST :8001/auth/login`\n"
        "- `GET /api/auth/me` → `GET :8001/auth/me`\n"
        "- `GET /api/auth/admin-test` → `GET :8001/auth/admin-test`\n"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─────────────────────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────────────────────
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# De-duplicate while preserving order
allowed_origins = list(dict.fromkeys(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Register Service Proxies
# ─────────────────────────────────────────────────────────────
app.include_router(proxy_router)
app.include_router(product_proxy_router)
app.include_router(inventory_proxy_router)
app.include_router(order_proxy_router)
app.include_router(user_proxy_router)


# ─────────────────────────────────────────────────────────────
# Health Check Endpoint
# ─────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["Health"],
    summary="Gateway Health Check",
    description="Returns operational status of the API Gateway.",
)
def health_check() -> dict:
    """
    Verify the API Gateway service is running.
    """
    return {
        "service": "api-gateway",
        "status": "running",
    }
