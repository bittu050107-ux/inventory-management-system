"""
Core Configuration: config.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads ALL configuration from the ROOT .env file using
python-dotenv. No secrets are hardcoded here.

Why load from root .env instead of a local one?
  → Single source of truth for the entire monorepo.
  → One place to change settings, all services pick it up.
  → No risk of .env files getting out of sync.

Usage in any module:
  from app.core.config import settings
  print(settings.JWT_SECRET_KEY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ─────────────────────────────────────────────────────────────
# Locate and load the ROOT .env file
# ─────────────────────────────────────────────────────────────
# When running the service from its own directory, we need to
# walk up the folder tree to find the root .env.
#
# Structure:
#   inventory-management-system/   ← ROOT (where .env lives)
#     backend/
#       services/
#         auth-service/
#           app/
#             core/
#               config.py          ← THIS FILE
#
# Path from this file to root: 6 levels up
# ─────────────────────────────────────────────────────────────

def _find_root_env() -> Path:
    """
    Walk up the directory tree from this file to find the root .env.
    This ensures the service loads the single shared config regardless
    of where it is run from.
    """
    current = Path(__file__).resolve()

    # Walk up until we find a .env file or hit the filesystem root
    for parent in current.parents:
        env_path = parent / ".env"
        if env_path.exists():
            return env_path

    raise FileNotFoundError(
        "Root .env file not found. "
        "Make sure you have a .env in the inventory-management-system/ root."
    )


# Load the root .env into environment variables
_env_path = _find_root_env()
load_dotenv(dotenv_path=_env_path)


# ─────────────────────────────────────────────────────────────
# Settings — typed access to environment variables
# ─────────────────────────────────────────────────────────────

class Settings:
    """
    Central settings object.

    Each property reads from environment variables (loaded from .env).
    This means:
      - No hardcoded values anywhere in the codebase
      - Easy to override in production via actual env vars
      - Type hints make it clear what type each setting is
    """

    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # JWT Configuration
    JWT_SECRET_KEY: str       = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str        = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Admin Seed Account (created once on startup if no admin exists)
    ADMIN_SEED_EMAIL:    str = os.getenv("ADMIN_SEED_EMAIL", "admin@inventory.com")
    ADMIN_SEED_PASSWORD: str = os.getenv("ADMIN_SEED_PASSWORD", "admin123")

    AUTH_SERVICE_URL:      str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    USER_SERVICE_URL:      str = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
    PRODUCT_SERVICE_URL:   str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003")
    INVENTORY_SERVICE_URL: str = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8004")
    ORDER_SERVICE_URL:     str = os.getenv("ORDER_SERVICE_URL", "http://localhost:8005")
    API_GATEWAY_URL:       str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    FRONTEND_URL:          str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    def validate(self) -> None:
        """
        Validate that critical settings are not empty.
        Called at application startup to fail fast if misconfigured.
        """
        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY is not set. "
                "Check your root .env file."
            )
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is not set. "
                "Check your root .env file."
            )


# ─────────────────────────────────────────────────────────────
# Singleton settings instance
# Import this everywhere: from app.core.config import settings
# ─────────────────────────────────────────────────────────────
settings = Settings()
