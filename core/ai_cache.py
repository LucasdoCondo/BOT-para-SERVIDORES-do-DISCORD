"""Helper cache IA: get/set com TTL (Postgres)."""
import logging
from datetime import datetime
from core.db import get_session
from models import AICache, default_expiry

log = logging.getLogger("bot.cache_helper")


async def cache_get(key: str) -> str | None:
    try:
        async with get_session() as s:
            row = await s.get(AICache, key)
            if not row:
                return None
            if row.expires_at and row.expires_at < datetime.utcnow():
                await s.delete(row)
                await s.commit()
                return None
            row.hits += 1
            s.add(row)
            await s.commit()
            return row.answer
    except Exception:
        log.exception("cache_get falhou")
        return None


async def cache_set(key: str, prompt: str, answer: str, ttl_h: int = 24) -> None:
    try:
        async with get_session() as s:
            row = await s.get(AICache, key)
            if row:
                row.answer = answer
                row.hits += 1
                row.expires_at = default_expiry(ttl_h)
            else:
                row = AICache(key=key, prompt=prompt[:500], answer=answer, expires_at=default_expiry(ttl_h))
            s.add(row)
            await s.commit()
    except Exception:
        log.exception("cache_set falhou")
