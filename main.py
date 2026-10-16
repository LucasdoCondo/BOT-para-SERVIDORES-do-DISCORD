import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.ai_cache_evict import evict_loop

from config.settings import settings
from core.dashboard import start
from core.db import init_db
from core.logger import setup_logging

# Carrega .env antes de tudo
load_dotenv()

setup_logging(level=settings.LOG_LEVEL)
log = logging.getLogger("bot.main")


def get_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True  # Necessário p/ prefix commands + filtro. Ative no Portal Dev.
    intents.members = True          # Necessário p/ kick/ban/timeout. Ative SERVER MEMBERS INTENT.
    intents.guilds = True
    intents.messages = True
    intents.moderation = True
    return intents


async def main() -> None:
    if not settings.DISCORD_TOKEN:
        log.critical("DISCORD_TOKEN não definido! Copie .env.example para .env e preencha.")
        sys.exit(1)

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(settings.COMMAND_PREFIX),
        intents=get_intents(),
        help_command=None,  # usamos cog General com help custom
        case_insensitive=True,
    )

    # Lista de Cogs (modular - adicione novos aqui)
    initial_cogs = [
        "cogs.general",
        "cogs.ai",
        "cogs.moderation",
        "cogs.levels",
        "cogs.warns",
        "cogs.welcome",
        "cogs.automod",
        "cogs.tickets",
        "cogs.reminders",
        "cogs.persona",
        "cogs.status",
        "cogs.errors",
        "cogs.music",         # Novo: Player Lo-Fi
        "cogs.admin_tasks",   # Novo: Tarefas Administrativas
    ]

    @bot.event
    async def on_ready():
        log.info(f"✅ Logado como {bot.user} (ID: {bot.user.id}) | {len(bot.guilds)} servidor(es)")
        log.info(f"Prefixo: {settings.COMMAND_PREFIX} | Slash commands: sincronizados globalmente")
        try:
            synced = await bot.tree.sync()
            log.info(f"🔄 {len(synced)} slash command(s) sincronizado(s).")
        except Exception as e:
            log.exception(f"Falha ao sincronizar slash commands: {e}")
        # Healthcheck Docker: marca vida a cada on_ready
        try:
            with open("/tmp/bot_alive", "w") as f:
                f.write("ok")
        except Exception:
            pass

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{settings.COMMAND_PREFIX}help | /ask com Gemini"
            )
        )

    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            log.info(f"📦 Cog carregado: {cog}")
        except Exception as e:
            log.exception(f"❌ Falha ao carregar {cog}: {e}")

    # Banco: Alembic upgrade head (versionado) com fallback create_all
    try:
        from alembic.config import Config as AlembicConfig
        from alembic import command as alembic_cmd
        cfg = AlembicConfig("alembic.ini")
        await asyncio.to_thread(alembic_cmd.upgrade, cfg, "head")
        log.info("Banco migrado (alembic head OK)")
    except Exception as e:
        log.warning(f"Alembic falhou ({e}), usando create_all fallback")
        try:
            await init_db()
        except Exception as e2:
            log.exception(f"❌ Falha ao conectar no banco: {e2}")
            log.critical("Verifique DATABASE_URL e se o Postgres está rodando.")
            sys.exit(1)

    # Dashboard interno (thread) — ativa somente se DASHBOARD_ENABLED=1
    if settings.DASHBOARD_ENABLED:
        try:
            start(host="127.0.0.1", port=settings.DASHBOARD_PORT)
            log.info("Dashboard FastAPI ativado")
        except Exception as e:
            log.warning(f"Dashboard falhou: {e}")

    try:
        await bot.start(settings.DISCORD_TOKEN)
    except discord.LoginFailure:
        log.critical("Token do Discord inválido. Verifique DISCORD_TOKEN no .env")
    except KeyboardInterrupt:
        log.info("Desligando por KeyboardInterrupt...")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
