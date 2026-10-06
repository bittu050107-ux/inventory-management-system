"""
Application Service: SupplierService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Encapsulates all Supplier business logic.
Depends strictly on repository interfaces.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List
from app.application.dto.supplier_dto import (
    SupplierCreateRequest,
    SupplierUpdateRequest,
    SupplierResponse,
)
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.domain.entities.supplier import Supplier
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.repositories.product_repository import ProductRepository


class SupplierService:
    """Service handling supplier business workflows."""

    def __init__(
        self,
        supplier_repository: SupplierRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._supplier_repo = supplier_repository
        self._product_repo = product_repository

    def create_supplier(self, request: SupplierCreateRequest) -> SupplierResponse:
        """Create a new supplier record."""
        domain_supplier = Supplier(
            name=request.name,
            email=request.email,
            phone=request.phone,
            address=request.address,
        )
        saved = self._supplier_repo.create(domain_supplier)
        return SupplierResponse(
            id=saved.id,
            name=saved.name,
            email=saved.email,
            phone=saved.phone,
            address=saved.address,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    def get_supplier_by_id(self, supplier_id: int) -> SupplierResponse:
        """Fetch supplier by id or raise NotFoundError."""
        supplier = self._supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")

        return SupplierResponse(
            id=supplier.id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
        )

    def get_all_suppliers(self) -> List[SupplierResponse]:
        """Fetch all suppliers."""
        suppliers = self._supplier_repo.get_all()
        return [
            SupplierResponse(
                id=s.id,
                name=s.name,
                email=s.email,
                phone=s.phone,
                address=s.address,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in suppliers
        ]

    def update_supplier(
        self, supplier_id: int, request: SupplierUpdateRequest
    ) -> SupplierResponse:
        """Update existing supplier details."""
        existing = self._supplier_repo.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")

        if request.name is not None:
            existing.name = request.name
        if request.email is not None:
            existing.email = request.email
        if request.phone is not None:
            existing.phone = request.phone
        if request.address is not None:
            existing.address = request.address

        updated = self._supplier_repo.update(existing)
        return SupplierResponse(
            id=updated.id,
            name=updated.name,
            email=updated.email,
            phone=updated.phone,
            address=updated.address,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    def delete_supplier(self, supplier_id: int) -> None:
        """Delete supplier if no products are associated with it."""
        existing = self._supplier_repo.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")

        product_count = self._product_repo.count_by_supplier(supplier_id)
        if product_count > 0:
            raise BusinessRuleError(
                f"Cannot delete supplier '{existing.name}' because {product_count} product(s) are assigned to it"
            )

        self._supplier_repo.delete(supplier_id)
