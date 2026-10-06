"""
Inventory Service Entry Point: main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI application for the Inventory Microservice.

Responsibilities:
  - Inventory level tracking per product
  - Stock transaction audit history (IN, OUT, ADJUSTMENT)
  - Auto-initialization of DB tables on startup
  - Product existence verification via Product Service HTTP API
  - Health checks: GET /health and GET /health/db

Port: 8004
Swagger: http://localhost:8004/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.infrastructure.database.database import Base, engine, check_db_connection
import app.infrastructure.database.models  # noqa: F401 (register models)
from app.api.routes.inventory import router as inventory_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes PostgreSQL tables on startup.
    """
    print("[INFO] Inventory Service starting...")
    settings.validate()

    # Create tables if not present
    Base.metadata.create_all(bind=engine)
    print("[OK] Inventory Service database tables verified/created.")

    yield

    print("[STOP] Inventory Service shutting down...")


app = FastAPI(
    title="Inventory Service",
    description=(
        "Inventory and Stock Management Microservice.\n\n"
        "## Features\n"
        "- **Stock Tracking**: Maintain live quantity and reorder thresholds per product\n"
        "- **Stock-In**: Increment stock with reference and audit logs\n"
        "- **Stock-Out**: Decrement stock with insufficient stock safeguards\n"
        "- **Adjustment**: Direct physical stock correction (Admin/Manager only)\n"
        "- **Audit Log**: Immutable transaction ledger for all movements\n"
        "- **Product Validation**: External HTTP verification via Product Service\n"
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
    summary="Inventory Service health check",
)
def health_check():
    """Service liveness status."""
    return {
        "status": "ok",
        "service": "inventory-service",
    }


@app.get(
    "/health/db",
    tags=["Health"],
    summary="Database connectivity check",
)
def health_db():
    """Verify PostgreSQL connectivity for Inventory Service."""
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
# Mount Routes
# ─────────────────────────────────────────────────────────────
app.include_router(inventory_router)
