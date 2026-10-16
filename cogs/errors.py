"""Tratamento global de erros + cooldown amigavel."""
import logging
import discord
from discord.ext import commands
from utils.embeds import error_embed

log = logging.getLogger("bot.errors")

class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Calma! Tente em {error.retry_after:.1f}s.", delete_after=5)
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=error_embed("Faltou argumento", f"Uso: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`"))
        if isinstance(error, commands.BadArgument):
            return await ctx.send(embed=error_embed("Argumento invalido", "Verifique mencoes, numeros e tente de novo."))
        if isinstance(error, commands.CheckFailure):
            return await ctx.send(embed=error_embed("Sem permissao", "Voce nao tem permissao para esse comando."))
        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            return await ctx.send(embed=error_embed("Bot sem permissao", f"Faltam: `{perms}`"))
        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(embed=error_embed("Erro", "Use esse comando num servidor."))
        log.exception(f"Erro no comando {ctx.command}: {error}")
        try:
            await ctx.send(embed=error_embed("Erro inesperado", "Ocorreu um erro. O log foi registrado."))
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        log.exception(f"Erro slash: {error}")
        msg = "Ocorreu um erro no slash command."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Errors(bot))
