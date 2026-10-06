"""
Infrastructure Repository: PostgreSQLUserRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Concrete implementation of UserRepository backed by PostgreSQL
via SQLAlchemy ORM.

Responsibilities:
  - Translate between domain User entity ↔ UserModel (ORM)
  - Execute all database queries (no queries live in services)
  - Commit/rollback transactions properly

Clean Architecture Rule:
  - This class knows about SQLAlchemy Session and UserModel
  - The application service knows ONLY about UserRepository (interface)
  - Swapping to a different DB → create new class, update dependencies.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class PostgreSQLUserRepository(UserRepository):
    """
    PostgreSQL-backed implementation of the UserRepository domain interface.

    Uses SQLAlchemy Session for all database operations.
    Translates UserModel (ORM) ↔ User (domain entity).

    Every method maps a domain operation to a SQL query.
    No business logic lives here — only database access.
    """

    def __init__(self, db: Session) -> None:
        """
        Inject the SQLAlchemy session.

        Args:
            db : The SQLAlchemy Session provided by FastAPI's get_db() dependency.
        """
        self._db = db

    # ─────────────────────────────────────────────────────────
    # Private helper: ORM model → Domain entity
    # ─────────────────────────────────────────────────────────

    def _to_domain(self, model: UserModel) -> User:
        """
        Convert a SQLAlchemy UserModel row into a pure domain User entity.

        This translation layer prevents ORM models from leaking
        into the application or domain layers.
        """
        return User(
            id=str(model.id),
            email=model.email,
            password=model.password_hash,   # password field holds the bcrypt hash
            role=UserRole(model.role),
        )

    # ─────────────────────────────────────────────────────────
    # Repository Methods (implements UserRepository interface)
    # ─────────────────────────────────────────────────────────

    def find_by_email(self, email: str) -> Optional[User]:
        """
        SELECT * FROM users WHERE email = :email LIMIT 1.

        Args:
            email : The email to search for.

        Returns:
            Domain User entity if found, None otherwise.
        """
        model = (
            self._db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )
        return self._to_domain(model) if model else None

    def create_user(self, user: User) -> User:
        """
        INSERT INTO users (email, password_hash, role) VALUES (...).

        The password field in the User entity MUST already be a bcrypt hash
        before calling this method. The repository never hashes passwords.

        Args:
            user : Domain User entity (user.password should be a bcrypt hash).

        Returns:
            The persisted User entity with the database-generated id.
        """
        db_user = UserModel(
            email=user.email,
            password_hash=user.password,  # already bcrypt-hashed by AuthService
            role=user.role.value,
        )
        self._db.add(db_user)
        self._db.commit()
        self._db.refresh(db_user)     # Reload to get auto-generated id and timestamps
        return self._to_domain(db_user)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        SELECT * FROM users WHERE id = :user_id.

        Args:
            user_id : The integer primary key.

        Returns:
            Domain User entity if found, None otherwise.
        """
        model = (
            self._db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def find_admin(self) -> Optional[User]:
        """
        SELECT * FROM users WHERE role = 'ADMIN' LIMIT 1.

        Used at startup to determine if the seed admin needs to be created.

        Returns:
            A User with ADMIN role if one exists, None otherwise.
        """
        model = (
            self._db.query(UserModel)
            .filter(UserModel.role == UserRole.ADMIN.value)
            .first()
        )
        return self._to_domain(model) if model else None
