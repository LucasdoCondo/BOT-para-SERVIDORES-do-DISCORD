"""Config central via variáveis de ambiente (.env)."""
import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")


@dataclass(frozen=True)
class Settings:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MOD_ROLE_IDS: tuple = tuple(
        x.strip() for x in os.getenv("MOD_ROLE_IDS", "").split(",") if x.strip()
    )
    MODLOG_CHANNEL_ID: int = int(os.getenv("MODLOG_CHANNEL_ID", "0") or 0)
    BANNED_WORDS: tuple = tuple(
        x.strip().lower() for x in os.getenv("BANNED_WORDS", "spam,http://,https://").split(",") if x.strip()
    )
    # Banco Postgres (docker-compose). Formato asyncpg:
    # postgresql+asyncpg://bot:bot_secret@db:5432/botdb
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://bot:bot_secret@localhost:5432/botdb",
    )
    # Levels
    XP_PER_MESSAGE_MIN: int = int(os.getenv("XP_PER_MESSAGE_MIN", "5") or 5)
    XP_PER_MESSAGE_MAX: int = int(os.getenv("XP_PER_MESSAGE_MAX", "15") or 15)
    XP_COOLDOWN_SECONDS: int = int(os.getenv("XP_COOLDOWN_SECONDS", "60") or 60)
    # Warns (moderação pro)
    WARN_MAX: int = int(os.getenv("WARN_MAX", "3") or 3)
    WARN_AUTOMUTE_MINUTES: int = int(os.getenv("WARN_AUTOMUTE_MINUTES", "60") or 60)
    # Boas-vindas
    WELCOME_CHANNEL_ID: int = int(os.getenv("WELCOME_CHANNEL_ID", "0") or 0)
    WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE", "Bem-vindo(a) {member} ao {guild}!")
    AUTOROLE_IDS: tuple = tuple(
        x.strip() for x in os.getenv("AUTOROLE_IDS", "").split(",") if x.strip()
    )
    # Automod
    AUTOMOD_MAX_MSG: int = int(os.getenv("AUTOMOD_MAX_MSG", "5") or 5)
    AUTOMOD_WINDOW: int = int(os.getenv("AUTOMOD_WINDOW_SECONDS", "10") or 10)
    AUTOMOD_MUTE_MIN: int = int(os.getenv("AUTOMOD_MUTE_MINUTES", "10") or 10)
    AUTOMOD_WHITELIST: tuple = tuple(
        x.strip() for x in os.getenv("AUTOMOD_WHITELIST_CHANNELS", "").split(",") if x.strip()
    )
    # Tickets
    TICKET_CATEGORY_ID: int = int(os.getenv("TICKET_CATEGORY_ID", "0") or 0)
    TICKET_STAFF_ROLES: tuple = tuple(
        x.strip() for x in os.getenv("TICKET_STAFF_ROLE_IDS", "").split(",") if x.strip()
    )
    TICKET_LOG_CHANNEL_ID: int = int(os.getenv("TICKET_LOG_CHANNEL_ID", "0") or 0)
    TICKET_MAX_OPEN: int = int(os.getenv("TICKET_MAX_OPEN_PER_USER", "3") or 3)
    # IA persona + resumo
    AI_PERSONA: str = os.getenv("AI_PERSONA", "")
    AI_SUMMARY_MAX: int = int(os.getenv("AI_SUMMARY_MAX_CHARS", "1500") or 1500)
    # Cache IA (economia quota Gemini)
    AI_CACHE_ENABLED: bool = _get_bool("AI_CACHE_ENABLED", True)
    AI_CACHE_TTL_HOURS: int = int(os.getenv("AI_CACHE_TTL_HOURS", "24") or 24)
    # Dashboard web (opcional, porta interna)
    DASHBOARD_ENABLED: bool = _get_bool("DASHBOARD_ENABLED", False)
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8000") or 8000)


settings = Settings()

