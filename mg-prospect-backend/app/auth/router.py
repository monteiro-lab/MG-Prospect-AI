from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

# Tenta importar o JWT (suporta tanto PyJWT quanto python-jose)
try:
    from jose import jwt, JWTError
except ImportError:
    import jwt
    from jwt import PyJWTError as JWTError

from app.core.database import get_db
from app.auth.models import User

router = APIRouter()

# Configurações de Segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_super_segura_aqui_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 horas

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 1. Busca o usuário no banco pelo e-mail
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    # 2. Verifica se o usuário existe e se a senha bate com o hash
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Gera o Token de Acesso (JWT)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer"}

# Função que protege as outras rotas (A "trava" da porta)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

import secrets
from app.auth.models import PasswordResetToken
from app.auth.schemas import ForgotPasswordRequest, ResetPasswordRequest
from app.integrations.email_provider import send_prospect_email

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()
    
    if not user:
        # Prevent email enumeration by returning a generic message
        return {"msg": "Se o e-mail existir, um link de recuperação será enviado."}
        
    # Generate token
    token = secrets.token_urlsafe(32)
    
    # Store token in DB
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=pwd_context.hash(token),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset_token)
    await db.commit()
    
    # In production, use frontend URL from settings
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={token}&email={user.email}"
    
    # Send email
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Recuperação de Senha</h2>
        <p>Olá {user.full_name},</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta no MG Prospect AI.</p>
        <p>Clique no botão abaixo para criar uma nova senha:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #D4AF37; color: #111111; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Redefinir Senha</a>
        </div>
        <p style="font-size: 12px; color: #666;">Se você não solicitou esta alteração, ignore este e-mail. Este link expirará em 1 hora.</p>
    </div>
    """
    
    await send_prospect_email(
        to_email=user.email,
        subject="MG Prospect AI - Recuperação de Senha",
        html_content=html_content
    )
    
    return {"msg": "Se o e-mail existir, um link de recuperação será enviado."}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="E-mail inválido ou token expirado.")
        
    # Get unexpired tokens for this user
    now = datetime.utcnow()
    tokens_result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id)
        .where(PasswordResetToken.used_at.is_(None))
        .where(PasswordResetToken.expires_at > now)
    )
    tokens = tokens_result.scalars().all()
    
    valid_token = None
    for t in tokens:
        if pwd_context.verify(req.token, t.token_hash):
            valid_token = t
            break
            
    if not valid_token:
        raise HTTPException(status_code=400, detail="Token inválido ou já expirado.")
        
    # Valid token found. Reset password.
    user.hashed_password = pwd_context.hash(req.new_password)
    valid_token.used_at = now
    
    await db.commit()
    return {"msg": "Senha redefinida com sucesso."}