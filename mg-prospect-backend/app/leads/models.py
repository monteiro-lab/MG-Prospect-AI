from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    public_token: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=True)
    campaign_id: Mapped[int] = mapped_column(index=True, nullable=True)
    name: Mapped[str] = mapped_column(index=True)
    category: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    international_phone: Mapped[str] = mapped_column(nullable=True)
    website: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    
    # Google Places
    place_id: Mapped[str] = mapped_column(nullable=True, index=True)
    google_maps_url: Mapped[str] = mapped_column(nullable=True)
    business_status: Mapped[str] = mapped_column(nullable=True)
    opening_hours: Mapped[str] = mapped_column(nullable=True)
    
    rating: Mapped[float] = mapped_column(default=0.0)
    review_count: Mapped[int] = mapped_column(default=0)
    
    score: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(default="NOVO")
    
    # Controles LGPD / Anti-spam
    do_not_contact: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

class LeadInterest(Base):
    __tablename__ = "lead_interests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    lead_token: Mapped[str] = mapped_column(String, index=True, nullable=True)
    company_name: Mapped[str] = mapped_column(String)
    contact_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String, nullable=True)
    segment: Mapped[str] = mapped_column(String, nullable=True)
    preferred_contact_time: Mapped[str] = mapped_column(String, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    consent: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String, default="email_cta")
    status: Mapped[str] = mapped_column(String, default="new")
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)