from app.leads.models import Lead

def calculate_lead_score(lead: Lead) -> int:
    """
    Calcula o score inteligente contábil (0 a 100) com base nos dados enriquecidos.
    
    Critérios de pontuação:
    - +20 se possui telefone
    - +20 se possui website
    - +10 se possui endereço completo
    - +15 se possui rating >= 4.0
    - +10 se possui review_count >= 5
    - +15 se está em cidade-alvo (Petrolina/PE ou Juazeiro/BA)
    - +10 se business_status indica operação ativa
    """
    score = 0
    
    # Dados de contato enriquecidos
    if lead.phone or lead.international_phone:
        score += 20
    if lead.website:
        score += 20
    if lead.address:
        score += 10
    
    # Qualidade e reputação digital
    if lead.rating and lead.rating >= 4.0:
        score += 15
    if lead.review_count and lead.review_count >= 5:
        score += 10
    
    # Bônus geográfico (Vale do São Francisco)
    target_cities = ["petrolina", "juazeiro"]
    if lead.city and lead.city.lower() in target_cities:
        score += 15
        
    # Empresa em operação ativa
    if lead.business_status and lead.business_status.upper() == "OPERATIONAL":
        score += 10
        
    return min(score, 100)