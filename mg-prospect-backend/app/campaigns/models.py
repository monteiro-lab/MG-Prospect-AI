from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from app.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    target_city: Mapped[str]
    target_state: Mapped[str]
    radius_km: Mapped[int] = mapped_column(default=5)
    keyword: Mapped[str]
    max_leads: Mapped[int] = mapped_column(default=100)
    
    # Status possíveis: AGUARDANDO, RODANDO, CONCLUIDO, PAUSADO, ERRO
    status: Mapped[str] = mapped_column(default="AGUARDANDO")
    
    total_found: Mapped[int] = mapped_column(default=0)
    total_saved: Mapped[int] = mapped_column(default=0)
    total_duplicates: Mapped[int] = mapped_column(default=0)
    total_errors: Mapped[int] = mapped_column(default=0)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(nullable=True)


class CampaignLog(Base):
    __tablename__ = "campaign_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(index=True)
    level: Mapped[str] = mapped_column(default="info")  # info, success, warning, error
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)