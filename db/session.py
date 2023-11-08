from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config import settings
from models.base_model import Base

engine = create_async_engine(
    settings.db.url,
    echo=settings.db.echo
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False,
                                         autoflush=False, )


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
