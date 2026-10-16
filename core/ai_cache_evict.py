"""Eviction automático de linhas expiradas (suave, semi-asincrono)."""
import logging
from datetime import datetime, timedelta
import asyncio
from core.db import AsyncSessionLocal, engine
from models import AICache

log = logging.getLogger("bot.cache_evict")


async def evict_once(retries: int = 3) -> int:
    removed = 0
    for _ in range(retries):
        try:
            async with AsyncSessionLocal() as s:
                now = datetime.utcnow()
                stmt = AICache.__table__.delete().where(AICache.expires_at <= now)
                await s.execute(stmt)
                removed = await s.execute(stmt)
                await s.commit()
            break
        except Exception:
            log.exception("evict falhou")
            await asyncio.sleep(1)
    return removed


async def evict_loop(hour: int = 6):
    while True:
        await asyncio.sleep(hour * 3600)
        n = await evict_once()
        if n:
            log.info(f"cache eviction: {n} rows expiradas removidas")
