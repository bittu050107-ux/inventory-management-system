"""
Infrastructure Repository: CategoryRepositoryImpl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL implementation of CategoryRepository via SQLAlchemy.
Translates between CategoryModel (ORM) and Category (domain entity).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities.category import Category
from app.domain.repositories.category_repository import CategoryRepository
from app.infrastructure.database.models import CategoryModel


class CategoryRepositoryImpl(CategoryRepository):
    """PostgreSQL-backed Category repository implementation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: CategoryModel) -> Category:
        """Map ORM model to domain entity."""
        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def create(self, category: Category) -> Category:
        db_category = CategoryModel(
            name=category.name,
            description=category.description,
        )
        self._db.add(db_category)
        self._db.commit()
        self._db.refresh(db_category)
        return self._to_domain(db_category)

    def get_by_id(self, category_id: int) -> Optional[Category]:
        model = (
            self._db.query(CategoryModel)
            .filter(CategoryModel.id == category_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_by_name(self, name: str) -> Optional[Category]:
        model = (
            self._db.query(CategoryModel)
            .filter(CategoryModel.name == name)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_all(self) -> List[Category]:
        models = self._db.query(CategoryModel).order_by(CategoryModel.id).all()
        return [self._to_domain(m) for m in models]

    def update(self, category: Category) -> Optional[Category]:
        db_category = (
            self._db.query(CategoryModel)
            .filter(CategoryModel.id == category.id)
            .first()
        )
        if not db_category:
            return None

        db_category.name = category.name
        db_category.description = category.description
        self._db.commit()
        self._db.refresh(db_category)
        return self._to_domain(db_category)

    def delete(self, category_id: int) -> bool:
        db_category = (
            self._db.query(CategoryModel)
            .filter(CategoryModel.id == category_id)
            .first()
        )
        if not db_category:
            return False

        self._db.delete(db_category)
        self._db.commit()
        return True
