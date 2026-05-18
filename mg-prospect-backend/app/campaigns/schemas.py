from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CampaignBase(BaseModel):
    name: str
    target_city: str
    target_state: str
    radius_km: Optional[int] = 5
    keyword: str
    max_leads: Optional[int] = 100

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    id: int
    status: str
    total_found: int
    total_saved: int
    total_duplicates: int
    total_errors: int
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CampaignLogResponse(BaseModel):
    id: int
    campaign_id: int
    level: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)