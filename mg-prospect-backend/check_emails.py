import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        r = await db.execute(text("SELECT name, email FROM leads WHERE email IS NOT NULL LIMIT 5"))
        rows = r.fetchall()
        for row in rows:
            print(f"{row[0]}: {row[1]}")
        if not rows:
            print("Nenhum lead com email no banco")
        
        r2 = await db.execute(text("SELECT COUNT(*) FROM leads"))
        total = r2.scalar()
        print(f"Total de leads: {total}")

asyncio.run(check())
