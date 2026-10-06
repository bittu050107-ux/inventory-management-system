"""
Application DTOs: order_dto.py (Order Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic schemas for Order request/response validation.
These cross the API boundary — they are NOT domain entities.

Schemas:
  Requests  → OrderItemRequest, CreateOrderRequest, UpdateOrderStatusRequest
  Responses → OrderItemResponse, OrderResponse, OrderListResponse
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────────────────────────

class OrderItemRequest(BaseModel):
    """A single line item in a create-order request."""
    product_id: int = Field(
        ...,
        gt=0,
        description="ID of the product to order",
        example=1,
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Number of units to order (must be > 0)",
        example=3,
    )
    unit_price: float = Field(
        ...,
        gt=0,
        description="Price per unit at the time of order (snapshot)",
        example=299.99,
    )


class CreateOrderRequest(BaseModel):
    """Payload for POST /orders — create a new order."""
    items: List[OrderItemRequest] = Field(
        ...,
        min_length=1,
        description="At least one order item is required",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional instructions or delivery notes",
        example="Please deliver before 6PM",
    )

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v: List[OrderItemRequest]) -> List[OrderItemRequest]:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class UpdateOrderStatusRequest(BaseModel):
    """Payload for PATCH /orders/{order_id}/status — update order status."""
    status: str = Field(
        ...,
        description="New status: CONFIRMED, SHIPPED, DELIVERED, or CANCELLED",
        example="CONFIRMED",
    )

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        allowed = {"PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"}
        if v.upper() not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        return v.upper()


# ─────────────────────────────────────────────────────────────
# RESPONSE SCHEMAS
# ─────────────────────────────────────────────────────────────

class OrderItemResponse(BaseModel):
    """Response representation of a single order line item."""
    id: int = Field(..., description="Line item ID")
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., description="Units ordered")
    unit_price: float = Field(..., description="Price per unit at order time")
    total_price: float = Field(..., description="quantity × unit_price")

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Full order response including all items."""
    id: int = Field(..., description="Order primary key")
    user_id: str = Field(..., description="Placing user's ID (JWT sub)")
    status: str = Field(..., description="Current order lifecycle status")
    notes: Optional[str] = Field(default=None, description="Order notes")
    total_amount: float = Field(..., description="Sum of all item totals")
    items: List[OrderItemResponse] = Field(..., description="Line items in this order")
    created_at: Optional[datetime] = Field(default=None, description="Order creation time")
    updated_at: Optional[datetime] = Field(default=None, description="Last update time")

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Paginated/listed orders response."""
    total: int = Field(..., description="Total number of orders returned")
    orders: List[OrderResponse] = Field(..., description="List of order objects")
