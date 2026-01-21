from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class OrderItem(BaseModel):
    """Item in an order"""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class Order(BaseModel):
    """Order model"""
    id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    items: List[OrderItem]
    total: Decimal
    status: str = "pending"
    external_order_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Create order request"""
    items: List[dict]  # [{product_id, quantity}]


class OrderConfirm(BaseModel):
    """Confirm order request"""
    order_id: UUID
    confirmed: bool
