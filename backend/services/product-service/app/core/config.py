"""
Core Configuration: config.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads configuration from the ROOT .env file.
Does NOT store or create its own .env.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def _find_root_env() -> Path:
    """
    Traverse up the directory hierarchy to discover the root .env file.
    Ensures monorepo configuration consistency regardless of execution CWD.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        env_path = parent / ".env"
        if env_path.exists():
            return env_path

    raise FileNotFoundError(
        "Root .env file not found. Ensure .env exists in inventory-management-system/"
    )


# Load root .env
_root_env_path = _find_root_env()
load_dotenv(dotenv_path=_root_env_path, override=True)


class Settings:
    """Product Service settings loaded from environment."""

    APP_ENV: str = os.getenv("APP_ENV", "development")

    # JWT Verification (Shared Secret)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Microservice URLs
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003")
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    def validate(self) -> None:
        """Fail fast if critical settings are missing."""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY is not configured in root .env")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not configured in root .env")


settings = Settings()
