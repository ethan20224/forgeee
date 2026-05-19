from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.database.models import Base

TEST_DATABASE_URL = "postgresql+asyncpg://speleg@localhost:5432/forge_test"


@pytest.fixture(scope="session")
async def engine_test():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine_test) -> AsyncGenerator[AsyncSession]:
    """Per-test session wrapped in a transaction that always rolls back."""
    conn = await engine_test.connect()
    txn = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    yield session

    await session.close()
    await txn.rollback()
    await conn.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Test client with DB override and rate limiter disabled."""
    from src.common.rate_limit import limiter
    from src.database.connection import get_db
    from src.main import app

    async def _override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    limiter.enabled = False

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    limiter.enabled = True
