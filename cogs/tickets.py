"""Tickets: painel com botao -> canal privado (Postgres)."""
import logging
import discord
from discord.ext import commands
from sqlmodel import select, func
from config.settings import settings
from core.checks import is_mod
from core.db import get_session
from models import Ticket
from utils.embeds import success_embed, error_embed, info_embed

log = logging.getLogger("bot.tickets")

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar ticket", style=discord.ButtonStyle.red, custom_id="ticket_close")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("Tickets")
        if cog:
            await cog.close_ticket(interaction)
        else:
            await interaction.response.send_message("Erro interno.", ephemeral=True)

class OpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir ticket", style=discord.ButtonStyle.green, custom_id="ticket_open", emoji="\U0001F39F")
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("Tickets")
        if cog:
            await cog.create_ticket(interaction, subject="Suporte")
        else:
            await interaction.response.send_message("Erro interno.", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _staff_roles(self, guild):
        roles = []
        for rid in settings.TICKET_STAFF_ROLES:
            if rid.isdigit():
                r = guild.get_role(int(rid))
                if r:
                    roles.append(r)
        return roles

    def _overwrites(self, guild, user):
        ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        ow[user] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        ow[guild.me] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        return ow

    async def create_ticket(self, interaction: discord.Interaction, subject: str):
        g = interaction.guild
        if not g:
            return await interaction.response.send_message("Use num servidor.", ephemeral=True)
        async with get_session() as s:
            q = await s.exec(select(func.count(Ticket.id)).where(Ticket.guild_id == g.id, Ticket.user_id == interaction.user.id, Ticket.status == "open"))
            n = q.one()
        if n >= settings.TICKET_MAX_OPEN:
            return await interaction.response.send_message(f"Voce ja tem {n} aberto(s).", ephemeral=True)
        ow = self._overwrites(g, interaction.user)
        for r in await self._staff_roles(g):
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        cat = g.get_channel(settings.TICKET_CATEGORY_ID) if settings.TICKET_CATEGORY_ID else None
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            ch = await g.create_text_channel(f"ticket-{interaction.user.display_name}", overwrites=ow, category=cat, reason=f"Ticket {interaction.user}")
        except discord.Forbidden:
            return await interaction.followup.send("Sem permissao p/ criar canais.", ephemeral=True)
        async with get_session() as s:
            s.add(Ticket(guild_id=g.id, user_id=interaction.user.id, channel_id=ch.id, subject=subject))
            await s.commit()
        em = info_embed("Ticket criado", f"{interaction.user.mention} assunto: **{subject}**")
        await ch.send(f"{interaction.user.mention}", embed=em, view=CloseView())
        await interaction.followup.send(f"Ticket: {ch.mention}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction):
        ch = interaction.channel
        if not ch or not ch.name.startswith("ticket-"):
            return await interaction.response.send_message("Nao e ticket.", ephemeral=True)
        staff = interaction.user.guild_permissions.manage_channels or any(str(r.id) in settings.TICKET_STAFF_ROLES for r in interaction.user.roles)
        async with get_session() as s:
            q = await s.exec(select(Ticket).where(Ticket.guild_id == interaction.guild.id, Ticket.channel_id == ch.id, Ticket.status == "open"))
            t = q.first()
        if not t:
            return await interaction.response.send_message("Nao registrado.", ephemeral=True)
        if interaction.user.id != t.user_id and not staff:
            return await interaction.response.send_message("So dono/staff fecha.", ephemeral=True)
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with get_session() as s:
            t2 = await s.get(Ticket, t.id)
            if t2:
                from datetime import datetime
                t2.status = "closed"
                t2.closed_at = datetime.utcnow()
                s.add(t2)
                await s.commit()
        try:
            await ch.delete(reason=f"Fechado por {interaction.user}")
        except Exception:
            await interaction.followup.send("Erro ao fechar.", ephemeral=True)
    @commands.hybrid_command(name="ticket", description="Abre ticket.")
    @commands.guild_only()
    async def ticket(self, ctx: commands.Context, *, assunto: str = "Suporte"):
        g = ctx.guild
        async with get_session() as s:
            q = await s.exec(select(func.count(Ticket.id)).where(Ticket.guild_id == g.id, Ticket.user_id == ctx.author.id, Ticket.status == "open"))
            n = q.one()
        if n >= settings.TICKET_MAX_OPEN:
            return await ctx.send(f"Voce ja tem {n} aberto(s).")
        ow = self._overwrites(g, ctx.author)
        for r in await self._staff_roles(g):
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        cat = g.get_channel(settings.TICKET_CATEGORY_ID) if settings.TICKET_CATEGORY_ID else None
        try:
            ch = await g.create_text_channel(f"ticket-{ctx.author.display_name}", overwrites=ow, category=cat)
        except discord.Forbidden:
            return await ctx.send(embed=error_embed("Ticket", "Sem permissao p/ criar canais."))
        async with get_session() as s:
            s.add(Ticket(guild_id=g.id, user_id=ctx.author.id, channel_id=ch.id, subject=assunto))
            await s.commit()
        await ctx.send(embed=success_embed("Ticket", f"Criado: {ch.mention}"))
        await ch.send(f"{ctx.author.mention}", embed=info_embed("Ticket", f"Assunto: **{assunto}**"), view=CloseView())

    @commands.hybrid_command(name="ticketpanel", description="Posta painel.")
    @is_mod()
    @commands.guild_only()
    async def ticketpanel(self, ctx: commands.Context):
        em = info_embed("Suporte", "Clique abaixo para abrir ticket privado.")
        await ctx.send(embed=em, view=OpenView())

    @commands.hybrid_command(name="ticketclose", description="Fecha ticket.")
    @commands.guild_only()
    async def ticketclose(self, ctx: commands.Context):
        ch = ctx.channel
        if not ch.name.startswith("ticket-"):
            return await ctx.send("Nao e ticket.")
        async with get_session() as s:
            q = await s.exec(select(Ticket).where(Ticket.guild_id == ctx.guild.id, Ticket.channel_id == ch.id, Ticket.status == "open"))
            t = q.first()
            if t:
                from datetime import datetime
                t.status = "closed"
                t.closed_at = datetime.utcnow()
                s.add(t)
                await s.commit()
        try:
            await ctx.send("Fechando...")
            await ch.delete(reason=f"Fechado por {ctx.author}")
        except Exception as e:
            await ctx.send(embed=error_embed("Ticket", f"Erro: {e}"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
    bot.add_view(OpenView())
    bot.add_view(CloseView())

