"""
Core Security: security.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JWT token creation/decoding AND bcrypt password hashing.

Why bcrypt?
  → One-way hashing: passwords cannot be recovered from hashes
  → Slow by design: makes brute-force attacks computationally expensive
  → Work factor: cost can be increased as hardware gets faster

JWT Payload Structure:
  {
    "sub":  "user-id",      ← Subject (standard JWT claim)
    "role": "ADMIN",        ← Custom claim for RBAC
    "exp":  1234567890      ← Expiration timestamp (auto-set)
  }
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# ─────────────────────────────────────────────────────────────
# bcrypt Password Hashing
# ─────────────────────────────────────────────────────────────
# CryptContext handles bcrypt algorithm selection and versioning.
# deprecated="auto" → automatically re-hashes if algorithm changes.
# ─────────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Example:
        hash_password("admin123")
        → "$2b$12$WCi5XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXW"

    The result is a long string starting with "$2b$".
    This string is safe to store in the database — it cannot
    be reversed to recover the original password.

    Args:
        plain_password : The plain-text password to hash.

    Returns:
        A bcrypt hash string (60 characters).
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    How it works:
        1. bcrypt extracts the salt from the stored hash
        2. Hashes the plain_password with that same salt
        3. Compares the result to the stored hash

    Args:
        plain_password  : What the user typed at login.
        hashed_password : The bcrypt hash from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────────────────────
# JWT Token Utilities
# ─────────────────────────────────────────────────────────────

def create_access_token(
    user_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id       : User's unique ID (stored as 'sub' claim).
        role          : User's role string (e.g. 'ADMIN', 'USER').
        expires_delta : Optional custom expiry. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        A signed JWT string. Client sends this as:
        Authorization: Bearer <token>
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub":  user_id,
        "role": role,
        "exp":  expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token : The JWT string to decode.

    Returns:
        The decoded payload dict (contains 'sub', 'role', 'exp').

    Raises:
        jose.JWTError : If the token is invalid, expired, or tampered with.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
