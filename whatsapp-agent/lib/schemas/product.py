from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class Category(BaseModel):
    """Product category"""
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    display_order: int = 0

    class Config:
        from_attributes = True


class Product(BaseModel):
    """Product model"""
    id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: Decimal
    available: bool = True

    class Config:
        from_attributes = True


class Recipe(BaseModel):
    """Recipe model"""
    id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    name: str
    ingredients: List[Dict[str, Any]]
    instructions: str
    tips: Optional[str] = None

    class Config:
        from_attributes = True
