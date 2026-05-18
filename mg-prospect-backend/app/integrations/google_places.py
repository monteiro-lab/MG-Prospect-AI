import httpx
import asyncio
from typing import List, Dict, Any, Optional

async def fetch_places_from_google(keyword: str, city: str, state: str, api_key: str, max_results: int = 60) -> List[Dict[str, Any]]:
    """
    Busca empresas no Google Places (Text Search API).
    Lida automaticamente com paginação (next_page_token) para buscar mais de 20 resultados.
    """
    if not api_key:
        print("AVISO: GOOGLE_PLACES_API_KEY não configurada no .env. Ignorando busca.")
        return []

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{keyword} em {city} {state}"
    
    params = {
        "query": query,
        "key": api_key,
        "language": "pt-BR"
    }

    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while len(results) < max_results:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Erro na API do Google: {response.text}")
                break
                
            data = response.json()
            results.extend(data.get("results", []))
            
            next_page_token = data.get("next_page_token")
            if not next_page_token or len(results) >= max_results:
                break
                
            # O Google exige um pequeno delay antes do token ficar válido
            await asyncio.sleep(2)
            params = {"pagetoken": next_page_token, "key": api_key}

    return results[:max_results]


async def fetch_place_details(place_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Busca detalhes de um estabelecimento pelo place_id usando Google Places Details API.
    Retorna telefone, website, endereço formatado, horário de funcionamento, etc.
    """
    if not api_key or not place_id:
        return None
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    # Solicitar apenas os campos que precisamos para economizar na cota da API
    fields = ",".join([
        "formatted_phone_number",
        "international_phone_number",
        "website",
        "formatted_address",
        "opening_hours",
        "business_status",
        "url",  # Google Maps URL
        "rating",
        "user_ratings_total",
        "geometry",
        "types",
    ])
    
    params = {
        "place_id": place_id,
        "key": api_key,
        "language": "pt-BR",
        "fields": fields,
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Erro ao buscar detalhes do place_id {place_id}: {response.text}")
                return None
            
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"Google Places Details status: {data.get('status')} para {place_id}")
                return None
            
            result = data.get("result", {})
            
            # Extrair horários como string legível
            opening_hours_text = None
            opening_hours = result.get("opening_hours")
            if opening_hours:
                weekday_text = opening_hours.get("weekday_text", [])
                if weekday_text:
                    opening_hours_text = " | ".join(weekday_text)
            
            # Extrair coordenadas
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            return {
                "phone": result.get("formatted_phone_number"),
                "international_phone": result.get("international_phone_number"),
                "website": result.get("website"),
                "address": result.get("formatted_address"),
                "business_status": result.get("business_status"),
                "google_maps_url": result.get("url"),
                "opening_hours": opening_hours_text,
                "rating": result.get("rating"),
                "review_count": result.get("user_ratings_total"),
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            }
        except Exception as e:
            print(f"Exceção ao buscar detalhes do place_id {place_id}: {e}")
            return None