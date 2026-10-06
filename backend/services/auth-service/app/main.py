"""
Auth Service Entry Point: main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI application factory for the Authentication microservice.

Startup sequence:
  1. Settings validation (JWT_SECRET_KEY, DATABASE_URL)
  2. Create database tables (CREATE TABLE IF NOT EXISTS)
  3. Seed admin account if none exists
  4. Mount API router
  5. Start accepting requests

Port: 8001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.core.config import settings
from app.core.security import hash_password
from app.domain.entities.user import User, UserRole
from app.infrastructure.database.database import Base, SessionLocal, engine
from app.infrastructure.repositories.user_repository_impl import PostgreSQLUserRepository


# ─────────────────────────────────────────────────────────────
# Startup / Shutdown Lifecycle
# ─────────────────────────────────────────────────────────────

def _create_tables() -> None:
    """
    Create all SQLAlchemy-mapped tables in PostgreSQL.

    Uses CREATE TABLE IF NOT EXISTS (idempotent — safe to call on every restart).
    Import models here so SQLAlchemy knows about them before calling create_all.
    """
    # Import models to register them with Base.metadata
    import app.infrastructure.database.models  # noqa: F401  (side-effect import)

    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created (or already exist).")


def _seed_admin_account() -> None:
    """
    Create the initial ADMIN account if no admin user exists yet.

    Why:
        A fresh database has no users. We need at least one ADMIN to
        manage the system. This runs once at startup and is idempotent
        (does nothing if an ADMIN already exists).

    Credentials come from root .env:
        ADMIN_SEED_EMAIL    → admin@inventory.com (default)
        ADMIN_SEED_PASSWORD → admin123 (default, change in production!)
    """
    db = SessionLocal()
    try:
        repo = PostgreSQLUserRepository(db)

        # Check if any ADMIN user exists
        existing_admin = repo.find_admin()
        if existing_admin:
            print(f"[OK] Admin already exists: {existing_admin.email} - skipping seed.")
            return

        # No admin exists — create one
        hashed = hash_password(settings.ADMIN_SEED_PASSWORD)
        admin_user = User(
            id="",
            email=settings.ADMIN_SEED_EMAIL,
            password=hashed,
            role=UserRole.ADMIN,
        )
        repo.create_user(admin_user)
        print(f"[OK] Admin account seeded: {settings.ADMIN_SEED_EMAIL}")

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager — runs code on startup and shutdown.

    On startup:
        1. Validate configuration
        2. Create DB tables
        3. Seed admin if needed

    On shutdown:
        - (add cleanup here in future, e.g., close connection pools)
    """
    # ── Startup ──────────────────────────────────────────────
    print("[INFO] Auth Service starting...")

    # 1. Fail fast if critical environment variables are missing
    settings.validate()
    print(f"[OK] Configuration valid. Environment: {settings.APP_ENV}")

    # 2. Create database tables
    _create_tables()

    # 3. Seed admin account
    _seed_admin_account()

    print("[OK] Auth Service ready at http://localhost:8001")

    yield   # Application runs here

    # ── Shutdown ─────────────────────────────────────────────
    print("[STOP] Auth Service shutting down...")


# ─────────────────────────────────────────────────────────────
# FastAPI Application Factory
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Auth Service",
    description=(
        "JWT-based Authentication Microservice for the Inventory Management System.\n\n"
        "**Endpoints:**\n"
        "- `POST /auth/login` — Login and receive JWT\n"
        "- `POST /auth/register` — Register a new USER\n"
        "- `POST /auth/verify` — Validate a JWT token\n"
        "- `GET /auth/me` — Get current user info\n"
        "- `GET /auth/admin-test` — Admin-only route (ADMIN role required)\n"
        "- `GET /auth/user-only` — Any authenticated user\n"
        "- `GET /health` — Service health\n"
        "- `GET /health/db` — Database connectivity\n"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Mount Routers
# ─────────────────────────────────────────────────────────────
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

# Health check at root level too (no prefix)
app.include_router(
    auth_router,
    prefix="",
    include_in_schema=False,   # Don't duplicate in Swagger
    tags=["health"],
)
