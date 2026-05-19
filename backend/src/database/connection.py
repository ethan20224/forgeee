from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Async SQLAlchemy engine and session factory for PostgreSQL.

Flow:
1. Engine created from DATABASE_URL on module import
2. get_db() yields an AsyncSession per request via FastAPI Depends()
3. Auto-commits on success, rolls back on exception

Main Entry Point: get_db()

Dependencies:
- sqlalchemy[asyncio]: async ORM engine
- asyncpg: PostgreSQL async driver
- src.config: DATABASE_URL setting
"""
