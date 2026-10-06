"""
Domain Repository Interface: UserRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract interface defining ALL user data operations.

Clean Architecture Rule:
  - Domain defines the interface (what)
  - Infrastructure implements the interface (how)
  - Application layer depends ONLY on this interface

This makes it trivial to swap implementations:
  In-memory dict → PostgreSQL → MongoDB
  ...without changing a single line of application logic.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    """
    Abstract repository contract for User data access.

    Any class wanting to act as a user repository MUST implement
    all abstract methods here. This enforces consistent behavior
    regardless of the underlying storage technology.
    """

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address.

        Args:
            email : The email address to search for.

        Returns:
            The User domain entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, user: User) -> User:
        """
        Persist a new user and return the saved entity with generated ID.

        The caller is responsible for hashing the password before
        passing the User entity here. The repository does NOT hash.

        Args:
            user : The User domain entity to persist (id may be None).

        Returns:
            The persisted User entity with the database-generated id.
        """
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by their integer primary key.

        Args:
            user_id : The unique integer ID.

        Returns:
            The User domain entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_admin(self) -> Optional[User]:
        """
        Find the first ADMIN user in the system.

        Used at startup to check whether an admin seed is needed.

        Returns:
            An ADMIN User entity if one exists, None otherwise.
        """
        ...
