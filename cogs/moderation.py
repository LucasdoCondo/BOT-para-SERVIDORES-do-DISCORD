"""Moderacao: kick, ban, unban, mute(timeout), unmute, clear + filtro."""
import logging
from datetime import timedelta
import discord
from discord.ext import commands
from config.settings import settings
from core.checks import is_mod
from utils.embeds import success_embed, error_embed

log = logging.getLogger("bot.moderation")

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


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="kick")
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, motivo: str = "Sem motivo"):
        if member == ctx.author or member == ctx.guild.owner:
            return await ctx.send(embed=error_embed("Kick", "Nao pode expulsar esse membro."))
        if ctx.author.top_role <= member.top_role and not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=error_embed("Kick", "Voce nao tem cargo maior que o alvo."))
        try:
            await member.kick(reason=f"{ctx.author}: {motivo}")
            await ctx.send(embed=success_embed("Kick", f"{member.mention} expulso. Motivo: {motivo}"))
            await _send_modlog(ctx.guild, f"KICK {member} por {ctx.author}: {motivo}")
        except discord.Forbidden:
            await ctx.send(embed=error_embed("Kick", "Sem permissao. Verifique cargos do bot."))

    @commands.command(name="ban")
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, motivo: str = "Sem motivo"):
        if member == ctx.author or member == ctx.guild.owner:
            return await ctx.send(embed=error_embed("Ban", "Nao pode banir esse membro."))
        try:
            await member.ban(reason=f"{ctx.author}: {motivo}", delete_message_days=1)
            await ctx.send(embed=success_embed("Ban", f"{member.mention} banido. Motivo: {motivo}"))
            await _send_modlog(ctx.guild, f"BAN {member} por {ctx.author}: {motivo}")
        except discord.Forbidden:
            await ctx.send(embed=error_embed("Ban", "Sem permissao."))

    @commands.command(name="unban")
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(embed=success_embed("Unban", f"{user} desbanido."))
        except discord.NotFound:
            await ctx.send(embed=error_embed("Unban", "Usuario nao esta banido."))
        except Exception as e:
            await ctx.send(embed=error_embed("Unban", f"Erro: {e}"))

    @commands.command(name="mute")
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutos: int = 10, *, motivo: str = "Sem motivo"):
        if minutos < 1 or minutos > 40320:
            return await ctx.send(embed=error_embed("Mute", "Use 1 a 40320 minutos."))
        try:
            await member.timeout(timedelta(minutes=minutos), reason=f"{ctx.author}: {motivo}")
            await ctx.send(embed=success_embed("Mute", f"{member.mention} silenciado por {minutos}min. Motivo: {motivo}"))
            await _send_modlog(ctx.guild, f"MUTE {member} {minutos}min por {ctx.author}: {motivo}")
        except discord.Forbidden:
            await ctx.send(embed=error_embed("Mute", "Sem permissao de timeout."))

    @commands.command(name="unmute")
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
            await member.timeout(None, reason=f"Unmute por {ctx.author}")
            await ctx.send(embed=success_embed("Unmute", f"{member.mention} liberado."))
        except Exception as e:
            await ctx.send(embed=error_embed("Unmute", f"Erro: {e}"))

    @commands.command(name="clear", aliases=["purge"])
    @_is_mod()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, qtd: int = 10):
        if qtd < 1 or qtd > 100:
            return await ctx.send(embed=error_embed("Clear", "Use 1 a 100."))
        try:
            deleted = await ctx.channel.purge(limit=qtd + 1)
            msg = await ctx.send(embed=success_embed("Clear", f"{len(deleted)-1} msgs apagadas."))
            await msg.delete(delay=5)
        except Exception as e:
            await ctx.send(embed=error_embed("Clear", f"Erro: {e}"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return
        content = message.content.lower()
        for word in settings.BANNED_WORDS:
            if word and word in content:
                try:
                    await message.delete()
                    warn = await message.channel.send(f"{message.author.mention} mensagem bloqueada (filtro).", delete_after=5)
                    log.info(f"Filtro bloqueou msg de {message.author} em {message.guild}: {word}")
                    await _send_modlog(message.guild, f"FILTRO bloqueou msg de {message.author}: `{word}`")
                    break
                except Exception:
                    break


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
