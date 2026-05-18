from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
from datetime import datetime
import os

from app.core.database import get_db
from app.leads.models import Lead, LeadInterest
from app.public.schemas import LeadInterestCreate, LeadInterestResponse

from app.core.config import settings

router = APIRouter()

async def send_to_n8n(webhook_url: str, payload: dict, interest_id: int):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(webhook_url, json=payload)
            if res.status_code >= 400:
                print(f"n8n webhook error: {res.status_code} - {res.text}")
                # We could update the status to 'error' here if we passed a DB session,
                # but for background task simplicity we just log it.
            else:
                print(f"n8n webhook success for interest {interest_id}")
    except Exception as e:
        print(f"Failed to send webhook to n8n: {e}")

@router.get("/interest/{lead_token}")
async def get_lead_by_token(lead_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.public_token == lead_token))
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead inválido ou expirado")
        
    return {
        "company_name": lead.name,
        "city": lead.city,
        "segment": lead.category
    }

@router.post("/interest", response_model=LeadInterestResponse)
async def submit_interest(
    data: LeadInterestCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    if not data.consent:
        raise HTTPException(status_code=400, detail="O consentimento é obrigatório")

    lead = None
    if data.lead_token:
        result = await db.execute(select(Lead).where(Lead.public_token == data.lead_token))
        lead = result.scalars().first()

    interest = LeadInterest(
        lead_id=lead.id if lead else None,
        lead_token=data.lead_token,
        company_name=data.company_name,
        contact_name=data.contact_name,
        email=data.email,
        phone=data.phone,
        city=data.city,
        segment=data.segment,
        preferred_contact_time=data.preferred_contact_time,
        message=data.message,
        consent=data.consent,
        status="sent_to_n8n" if settings.N8N_WEBHOOK_LEAD_INTEREST_URL else "new"
    )
    
    db.add(interest)
    
    if lead:
        # Update lead status to "interessado" if not already client
        if lead.status not in ["CLIENTE", "EM NEGOCIAÇÃO"]:
            lead.status = "INTERESSADO"
        lead.updated_at = datetime.utcnow()
        
    await db.commit()
    await db.refresh(interest)
    
    webhook_url = settings.N8N_WEBHOOK_LEAD_INTEREST_URL
    if webhook_url:
        payload = {
            "event": "lead_interest_created",
            "source": "mg_prospect_ai",
            "lead": {
                "id": lead.id,
                "public_token": lead.public_token,
                "company_name": lead.name,
                "segment": lead.category,
                "city": lead.city,
                "state": lead.state,
                "phone": lead.phone,
                "email": lead.email
            } if lead else None,
            "interest": {
                "id": interest.id,
                "contact_name": interest.contact_name,
                "email": interest.email,
                "phone": interest.phone,
                "preferred_contact_time": interest.preferred_contact_time,
                "message": interest.message,
                "consent": interest.consent,
                "created_at": interest.created_at.isoformat()
            }
        }
        background_tasks.add_task(send_to_n8n, webhook_url, payload, interest.id)
        
    return {"msg": "Interesse registrado com sucesso. Entraremos em contato em breve!"}

@router.post("/unsubscribe/{lead_token}")
async def unsubscribe_lead(lead_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.public_token == lead_token))
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Link de cancelamento inválido ou expirado")
        
    lead.do_not_contact = True
    lead.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"msg": "Você foi removido com sucesso de nossa lista de contatos."}
