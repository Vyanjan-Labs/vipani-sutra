from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ListingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    price: Optional[float] = None
    original_price: Optional[float] = None
    city: str
    locality: Optional[str] = None
    contact_number: str

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    locality: Optional[str] = None
    contact_number: Optional[str] = None
    status: Optional[str] = None
    buyer_user_id: Optional[int] = Field(
        None,
        description="Buyer user id — set by seller when marking a sale (needed for mutual ratings).",
    )

class ListingOut(BaseModel):
    id: int
    user_id: int
    buyer_user_id: Optional[int] = None
    title: str
    description: Optional[str]
    category: str
    price: Optional[float]
    original_price: Optional[float]
    images: List[str]
    city: str
    locality: Optional[str]
    contact_number: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ListingFilters(BaseModel):
    city: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
