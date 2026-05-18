from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from passlib.context import CryptContext

from app.core.database import engine, Base, get_db
from app.auth.router import router as auth_router
from app.leads.router import router as leads_router
from app.campaigns.router import router as campaigns_router
from app.emails.router import router as emails_router
from app.public.router import router as public_router
from app.auth.models import User
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Contexto para criar o hash da senha na hora
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Em produção, as tabelas são gerenciadas via Alembic migrations.
    # Base.metadata.create_all foi removido para garantir a segurança dos dados.
    yield

app = FastAPI(
    title="MG Prospect AI",
    description="Plataforma de Prospecção B2B para Mendonça Galvão Contadores",
    version="1.0.0",
    lifespan=lifespan
)

import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS para o React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL], # Estrito para a URL do frontend em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas (Sem duplicações)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(leads_router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(campaigns_router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(emails_router, prefix="/api/v1/emails", tags=["Emails"])
app.include_router(public_router, prefix="/api/v1/public", tags=["Public"])

@app.get("/")
def root():
    return {"message": "MG Prospect AI API está rodando!"}