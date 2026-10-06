"""
Core Security: security.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JWT token decoding for incoming requests.
Order Service only VALIDATES tokens — it never issues them.
Token issuance is handled exclusively by Auth Service.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any
from jose import jwt, JWTError

from app.core.config import settings


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The raw JWT string from the Authorization header.

    Returns:
        The decoded payload dict (e.g. {"sub": "123", "role": "ADMIN"}).

    Raises:
        ValueError: If the token is invalid, expired, or malformed.
    """
    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise ValueError(f"JWT validation failed: {str(exc)}")
