"""
Core Configuration: config.py (API Gateway)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads ALL configuration from the SINGLE ROOT .env file using
python-dotenv. No secrets or service URLs are hardcoded here.

Clean Architecture Rule:
  - The Gateway discovers services via configured environment URLs.
  - One root .env file serves the entire microservice ecosystem.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def _find_root_env() -> Path:
    """
    Traverse up the directory hierarchy to locate the root .env file.
    Ensures seamless execution from any working directory.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        env_path = parent / ".env"
        if env_path.exists():
            return env_path
    raise FileNotFoundError(
        "Root .env file not found. Ensure .env exists at the repository root."
    )


# Load environment variables from the single root .env
_env_path = _find_root_env()
load_dotenv(dotenv_path=_env_path)


class GatewaySettings:
    """
    API Gateway configuration settings loaded from root .env.
    """
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # API Gateway URL
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

    # Downstream Microservice URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003")
    INVENTORY_SERVICE_URL: str = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8004")
    ORDER_SERVICE_URL: str = os.getenv("ORDER_SERVICE_URL", "http://localhost:8005")

    # Frontend CORS origin
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # HTTP Client timeouts (seconds)
    REQUEST_TIMEOUT: float = float(os.getenv("GATEWAY_TIMEOUT", "10.0"))

    def validate(self) -> None:
        """
        Validate presence of critical downstream service URLs.
        """
        if not self.AUTH_SERVICE_URL:
            raise ValueError("AUTH_SERVICE_URL is not configured in root .env.")


settings = GatewaySettings()
