"""
Shared Constants — HTTP Status Codes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Centralized constants used across all microservices.
Import from here instead of using magic numbers.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# Token type constant
BEARER_TOKEN_TYPE = "bearer"

# Standard messages
MSG_INVALID_CREDENTIALS = "Invalid email or password"
MSG_TOKEN_EXPIRED = "Token has expired"
MSG_TOKEN_INVALID = "Invalid or malformed token"
MSG_UNAUTHORIZED = "Authentication required"
MSG_FORBIDDEN = "You do not have permission to perform this action"
