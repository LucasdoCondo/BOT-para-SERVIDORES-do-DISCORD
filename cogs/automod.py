"""Automod: anti-flood + anti-invite (leve, p/ VPS free)."""
import logging
import time
from collections import deque
from datetime import timedelta
import discord
from discord.ext import commands
from config.settings import settings

log = logging.getLogger("bot.automod")
_hist: dict[tuple[int, int], deque] = {}

class Automod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return
        if str(message.channel.id) in settings.AUTOMOD_WHITELIST:
            return
        low = message.content.lower()
        if ("discord.gg/" in low or "discord.com/invite/" in low):
            try:
                await message.delete()
                await message.channel.send(f"{message.author.mention} convites nao sao permitidos.", delete_after=5)
                return
            except Exception:
                return
        key = (message.guild.id, message.author.id)
        dq = _hist.setdefault(key, deque())
        now = time.monotonic()
        dq.append(now)
        while dq and now - dq[0] > settings.AUTOMOD_WINDOW:
            dq.popleft()
        if len(dq) >= settings.AUTOMOD_MAX_MSG:
            dq.clear()
            try:
                await message.channel.purge(limit=10, check=lambda m: m.author.id == message.author.id)
            except Exception:
                pass
            try:
                await message.author.timeout(timedelta(minutes=settings.AUTOMOD_MUTE_MIN), reason="Automod flood")
                await message.channel.send(f"{message.author.mention} mutado {settings.AUTOMOD_MUTE_MIN}min (flood).", delete_after=10)
                log.info(f"Automod mutou {message.author} flood")
            except Exception:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Automod(bot))
