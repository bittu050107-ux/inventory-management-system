"""
Application DTOs: auth_dto.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DTOs (Data Transfer Objects) define the shape of data that
crosses layer boundaries — specifically between the API layer
and the application service layer.

Why DTOs instead of passing raw dicts?
  → Type safety: Pydantic validates input automatically
  → Clear contract: Exactly what's needed — no more, no less
  → Swagger docs: FastAPI generates OpenAPI spec from these
  → Decoupling: Domain entities never leak into HTTP responses

LoginRequest  → What the client sends to /auth/login
LoginResponse → What the server sends back on success
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    DTO for incoming login requests.

    Pydantic automatically:
      - Validates that email is a properly formatted email address
      - Raises a 422 Unprocessable Entity if validation fails
      - Generates Swagger request body documentation

    Example JSON body:
        {
          "email": "admin@inventory.com",
          "password": "admin123"
        }
    """
    email: EmailStr = Field(
        ...,
        description="User's registered email address",
        example="admin@inventory.com"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User's password",
        example="admin123"
    )


class LoginResponse(BaseModel):
    """
    DTO for successful login responses.

    Returned to the client after successful authentication.
    The client should store access_token and send it in future
    requests as: Authorization: Bearer <access_token>

    Example JSON response:
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer",
          "role": "ADMIN"
        }
    """
    access_token: str = Field(
        ...,
        description="JWT access token — include in Authorization header"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type — always 'bearer' for JWT"
    )
    role: str = Field(
        ...,
        description="The authenticated user's role (ADMIN, MANAGER, STAFF, USER)"
    )


class TokenVerifyRequest(BaseModel):
    """
    DTO for token verification requests (POST /auth/verify).
    """
    token: str = Field(
        ...,
        description="JWT access token to verify"
    )


class TokenVerifyResponse(BaseModel):
    """
    DTO returned when verifying a JWT token.
    Contains decoded identity claims: user_id and role.
    """
    valid: bool = Field(
        default=True,
        description="Indicates whether the token is currently valid and active"
    )
    user_id: str = Field(
        ...,
        description="User unique identifier extracted from token 'sub' claim"
    )
    role: str = Field(
        ...,
        description="User role extracted from token 'role' claim"
    )


class RoleCheckResponse(BaseModel):
    """
    DTO returned by role-protected routes to verify RBAC access.
    """
    message: str = Field(
        ...,
        description="Status message confirming access"
    )
    user_id: str = Field(
        ...,
        description="User ID extracted from token"
    )
    role: str = Field(
        ...,
        description="Role of the authenticated user"
    )


class UserMeResponse(BaseModel):
    """
    DTO returned by /auth/me representing current authenticated user identity.
    """
    user_id: str = Field(..., description="User unique identifier")
    role: str = Field(..., description="User role")


class AdminTestResponse(BaseModel):
    """
    DTO returned by /auth/admin-test confirming admin privileges.
    """
    message: str = Field(default="Welcome Admin", description="Welcome message for admin")
    role: str = Field(..., description="User role")


class RegisterRequest(BaseModel):
    """
    DTO for new user registration requests (POST /auth/register).

    Security:
        The 'role' field is intentionally ignored by the service layer
        for public registrations — all self-registered users get USER role.
        Only an internal/admin process can assign elevated roles.
    """
    email: EmailStr = Field(
        ...,
        description="New user's email address",
        example="bittu@example.com",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="New user's password (minimum 6 characters)",
        example="password123",
    )


class RegisterResponse(BaseModel):
    """
    DTO returned after a successful user registration.
    """
    message: str = Field(
        default="User registered successfully",
        description="Confirmation message",
    )



