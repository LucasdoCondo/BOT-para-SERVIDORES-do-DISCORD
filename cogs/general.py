"""Cog geral: ping, help, info."""
import discord
from discord import app_commands
from discord.ext import commands

from config.settings import settings
from utils.embeds import info_embed


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Mostra a latência do bot.")
    async def ping(self, ctx: commands.Context):
        ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! `{ms}ms`")

    @commands.hybrid_command(name="help", description="Mostra todos os comandos.")
    async def help_cmd(self, ctx: commands.Context):
        embed = discord.Embed(title="📚 Ajuda do Bot", color=discord.Color.blurple())
        embed.add_field(
            name="🤖 IA (Gemini - Grátis)",
            value="`/ask <pergunta>` ou `!ask <pergunta>`\n`/chat <msg>` - conversa contínua (por usuário)\n`/resumir [qtd]` - resume o canal\n`/persona` - ver persona do servidor",
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderação",
            value="`!kick` `!ban` `!unban` `!mute` `!unmute` `!clear`\n`!warn` `!warns` `!clearwarns` (automute) + antiflood auto",
            inline=False,
        )
        embed.add_field(
            name="🏆 Levels",
            value="`/rank` | `/leaderboard` — ganhe XP falando no chat",
            inline=False,
        )
        embed.add_field(
            name="📌 Geral",
            value="`/ping` | `/info` | `/status` | `/help`\n`/ticket` | `/remind 10m texto`",
            inline=False,
        )
        embed.set_footer(text=f"Prefixo: {settings.COMMAND_PREFIX} | Slash commands também funcionam!")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="info", description="Info do bot e do servidor.")
    async def info(self, ctx: commands.Context):
        g = ctx.guild
        embed = info_embed("Info", f"Olá! Eu sou **{self.bot.user.name}** 🤖\nGemini + Moderação | discord.py")
        if g:
            embed.add_field(name="Servidor", value=f"{g.name} (`{g.id}`)", inline=True)
            embed.add_field(name="Membros", value=str(g.member_count), inline=True)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
