"""Reminders persistentes (Postgres + loop)."""
import logging
import re
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands, tasks
from sqlmodel import select
from core.db import get_session
from models import Reminder
from utils.embeds import success_embed, error_embed, info_embed

log = logging.getLogger("bot.reminders")

def parse_dur(s: str) -> int | None:
    m = re.fullmatch(r"(\d+)(s|m|h|d)", s.strip().lower())
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2)
    if u == "s":
        return n
    if u == "m":
        return n * 60
    if u == "h":
        return n * 3600
    return n * 86400

class Reminders(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @tasks.loop(seconds=30)
    async def checker(self):
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            async with get_session() as s:
                q = await s.exec(select(Reminder).where(Reminder.remind_at <= now).limit(10))
                rows = q.all()
                for r in rows:
                    try:
                        ch = self.bot.get_channel(r.channel_id)
                        if ch:
                            await ch.send(f"<@{r.user_id}> lembrete: **{r.text}**")
                        await s.delete(r)
                    except Exception:
                        log.exception("Erro reminder")
                if rows:
                    await s.commit()
        except Exception:
            log.exception("Loop reminders")

    @checker.before_loop
    async def before_checker(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_command(name="remind", description="Lembra em Xs/m/h/d.")
    async def remind(self, ctx: commands.Context, quando: str, *, texto: str):
        secs = parse_dur(quando)
        if not secs or secs < 10 or secs > 30 * 86400:
            return await ctx.send(embed=error_embed("Remind", "Use `10s`, `5m`, `2h`, `1d` (10s a 30d)."))
        when = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=secs)
        async with get_session() as s:
            s.add(Reminder(guild_id=ctx.guild.id if ctx.guild else 0, channel_id=ctx.channel.id, user_id=ctx.author.id, text=texto, remind_at=when))
            await s.commit()
        await ctx.send(embed=success_embed("Remind", f"Ok! Lembro em `{quando}`: {texto}"))

    @commands.hybrid_command(name="reminders", description="Lista seus lembretes.")
    async def listrem(self, ctx: commands.Context):
        async with get_session() as s:
            q = await s.exec(select(Reminder).where(Reminder.user_id == ctx.author.id).order_by(Reminder.remind_at).limit(10))
            rows = q.all()
        if not rows:
            return await ctx.send("Sem lembretes.")
        lines = [f"`#{r.id}` <t:{int(r.remind_at.replace(tzinfo=timezone.utc).timestamp())}:R>: {r.text}" for r in rows]
        await ctx.send(embed=info_embed("Lembretes", "\n".join(lines)))

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
