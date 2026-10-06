"""
API Routes: categories.py (Product Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category CRUD endpoints.
Admin only: POST, PUT, DELETE
Authenticated users: GET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_category_service,
    get_current_user,
    require_admin,
)
from app.application.dto.category_dto import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
)
from app.application.services.category_service import CategoryService
from app.core.exceptions import (
    NotFoundError,
    DuplicateResourceError,
    BusinessRuleError,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category (Admin only)",
)
def create_category(
    request: CategoryCreateRequest,
    service: CategoryService = Depends(get_category_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> CategoryResponse:
    """Create a new category. Requires ADMIN role."""
    try:
        return service.create_category(request)
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="List all categories (Authenticated)",
)
def list_categories(
    service: CategoryService = Depends(get_category_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[CategoryResponse]:
    """List all categories. Accessible by any authenticated user."""
    return service.get_all_categories()


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID (Authenticated)",
)
def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> CategoryResponse:
    """Get single category details. Accessible by any authenticated user."""
    try:
        return service.get_category_by_id(category_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category (Admin only)",
)
def update_category(
    category_id: int,
    request: CategoryUpdateRequest,
    service: CategoryService = Depends(get_category_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> CategoryResponse:
    """Update existing category details. Requires ADMIN role."""
    try:
        return service.update_category(category_id, request)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DuplicateResourceError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category (Admin only)",
)
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    _admin: Dict[str, Any] = Depends(require_admin),
) -> None:
    """Delete a category. Fails if products are linked. Requires ADMIN role."""
    try:
        service.delete_category(category_id)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except BusinessRuleError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
