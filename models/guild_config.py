"""Config por servidor (persona IA, etc)."""
from datetime import datetime
from sqlmodel import Field, SQLModel


class GuildConfig(SQLModel, table=True):
    __tablename__ = "guild_configs"

    guild_id: int = Field(primary_key=True)
    persona: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
