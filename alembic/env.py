"""Alembic env: usa DATABASE_URL sync via psycopg ou async via asyncpg."""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

import models  # noqa: F401 - registra tabelas
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata


def _sync_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    # Alembic sync: troca asyncpg -> psycopg
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    return url or "postgresql+psycopg://bot:bot_secret@localhost:5432/botdb"


def run_migrations_offline() -> None:
    context.configure(url=_sync_url(), target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    engine = create_engine(_sync_url(), poolclass=pool.NullPool)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
