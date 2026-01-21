from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class Customer(BaseModel):
    """Customer model"""
    id: Optional[UUID] = None
    phone_number: str
    name: Optional[str] = None
    preferences: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    """Create customer request"""
    phone_number: str
    name: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Update customer request"""
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
