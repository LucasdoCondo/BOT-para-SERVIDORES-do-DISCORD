from datetime import datetime
from sqlmodel import Field, SQLModel


class UserLevel(SQLModel, table=True):
    __tablename__ = "user_levels"

    id: int | None = Field(default=None, primary_key=True)
    guild_id: int = Field(index=True)
    user_id: int = Field(index=True)
    xp: int = Field(default=0)
    level: int = Field(default=1)
    message_count: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Warn(SQLModel, table=True):
    __tablename__ = "warns"

    id: int | None = Field(default=None, primary_key=True)
    guild_id: int = Field(index=True)
    user_id: int = Field(index=True)
    mod_id: int = Field(default=0)
    reason: str = Field(default="Sem motivo")
    created_at: datetime = Field(default_factory=datetime.utcnow)
