from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.campaigns.models import Campaign, CampaignLog
from app.leads.models import Lead
from app.leads.service import calculate_lead_score
from app.integrations.google_places import fetch_places_from_google, fetch_place_details
from app.integrations.email_discovery import discover_email
from datetime import datetime

async def process_campaign_discovery(campaign_id: int):
    """
    Roda em background de forma segura, gerenciando sua própria sessão do banco de dados.
    Agora inclui enriquecimento via Google Places Details API e salva logs do progresso.
    """
    async with AsyncSessionLocal() as db:
        # 1. Busca a campanha
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalars().first()
        
        if not campaign:
            return

        async def log_event(message: str, level: str = "info"):
            log = CampaignLog(campaign_id=campaign.id, message=message, level=level)
            db.add(log)
            await db.commit()
            
        try:
            # 2. Atualiza status
            campaign.status = "RODANDO"
            campaign.total_found = 0
            campaign.total_saved = 0
            campaign.total_duplicates = 0
            campaign.total_errors = 0
            await db.commit()
            
            await log_event(f"Iniciando campanha: {campaign.name}", "info")
            await log_event(f"Consultando Google Places para palavra-chave '{campaign.keyword}' em {campaign.target_city}/{campaign.target_state}", "info")
            
            # 3. Busca no Google
            places = await fetch_places_from_google(
                keyword=campaign.keyword,
                city=campaign.target_city,
                state=campaign.target_state,
                api_key=settings.GOOGLE_PLACES_API_KEY,
                max_results=campaign.max_leads
            )
            
            campaign.total_found = len(places)
            await db.commit()
            
            if not places:
                await log_event("A busca não retornou resultados.", "warning")
            else:
                await log_event(f"Google Places retornou {len(places)} potenciais leads. Iniciando processamento...", "info")
            
            # 4. Processa e salva Leads, evitando duplicidade
            for place in places:
                name = place.get("name")
                place_id = place.get("place_id")
                
                # Regra Antiduplicidade: Verifica se já existe um lead com esse nome
                existing = await db.execute(select(Lead).where(Lead.name == name))
                if existing.scalars().first():
                    campaign.total_duplicates += 1
                    await log_event(f"Ignorado por duplicidade: {name}", "warning")
                    continue

                import secrets
                # Dados básicos da Text Search
                new_lead = Lead(
                    public_token=secrets.token_urlsafe(16),
                    campaign_id=campaign.id,
                    name=name,
                    place_id=place_id,
                    category=campaign.keyword,
                    city=campaign.target_city,
                    state=campaign.target_state,
                    rating=place.get("rating", 0.0),
                    review_count=place.get("user_ratings_total", 0),
                    address=place.get("formatted_address"),
                    business_status=place.get("business_status"),
                    status="NOVO"
                )
                
                # Extrair coordenadas da busca básica
                geometry = place.get("geometry", {})
                location = geometry.get("location", {})
                new_lead.latitude = location.get("lat")
                new_lead.longitude = location.get("lng")
                
                # 5. Enriquecimento via Place Details (telefone, site, etc.)
                if place_id and settings.GOOGLE_PLACES_API_KEY:
                    try:
                        details = await fetch_place_details(
                            place_id=place_id,
                            api_key=settings.GOOGLE_PLACES_API_KEY
                        )
                        if details:
                            if details.get("phone"):
                                new_lead.phone = details["phone"]
                            if details.get("international_phone"):
                                new_lead.international_phone = details["international_phone"]
                            if details.get("website"):
                                new_lead.website = details["website"]
                            if details.get("address"):
                                new_lead.address = details["address"]
                            if details.get("business_status"):
                                new_lead.business_status = details["business_status"]
                            if details.get("google_maps_url"):
                                new_lead.google_maps_url = details["google_maps_url"]
                            if details.get("opening_hours"):
                                new_lead.opening_hours = details["opening_hours"]
                            if details.get("rating"):
                                new_lead.rating = details["rating"]
                            if details.get("review_count"):
                                new_lead.review_count = details["review_count"]
                            if details.get("latitude"):
                                new_lead.latitude = details["latitude"]
                            if details.get("longitude"):
                                new_lead.longitude = details["longitude"]
                                
                        await log_event(f"Lead processado: {name}", "success")
                    except Exception as e:
                        campaign.total_errors += 1
                        await log_event(f"Aviso ao enriquecer '{name}': API Google retornou erro", "error")
                
                # 6. Email Discovery: se não temos e-mail mas temos website, tenta scraping
                if not new_lead.email and new_lead.website:
                    try:
                        discovered_email = await discover_email(new_lead.website)
                        if discovered_email:
                            new_lead.email = discovered_email
                            await log_event(f"E-mail descoberto para {name}: {discovered_email}", "success")
                        else:
                            await log_event(f"Nenhum e-mail encontrado no site de {name}", "info")
                    except Exception as e:
                        await log_event(f"Falha no email discovery para {name}", "warning")

                # Aplica nossa regra de inteligência contábil
                new_lead.score = calculate_lead_score(new_lead)
                
                db.add(new_lead)
                campaign.total_saved += 1
                await db.commit()

            campaign.status = "CONCLUIDO"
            campaign.finished_at = datetime.utcnow()
            await log_event(f"Busca finalizada! {campaign.total_saved} novos leads salvos.", "success")
            await db.commit()
            
        except Exception as e:
            campaign.status = "ERRO"
            campaign.finished_at = datetime.utcnow()
            await log_event(f"Falha na campanha: ocorreu um erro inesperado no sistema.", "error")
            await db.commit()