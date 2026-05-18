from pydantic import BaseModel, Field
from typing import Optional

class LeadInterestCreate(BaseModel):
    lead_token: Optional[str] = None
    company_name: str
    contact_name: str
    email: str
    phone: str
    city: Optional[str] = None
    segment: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    message: Optional[str] = None
    consent: bool

class LeadInterestResponse(BaseModel):
    msg: str
