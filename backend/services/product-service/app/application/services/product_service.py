"""
Application Service: ProductService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Encapsulates all Product business logic:
  - Category existence verification
  - Supplier existence verification
  - SKU uniqueness check
  - Product persistence via domain repository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List
from app.application.dto.product_dto import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from app.core.exceptions import NotFoundError, DuplicateResourceError, BusinessRuleError
from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.supplier_repository import SupplierRepository


class ProductService:
    """Service orchestrating product business workflows."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        supplier_repository: SupplierRepository,
    ) -> None:
        self._product_repo = product_repository
        self._category_repo = category_repository
        self._supplier_repo = supplier_repository

    def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """
        Validate dependencies, check SKU uniqueness, and create a new product.
        """
        # 1. Validate category exists
        category = self._category_repo.get_by_id(request.category_id)
        if not category:
            raise NotFoundError(
                f"Category with ID {request.category_id} does not exist"
            )

        # 2. Validate supplier exists
        supplier = self._supplier_repo.get_by_id(request.supplier_id)
        if not supplier:
            raise NotFoundError(
                f"Supplier with ID {request.supplier_id} does not exist"
            )

        # 3. Check SKU uniqueness
        existing_sku = self._product_repo.get_by_sku(request.sku)
        if existing_sku:
            raise DuplicateResourceError(
                f"Product with SKU '{request.sku}' already exists"
            )

        # 4. Construct domain entity
        domain_product = Product(
            name=request.name,
            sku=request.sku,
            description=request.description,
            price=request.price,
            category_id=request.category_id,
            supplier_id=request.supplier_id,
            is_active=True,
        )

        # 5. Persist via repository
        saved = self._product_repo.create(domain_product)

        # 6. Return response DTO
        return ProductResponse(
            id=saved.id,
            name=saved.name,
            sku=saved.sku,
            description=saved.description,
            price=saved.price,
            category_id=saved.category_id,
            supplier_id=saved.supplier_id,
            is_active=saved.is_active,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        """Retrieve single product by id or raise NotFoundError."""
        product = self._product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")

        return ProductResponse(
            id=product.id,
            name=product.name,
            sku=product.sku,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            supplier_id=product.supplier_id,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
        """Retrieve paginated list of products."""
        products = self._product_repo.get_all(skip=skip, limit=limit)
        return [
            ProductResponse(
                id=p.id,
                name=p.name,
                sku=p.sku,
                description=p.description,
                price=p.price,
                category_id=p.category_id,
                supplier_id=p.supplier_id,
                is_active=p.is_active,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in products
        ]

    def update_product(
        self, product_id: int, request: ProductUpdateRequest
    ) -> ProductResponse:
        """Validate changes and update an existing product."""
        existing = self._product_repo.get_by_id(product_id)
        if not existing:
            raise NotFoundError(f"Product with ID {product_id} not found")

        # Validate category if changed
        if request.category_id is not None and request.category_id != existing.category_id:
            category = self._category_repo.get_by_id(request.category_id)
            if not category:
                raise NotFoundError(
                    f"Category with ID {request.category_id} does not exist"
                )
            existing.category_id = request.category_id

        # Validate supplier if changed
        if request.supplier_id is not None and request.supplier_id != existing.supplier_id:
            supplier = self._supplier_repo.get_by_id(request.supplier_id)
            if not supplier:
                raise NotFoundError(
                    f"Supplier with ID {request.supplier_id} does not exist"
                )
            existing.supplier_id = request.supplier_id

        # Validate SKU uniqueness if changed
        if request.sku is not None and request.sku != existing.sku:
            duplicate = self._product_repo.get_by_sku(request.sku)
            if duplicate and duplicate.id != product_id:
                raise DuplicateResourceError(
                    f"Product with SKU '{request.sku}' already exists"
                )
            existing.sku = request.sku

        if request.name is not None:
            existing.name = request.name
        if request.description is not None:
            existing.description = request.description
        if request.price is not None:
            existing.price = request.price
        if request.is_active is not None:
            existing.is_active = request.is_active

        updated = self._product_repo.update(existing)
        return ProductResponse(
            id=updated.id,
            name=updated.name,
            sku=updated.sku,
            description=updated.description,
            price=updated.price,
            category_id=updated.category_id,
            supplier_id=updated.supplier_id,
            is_active=updated.is_active,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    def delete_product(self, product_id: int) -> None:
        """Delete product by primary key."""
        existing = self._product_repo.get_by_id(product_id)
        if not existing:
            raise NotFoundError(f"Product with ID {product_id} not found")

        self._product_repo.delete(product_id)
