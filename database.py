import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set.\n"
        "For local dev, add this to smart-finder-fastapi/.env:\n"
        "  DATABASE_URL=sqlite+aiosqlite:///../smart-finder-backend/db.sqlite3\n"
        "For Render, it is injected automatically from the PostgreSQL service."
    )

# ── Driver normalisation ───────────────────────────────────────────────────────
# Render gives postgres:// → convert to postgresql+asyncpg://
# Local SQLite URL stays as sqlite+aiosqlite:// — no change needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ── Engine config ─────────────────────────────────────────────────────────────
# SQLite does not support connection pooling — different config from PostgreSQL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},  # Required for SQLite
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
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
