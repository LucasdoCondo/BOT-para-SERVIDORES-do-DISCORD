"""Checks reutilizaveis (evita duplicar _is_mod em cada cog)."""
from discord.ext import commands
from config.settings import settings


def is_mod():
    async def pred(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False
        p = ctx.author.guild_permissions
        if p.administrator or p.moderate_members:
            return True
        if settings.MOD_ROLE_IDS:
            ids = {str(r.id) for r in ctx.author.roles}
            if ids & set(settings.MOD_ROLE_IDS):
                return True
        return False
    return commands.check(pred)
