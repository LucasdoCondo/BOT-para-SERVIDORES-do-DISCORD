"""Engine async SQLModel + init_db (create_all p/ MVP)."""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import settings

log = logging.getLogger("bot.db")

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(retries: int = 10, delay: float = 3.0) -> None:
    import models  # noqa: F401
    last = None
    for i in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            log.info("Banco pronto (SQLModel create_all OK)")
            return
        except Exception as e:
            last = e
            log.warning(f"Banco tentativa {i}/{retries} falhou: {e}")
            await asyncio.sleep(delay)
    raise last


def get_session() -> AsyncSession:
    return AsyncSessionLocal()
