from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

if not settings.database_url:
    msg = (
        "DATABASE_URL is missing. Copy `.env.example` to `.env` at the repository root "
        "and configure the PostgreSQL connection."
    )
    raise RuntimeError(msg)

# Engine is created at import time; database routes import this module.
engine = create_async_engine(settings.database_url, echo=settings.debug)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
