"""Boas-vindas + autorole + log join/leave."""
import logging
import discord
from discord.ext import commands
from config.settings import settings

log = logging.getLogger("bot.welcome")

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        g = member.guild
        if settings.AUTOROLE_IDS:
            for rid in settings.AUTOROLE_IDS:
                role = g.get_role(int(rid)) if rid.isdigit() else None
                if role:
                    try:
                        await member.add_roles(role, reason="Autorole")
                    except Exception:
                        log.warning(f"Autorole falhou {role}")
        if settings.WELCOME_CHANNEL_ID:
            ch = g.get_channel(settings.WELCOME_CHANNEL_ID)
            if ch:
                try:
                    txt = settings.WELCOME_MESSAGE.format(member=member.mention, guild=g.name, user=member.display_name)
                    em = discord.Embed(title=f"Bem-vindo(a) {member.display_name}!", description=txt, color=discord.Color.green())
                    if member.avatar:
                        em.set_thumbnail(url=member.avatar.url)
                    await ch.send(embed=em)
                except Exception:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
