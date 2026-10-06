"""
Application Service: AuthService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All authentication BUSINESS LOGIC lives here.

What AuthService does:
  - login()    : Validates credentials against PostgreSQL, returns JWT
  - register() : Hashes password, creates new USER in PostgreSQL
  - verify_token() : Decodes and validates a JWT

Clean Architecture Rules:
  ✅ No FastAPI imports
  ✅ No SQLAlchemy imports
  ✅ Depends on UserRepository INTERFACE, not the PostgreSQL class
  ✅ Returns DTOs, not domain entities
  ✅ Business rules live here (email uniqueness, role enforcement)
  ✅ Password verification via security.py — not inline

Password Security:
  - All passwords are hashed by hash_password() before storage
  - verify_password() uses bcrypt to compare at login
  - Plain-text passwords NEVER persist beyond this service method
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from app.application.dto.auth_dto import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenVerifyResponse,
)
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.domain.entities.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository


class AuthService:
    """
    Application service for authentication.

    Injected with a UserRepository (domain interface) via constructor.
    Does not know whether the repository is in-memory or PostgreSQL.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def login(self, request: LoginRequest) -> LoginResponse:
        """
        Authenticate user credentials and return a JWT token.

        Flow:
            1. Find user by email in the repository
            2. Verify bcrypt password hash
            3. Generate JWT with user_id and role
            4. Return LoginResponse DTO

        Args:
            request : LoginRequest DTO (email + password).

        Returns:
            LoginResponse DTO with access_token, token_type, and role.

        Raises:
            ValueError : Invalid credentials (same message for wrong
                         email and wrong password — prevents enumeration).
        """
        # Step 1: Find user by email
        user = self._user_repository.find_by_email(request.email)

        # Step 2: Verify user exists AND password matches bcrypt hash
        # Using the same error message for both prevents email enumeration attacks.
        if user is None or not verify_password(request.password, user.password):
            raise ValueError("Invalid email or password")

        # Step 3: Generate signed JWT access token
        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            role=user.role.value,
        )

    def register(self, request: RegisterRequest) -> RegisterResponse:
        """
        Register a new user with a hashed password.

        Security rules enforced here (business logic):
            - Public registration always assigns USER role (not ADMIN)
            - Email must be unique (checked via repository)
            - Password is hashed with bcrypt before storage

        Args:
            request : RegisterRequest DTO (email + password).

        Returns:
            RegisterResponse DTO with success message.

        Raises:
            ValueError : If the email is already registered (HTTP 409).
        """
        # Step 1: Check email uniqueness
        existing_user = self._user_repository.find_by_email(request.email)
        if existing_user is not None:
            raise ValueError("Email already registered")

        # Step 2: Hash password — plain-text NEVER touches the database
        hashed = hash_password(request.password)

        # Step 3: Build domain entity (role is always USER for public registration)
        new_user = User(
            id="",                  # Will be assigned by PostgreSQL on INSERT
            email=request.email,
            password=hashed,        # bcrypt hash, not plain-text
            role=UserRole.USER,     # Enforce USER role — security rule
        )

        # Step 4: Persist via repository
        self._user_repository.create_user(new_user)

        return RegisterResponse(message="User registered successfully")

    def verify_token(self, token: str) -> TokenVerifyResponse:
        """
        Decode and validate a JWT token.

        Args:
            token : Raw JWT string from Authorization header.

        Returns:
            TokenVerifyResponse with valid=True, user_id, and role.

        Raises:
            ValueError : If token is expired, invalid, or missing claims.
        """
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            role = payload.get("role")

            if not user_id or not role:
                raise ValueError("Token is missing required claims")

            return TokenVerifyResponse(
                valid=True,
                user_id=str(user_id),
                role=str(role),
            )
        except Exception as exc:
            raise ValueError(f"Invalid or expired token: {str(exc)}")
