from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    name: str
    category: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    international_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_id: Optional[str] = None
    google_maps_url: Optional[str] = None
    business_status: Optional[str] = None
    opening_hours: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0

class LeadCreate(LeadBase):
    campaign_id: Optional[int] = None

class LeadResponse(LeadBase):
    id: int
    score: int
    status: str
    do_not_contact: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedLeadResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int