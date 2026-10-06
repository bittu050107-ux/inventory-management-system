"""
Application Service: CategoryService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Encapsulates all Category business logic.
Depends strictly on repository interfaces, not SQLAlchemy models.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List
from app.application.dto.category_dto import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
)
from app.core.exceptions import NotFoundError, DuplicateResourceError, BusinessRuleError
from app.domain.entities.category import Category
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.product_repository import ProductRepository


class CategoryService:
    """Service handling category business workflows."""

    def __init__(
        self,
        category_repository: CategoryRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._category_repo = category_repository
        self._product_repo = product_repository

    def create_category(self, request: CategoryCreateRequest) -> CategoryResponse:
        """Validate uniqueness and create a new category."""
        existing = self._category_repo.get_by_name(request.name)
        if existing:
            raise DuplicateResourceError(f"Category with name '{request.name}' already exists")

        domain_category = Category(
            name=request.name,
            description=request.description,
        )
        saved = self._category_repo.create(domain_category)
        return CategoryResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    def get_category_by_id(self, category_id: int) -> CategoryResponse:
        """Fetch category by id or raise NotFoundError."""
        category = self._category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")

        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    def get_all_categories(self) -> List[CategoryResponse]:
        """Fetch all categories."""
        categories = self._category_repo.get_all()
        return [
            CategoryResponse(
                id=c.id,
                name=c.name,
                description=c.description,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in categories
        ]

    def update_category(
        self, category_id: int, request: CategoryUpdateRequest
    ) -> CategoryResponse:
        """Update category details with uniqueness verification."""
        existing = self._category_repo.get_by_id(category_id)
        if not existing:
            raise NotFoundError(f"Category with ID {category_id} not found")

        # If name is being changed, check uniqueness
        if request.name and request.name != existing.name:
            duplicate = self._category_repo.get_by_name(request.name)
            if duplicate and duplicate.id != category_id:
                raise DuplicateResourceError(
                    f"Category with name '{request.name}' already exists"
                )
            existing.name = request.name

        if request.description is not None:
            existing.description = request.description

        updated = self._category_repo.update(existing)
        return CategoryResponse(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    def delete_category(self, category_id: int) -> None:
        """Delete category if no products are associated with it."""
        existing = self._category_repo.get_by_id(category_id)
        if not existing:
            raise NotFoundError(f"Category with ID {category_id} not found")

        # Check if products depend on this category
        product_count = self._product_repo.count_by_category(category_id)
        if product_count > 0:
            raise BusinessRuleError(
                f"Cannot delete category '{existing.name}' because {product_count} product(s) are assigned to it"
            )

        self._category_repo.delete(category_id)
