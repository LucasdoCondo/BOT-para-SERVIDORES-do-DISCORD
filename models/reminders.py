"""Lembrete persistido (sobrevive a reboot)."""
from datetime import datetime
from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: int | None = Field(default=None, primary_key=True)
    guild_id: int = Field(index=True)
    channel_id: int = Field(index=True)
    user_id: int = Field(index=True)
    text: str = Field(default="")
    remind_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
