"""
Product Service Entry Point: main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI application for the Product Microservice.

Responsibilities:
  - Product, Category, and Supplier management
  - Database schema initialization (Base.metadata.create_all)
  - RBAC verification via shared JWT signature
  - Health checks: GET /health and GET /health/db

Port: 8003
Swagger: http://localhost:8003/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.infrastructure.database.database import Base, engine, check_db_connection
import app.infrastructure.database.models  # noqa: F401 (register models)
from app.api.routes.categories import router as category_router
from app.api.routes.suppliers import router as supplier_router
from app.api.routes.products import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes PostgreSQL tables on startup.
    """
    print("[INFO] Product Service starting...")
    settings.validate()

    # Create tables if not present
    Base.metadata.create_all(bind=engine)
    print("[OK] Product Service database tables verified/created.")

    yield

    print("[STOP] Product Service shutting down...")


app = FastAPI(
    title="Product Service",
    description=(
        "Product, Category, and Supplier Microservice for Inventory Management.\n\n"
        "## Features\n"
        "- **Products**: Full CRUD with SKU, price, category, supplier validation\n"
        "- **Categories**: Full CRUD with unique name constraint\n"
        "- **Suppliers**: Full CRUD for vendor/supplier records\n"
        "- **RBAC**: Admin-only for write operations; Authenticated users for read operations\n"
        "- **Auth**: JWT Bearer token authentication\n"
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
    summary="Product Service health check",
)
def health_check():
    """Service liveness status."""
    return {
        "service": "product-service",
        "status": "running",
    }


@app.get(
    "/health/db",
    tags=["Health"],
    summary="Database connectivity check",
)
def health_db():
    """Verify PostgreSQL connectivity for Product Service."""
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
app.include_router(category_router)
app.include_router(supplier_router)
app.include_router(product_router)
