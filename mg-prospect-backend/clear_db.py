"""Script para zerar leads, campanhas e logs do banco de dados."""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def clear_all():
    async with AsyncSessionLocal() as db:
        # Ordem importa por causa das foreign keys
        await db.execute(text("DELETE FROM campaign_logs"))
        await db.execute(text("DELETE FROM lead_interests"))
        await db.execute(text("DELETE FROM leads"))
        await db.execute(text("DELETE FROM campaigns"))
        await db.commit()
        print("Todas as tabelas foram limpas com sucesso.")
        
        # Verificar contagens
        for table in ["leads", "campaigns", "campaign_logs", "lead_interests"]:
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table}: {count} registros")

if __name__ == "__main__":
    asyncio.run(clear_all())
