import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def migrate():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        try:
            print("Attempting to add 'plan' column to users table...")
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS plan VARCHAR(50) DEFAULT 'free'"))
            print("✅ Successfully added 'plan' column!")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
