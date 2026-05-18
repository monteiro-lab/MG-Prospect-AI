from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MG Prospect AI"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 dia
    DATABASE_URL: str
    
    # Adicionamos a variável aqui para o Pydantic reconhecer:
    GOOGLE_PLACES_API_KEY: Optional[str] = None
    N8N_WEBHOOK_LEAD_INTEREST_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore" # Diz ao Pydantic para ignorar se houver algo a mais no .env

settings = Settings()