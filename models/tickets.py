"""Ticket persistido (canal privado por usuario)."""
from datetime import datetime
from sqlmodel import Field, SQLModel


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: int | None = Field(default=None, primary_key=True)
    guild_id: int = Field(index=True)
    user_id: int = Field(index=True)
    channel_id: int = Field(index=True)
    status: str = Field(default="open", index=True)
    subject: str = Field(default="Suporte")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = Field(default=None)
