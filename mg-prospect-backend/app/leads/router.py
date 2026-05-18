from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.auth.router import get_current_user
from app.leads.models import Lead
from app.leads.schemas import LeadCreate, LeadResponse
from app.leads.service import calculate_lead_score
from app.integrations.google_places import fetch_place_details
from pydantic import BaseModel

router = APIRouter()

@router.post("/", response_model=LeadResponse)
async def create_lead(lead_in: LeadCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    import secrets
    new_lead = Lead(**lead_in.model_dump(), public_token=secrets.token_urlsafe(16))
    
    # Calcular score no momento da criação
    new_lead.score = calculate_lead_score(new_lead)
    
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

from app.leads.schemas import LeadCreate, LeadResponse, PaginatedLeadResponse
from sqlalchemy import func, or_, desc, asc
from typing import Optional

@router.get("/", response_model=PaginatedLeadResponse)
async def list_leads(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    campaign_id: Optional[int] = None,
    has_email: Optional[bool] = None,
    min_score: Optional[int] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    query = select(Lead)
    
    # Filters
    if search:
        query = query.where(or_(
            Lead.name.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%")
        ))
    if status:
        query = query.where(Lead.status == status)
    if city:
        query = query.where(Lead.city.ilike(f"%{city}%"))
    if state:
        query = query.where(Lead.state.ilike(f"%{state}%"))
    if category:
        query = query.where(Lead.category.ilike(f"%{category}%"))
    if campaign_id:
        query = query.where(Lead.campaign_id == campaign_id)
    if has_email is True:
        query = query.where(Lead.email.isnot(None))
    elif has_email is False:
        query = query.where(Lead.email.is_(None))
    if min_score is not None:
        query = query.where(Lead.score >= min_score)
        
    # Sorting
    if hasattr(Lead, sort_by):
        column = getattr(Lead, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))
    else:
        query = query.order_by(desc(Lead.created_at))

    # Total Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

class LeadUpdateStage(BaseModel):
    status: str

@router.patch("/{lead_id}/stage", response_model=LeadResponse)
async def update_lead_stage(
    lead_id: int, 
    stage_in: LeadUpdateStage, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
        
    lead.status = stage_in.status
    await db.commit()
    await db.refresh(lead)
    return lead


@router.post("/{lead_id}/refresh-google-data", response_model=LeadResponse)
async def refresh_google_data(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """
    Atualiza os dados do lead via Google Places Details API.
    Regra: não sobrescreve dados existentes com valores vazios.
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if not lead.place_id:
        raise HTTPException(status_code=400, detail="Lead não possui place_id para consulta no Google")
    
    if not settings.GOOGLE_PLACES_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_PLACES_API_KEY não configurada no servidor")
    
    # Buscar detalhes atualizados
    details = await fetch_place_details(
        place_id=lead.place_id,
        api_key=settings.GOOGLE_PLACES_API_KEY
    )
    
    if not details:
        raise HTTPException(status_code=502, detail="Não foi possível obter dados do Google Places")
    
    # Atualizar campos — NÃO sobrescrever dados bons com vazio
    if details.get("phone"):
        lead.phone = details["phone"]
    if details.get("international_phone"):
        lead.international_phone = details["international_phone"]
    if details.get("website"):
        lead.website = details["website"]
    if details.get("address"):
        lead.address = details["address"]
    if details.get("business_status"):
        lead.business_status = details["business_status"]
    if details.get("google_maps_url"):
        lead.google_maps_url = details["google_maps_url"]
    if details.get("opening_hours"):
        lead.opening_hours = details["opening_hours"]
    if details.get("rating"):
        lead.rating = details["rating"]
    if details.get("review_count"):
        lead.review_count = details["review_count"]
    if details.get("latitude"):
        lead.latitude = details["latitude"]
    if details.get("longitude"):
        lead.longitude = details["longitude"]
    
    # Recalcular score com os dados enriquecidos
    lead.score = calculate_lead_score(lead)
    lead.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(lead)
    return lead