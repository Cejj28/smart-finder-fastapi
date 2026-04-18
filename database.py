import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Django sets DATABASE_URL as a postgres:// URL; SQLAlchemy needs postgresql+asyncpg://
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Render provides postgres:// — convert to postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


engine = create_async_engine(
    DATABASE_URL,
    echo=False,       # Set True during local debugging to see SQL
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Automatically reconnect on stale connections
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency — yields an async DB session and ensures it closes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
