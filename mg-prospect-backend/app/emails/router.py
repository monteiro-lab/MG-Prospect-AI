from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.emails.models import EmailTemplate
from app.emails.schemas import EmailTemplateCreate, EmailTemplateResponse

router = APIRouter()

@router.post("/", response_model=EmailTemplateResponse)
async def create_template(template_in: EmailTemplateCreate, db: AsyncSession = Depends(get_db)):
    new_template = EmailTemplate(**template_in.model_dump())
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    return new_template

@router.get("/", response_model=List[EmailTemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmailTemplate))
    return result.scalars().all()

from fastapi import HTTPException
from app.leads.models import Lead
from app.emails.schemas import EmailPreviewRequest, EmailPreviewResponse, EmailSendRequest
from app.emails.models import EmailLog
from app.integrations.email_provider import send_prospect_email
from datetime import datetime
import re

from app.emails.templates import render_email_template, format_email_html

def strip_tags(html: str) -> str:
    return re.sub('<[^<]+?>', '', html)

@router.post("/preview", response_model=EmailPreviewResponse)
async def preview_email(req: EmailPreviewRequest, db: AsyncSession = Depends(get_db)):
    lead = (await db.execute(select(Lead).where(Lead.id == req.lead_id))).scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
        
    template = (await db.execute(select(EmailTemplate).where(EmailTemplate.id == req.template_id))).scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
        
    lead_dict = {
        "id": lead.id,
        "public_token": lead.public_token,
        "name": lead.name,
        "city": lead.city,
        "state": lead.state,
        "category": lead.category,
        "phone": lead.phone,
        "website": lead.website,
        "email": lead.email
    }
    
    subject = render_email_template(template.subject, lead_dict)
    raw_body = render_email_template(template.html_body, lead_dict)
    html_body = format_email_html(raw_body, lead.public_token)
    
    return {
        "subject": subject,
        "html_body": html_body,
        "text_body": strip_tags(raw_body),
        "lead_data": {
            "name": lead.name,
            "email": lead.email
        }
    }

@router.post("/send")
async def send_email(req: EmailSendRequest, db: AsyncSession = Depends(get_db)):
    lead = (await db.execute(select(Lead).where(Lead.id == req.lead_id))).scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
        
    if not lead.email:
        raise HTTPException(status_code=400, detail="Lead não possui e-mail cadastrado")
        
    if lead.do_not_contact:
        raise HTTPException(status_code=400, detail="Lead marcado como não contatar")
        
    template = (await db.execute(select(EmailTemplate).where(EmailTemplate.id == req.template_id))).scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
        
    lead_dict = {
        "id": lead.id,
        "public_token": lead.public_token,
        "name": lead.name,
        "city": lead.city,
        "state": lead.state,
        "category": lead.category,
        "phone": lead.phone,
        "website": lead.website,
        "email": lead.email
    }
    
    subject = render_email_template(template.subject, lead_dict)
    raw_body = render_email_template(template.html_body, lead_dict)
    html_body = format_email_html(raw_body, lead.public_token)
    
    result = await send_prospect_email(
        to_email=lead.email,
        subject=subject,
        html_content=html_body
    )
    
    # Save log
    log = EmailLog(
        lead_id=lead.id,
        campaign_id=lead.campaign_id,
        recipient_email=lead.email,
        subject=subject,
        status="sent" if result["success"] else "failed",
        provider_message_id=result.get("message_id"),
        error_message=result.get("error"),
        sent_at=datetime.utcnow() if result["success"] else None
    )
    db.add(log)
    
    if result["success"]:
        lead.status = "PROSPECTADO"
        lead.updated_at = datetime.utcnow()
        await db.commit()
        return {"msg": "E-mail enviado com sucesso"}
    else:
        await db.commit()
        raise HTTPException(status_code=502, detail=f"Falha ao enviar e-mail: {result.get('error')}")