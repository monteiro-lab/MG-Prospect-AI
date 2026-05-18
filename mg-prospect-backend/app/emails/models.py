from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String
from datetime import datetime
from typing import Optional
from app.core.database import Base

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    subject: Mapped[str]
    html_body: Mapped[str]

class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(index=True)
    campaign_id: Mapped[Optional[int]] = mapped_column(index=True, nullable=True)
    recipient_email: Mapped[str]
    subject: Mapped[str]
    status: Mapped[str] = mapped_column(default="sent") # sent, failed, skipped
    provider: Mapped[str] = mapped_column(default="brevo")
    provider_message_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)