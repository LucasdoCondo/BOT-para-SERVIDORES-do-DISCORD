"""Status/ops: uptime, latencia, banco, disco (p/ VPS free)."""
import time
import discord
from discord.ext import commands
from sqlalchemy import text
from core.db import get_session
from utils.embeds import info_embed

_started = time.monotonic()

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="status", description="Saude do bot.")
    async def status(self, ctx: commands.Context):
        up = int(time.monotonic() - _started)
        h, r = divmod(up, 3600)
        m, s = divmod(r, 60)
        ms = round(self.bot.latency * 1000)
        try:
            async with get_session() as sess:
                await sess.exec(text("SELECT 1"))
            db = "OK"
        except Exception as e:
            db = f"FALHA: {e}"[:120]
        g = len(self.bot.guilds)
        u = sum(x.member_count or 0 for x in self.bot.guilds)
        em = info_embed("Status", f"Uptime `{h}h {m}m {s}s` | Ping `{ms}ms`\nBanco `{db}`\n{g} servidor(es) | ~{u} usuarios")
        await ctx.send(embed=em)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
