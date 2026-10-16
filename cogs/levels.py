"""Levels: XP por msg + rank/leaderboard (Postgres + SQLModel)."""
import logging
import random
import time
import discord
from discord.ext import commands
from sqlmodel import select
from config.settings import settings
from core.db import get_session
from models import UserLevel
from utils.embeds import info_embed

log = logging.getLogger("bot.levels")
class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if len(message.content) < 3:
            return
        key = (message.guild.id, message.author.id)
        now = time.monotonic()
        if now - _cooldowns.get(key, 0) < settings.XP_COOLDOWN_SECONDS:
            return
        _cooldowns[key] = now
        gain = random.randint(settings.XP_PER_MESSAGE_MIN, settings.XP_PER_MESSAGE_MAX)
        try:
            async with get_session() as s:
                q = await s.exec(select(UserLevel).where(UserLevel.guild_id == message.guild.id, UserLevel.user_id == message.author.id))
                row = q.first()
                if not row:
                    row = UserLevel(guild_id=message.guild.id, user_id=message.author.id)
                    s.add(row)
                row.xp += gain
                row.message_count += 1
                need = xp_for_next(row.level)
                leveled = False
                while row.xp >= need:
                    row.xp -= need
                    row.level += 1
                    need = xp_for_next(row.level)
                    leveled = True
                await s.commit()
                await s.refresh(row)
                if leveled:
                    try:
                        await message.channel.send(f"GG {message.author.mention} subiu para **nivel {row.level}**!")
                    except Exception:
                        pass
        except Exception:
            log.exception("Erro ao dar XP")

    @commands.hybrid_command(name="rank", description="Mostra seu nivel/XP.")
    async def rank(self, ctx: commands.Context, member: discord.Member | None = None):
        m = member or ctx.author
        async with get_session() as s:
            q = await s.exec(select(UserLevel).where(UserLevel.guild_id == ctx.guild.id, UserLevel.user_id == m.id))
            row = q.first()
        if not row:
            return await ctx.send(f"{m.display_name} ainda nao tem XP. Fale mais!")
        need = xp_for_next(row.level)
        bar_len = 12
        filled = int(bar_len * row.xp / need) if need else 0
        bar = "#" * filled + "-" * (bar_len - filled)
        em = info_embed(f"Rank de {m.display_name}", f"Nivel **{row.level}** | **{row.xp}/{need} XP**\n`[{bar}]`\n{row.message_count} msgs")
        if m.avatar:
            em.set_thumbnail(url=m.avatar.url)
        await ctx.send(embed=em)

    @commands.hybrid_command(name="leaderboard", description="Top 10 por XP.")
    async def leaderboard(self, ctx: commands.Context):
        async with get_session() as s:
            q = await s.exec(select(UserLevel).where(UserLevel.guild_id == ctx.guild.id).order_by(UserLevel.level.desc(), UserLevel.xp.desc()).limit(10))
            rows = q.all()
        if not rows:
            return await ctx.send("Ninguem tem XP ainda.")
        lines = []
        for i, r in enumerate(rows, 1):
            user = ctx.guild.get_member(r.user_id)
            name = user.display_name if user else f"ID {r.user_id}"
            lines.append(f"**{i}.** {name} — nv {r.level} ({r.xp} xp)")
        await ctx.send(embed=info_embed(f"Leaderboard {ctx.guild.name}", "\n".join(lines)))


async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))

_cooldowns: dict[tuple[int, int], float] = {}

def xp_for_next(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100
