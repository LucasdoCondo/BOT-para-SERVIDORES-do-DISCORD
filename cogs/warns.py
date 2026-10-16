"""Warns: !warn/!warns/!clearwarns + mute auto (Postgres)."""
import logging
from datetime import timedelta
import discord
from discord.ext import commands
from sqlmodel import select, func
from config.settings import settings
from core.checks import is_mod
from core.db import get_session
from models import Warn
from utils.embeds import success_embed, error_embed, info_embed

log = logging.getLogger("bot.warns")

_is_mod = is_mod

async def _send_modlog(guild, text: str):
    if not settings.MODLOG_CHANNEL_ID:
        return
    ch = guild.get_channel(settings.MODLOG_CHANNEL_ID)
    if ch:
        try:
            await ch.send(text)
        except Exception:
            pass

async def _count_warns(guild_id: int, user_id: int) -> int:
    async with get_session() as s:
        q = await s.exec(select(func.count(Warn.id)).where(Warn.guild_id == guild_id, Warn.user_id == user_id))
        return q.one()


class Warns(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _do_warn(self, guild, target_id: int, mod_id: int, reason: str) -> int:
        async with get_session() as s:
            s.add(Warn(guild_id=guild.id, user_id=target_id, mod_id=mod_id, reason=reason))
            await s.commit()
        total = await _count_warns(guild.id, target_id)
        await _send_modlog(guild, f"WARN {target_id} por {mod_id} ({total}/{settings.WARN_MAX}): {reason}")
        return total

    async def _maybe_automute(self, guild, member, total: int) -> bool:
        if total < settings.WARN_MAX:
            return False
        try:
            await member.timeout(timedelta(minutes=settings.WARN_AUTOMUTE_MINUTES), reason=f"Automute: {total} warns")
            await _send_modlog(guild, f"AUTOMUTE {member} {settings.WARN_AUTOMUTE_MINUTES}min ({total} warns)")
            return True
        except discord.Forbidden:
            log.warning("Automute sem permissao de timeout")
            return False
        except Exception:
            log.exception("Erro automute")
            return False

    @commands.hybrid_command(name="warn", description="Aplica advertencia.")
    @_is_mod()
    @commands.guild_only()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, motivo: str = "Sem motivo"):
        if member.bot:
            return await ctx.send(embed=error_embed("Warn", "Nao pode advertir bots."))
        if member == ctx.author:
            return await ctx.send(embed=error_embed("Warn", "Nao pode advertir a si mesmo."))
        if ctx.author.top_role <= member.top_role and not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=error_embed("Warn", "Cargo insuficiente."))
        total = await self._do_warn(ctx.guild, member.id, ctx.author.id, motivo)
        muted = await self._maybe_automute(ctx.guild, member, total)
        msg = f"{member.mention} advertido ({total}/{settings.WARN_MAX}). Motivo: {motivo}"
        if muted:
            msg += f"\nAutomute {settings.WARN_AUTOMUTE_MINUTES}min aplicado!"
        await ctx.send(embed=success_embed("Warn", msg))

    @commands.hybrid_command(name="warns", description="Lista warns de um membro.")
    @_is_mod()
    @commands.guild_only()
    async def warns(self, ctx: commands.Context, member: discord.Member):
        async with get_session() as s:
            q = await s.exec(select(Warn).where(Warn.guild_id == ctx.guild.id, Warn.user_id == member.id).order_by(Warn.id.desc()).limit(10))
            rows = q.all()
        if not rows:
            return await ctx.send(embed=info_embed("Warns", f"{member.display_name} nao tem warns."))
        lines = [f"`#{w.id}` <@{w.mod_id}>: {w.reason}" for w in rows]
        em = info_embed(f"Warns de {member.display_name} ({len(rows)})", "\n".join(lines))
        await ctx.send(embed=em)

    @commands.hybrid_command(name="clearwarns", description="Limpa warns de um membro.")
    @_is_mod()
    @commands.guild_only()
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        async with get_session() as s:
            q = await s.exec(select(Warn).where(Warn.guild_id == ctx.guild.id, Warn.user_id == member.id))
            rows = q.all()
            n = len(rows)
            for w in rows:
                await s.delete(w)
            await s.commit()
        await _send_modlog(ctx.guild, f"CLEARWARNS {member} por {ctx.author} ({n} removidos)")
        await ctx.send(embed=success_embed("Clearwarns", f"{n} warn(s) de {member.mention} removidos."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Warns(bot))
