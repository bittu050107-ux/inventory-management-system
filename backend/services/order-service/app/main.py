"""
Order Service Entry Point: main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI application for the Order Microservice.

Responsibilities:
  - Order creation with automatic stock reservation
  - Order lifecycle management (PENDING → CONFIRMED → SHIPPED → DELIVERED)
  - Order cancellation with automatic stock restoration
  - RBAC: Admin/Manager manage all orders, Users manage own orders
  - Health checks: GET /health and GET /health/db

Port:    8005
Swagger: http://localhost:8005/docs
ReDoc:   http://localhost:8005/redoc
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.infrastructure.database.database import Base, check_db_connection, engine
import app.infrastructure.database.models  # noqa: F401 — registers ORM models
from app.api.routes.orders import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    On startup:
      - Validates required environment variables
      - Creates database tables if they do not exist
    On shutdown:
      - Graceful teardown log
    """
    print("[INFO] Order Service starting...")
    settings.validate()

    # Auto-create tables (orders, order_items)
    Base.metadata.create_all(bind=engine)
    print("[OK] Order Service database tables verified/created.")

    yield

    print("[STOP] Order Service shutting down...")


# ─────────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Order Service",
    description=(
        "Order Management Microservice.\n\n"
        "## Features\n"
        "- **Create Orders**: Place orders with automatic stock reservation via Inventory Service\n"
        "- **Order Lifecycle**: PENDING → CONFIRMED → SHIPPED → DELIVERED status transitions\n"
        "- **Order Cancellation**: Cancel orders with automatic stock restoration\n"
        "- **Role-Based Access**: Admin/Manager manage all orders; Users see only their own\n"
        "- **Stock Safety**: Validates available stock before confirming any order\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─────────────────────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        settings.API_GATEWAY_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Health Check Endpoints
# ─────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["Health"],
    summary="Order Service health check",
)
def health_check():
    """Service liveness check — returns 200 if running."""
    return {
        "status": "ok",
        "service": "order-service",
    }


@app.get(
    "/health/db",
    tags=["Health"],
    summary="Database connectivity check",
)
def health_db():
    """Verify PostgreSQL connectivity for Order Service."""
    if not check_db_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
    return {
        "database": "postgresql",
        "status": "connected",
    }


# ─────────────────────────────────────────────────────────────
# Mount Routers
# ─────────────────────────────────────────────────────────────
app.include_router(orders_router)
