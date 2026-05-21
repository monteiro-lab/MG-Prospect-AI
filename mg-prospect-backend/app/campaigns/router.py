from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.auth.router import get_current_user
from app.campaigns.models import Campaign, CampaignLog
from app.campaigns.schemas import CampaignCreate, CampaignResponse, CampaignLogResponse
from app.campaigns.service import process_campaign_discovery

router = APIRouter()

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_in: CampaignCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db), 
    # current_user = Depends(get_current_user)
):
    # Cria a campanha no banco
    new_campaign = Campaign(**campaign_in.model_dump())
    db.add(new_campaign)
    await db.commit()
    await db.refresh(new_campaign)
    
    # Futuramente: Aqui vamos disparar a "Task" em background para buscar no Google Places
    background_tasks.add_task(process_campaign_discovery, new_campaign.id)
    
    return new_campaign

@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(Campaign).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign

@router.get("/{campaign_id}/logs", response_model=List[CampaignLogResponse])
async def get_campaign_logs(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(CampaignLog)
        .where(CampaignLog.campaign_id == campaign_id)
        .order_by(CampaignLog.created_at.asc())
    )
    return result.scalars().all()