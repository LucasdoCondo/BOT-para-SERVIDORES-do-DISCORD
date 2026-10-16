"""Cache IA em Postgres (economia de quota Gemini)."""
import hashlib
import logging
from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel

log = logging.getLogger("bot.cache")


class AICache(SQLModel, table=True):
    __tablename__ = "ai_cache"

    key: str = Field(primary_key=True, max_length=64)
    prompt: str = Field(default="")
    answer: str = Field(default="")
    hits: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=datetime.utcnow)


def cache_key(model: str, persona: str, prompt: str) -> str:
    raw = f"{model}|{persona[:200]}|{prompt.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:64]


def default_expiry(hours: int = 24) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)
