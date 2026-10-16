"""Persona IA por servidor + resumo (economia de quota)."""
import logging
import discord
from discord.ext import commands
from config.settings import settings
from core.checks import is_mod
from core.db import get_session
from models import GuildConfig
from utils.embeds import success_embed, error_embed, info_embed
import cogs.ai as ai_core

log = logging.getLogger("bot.persona")

async def _get_persona(guild_id: int) -> str:
    async with get_session() as s:
        cfg = await s.get(GuildConfig, guild_id)
        if cfg and cfg.persona:
            return cfg.persona
class Persona(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="persona", description="Ver persona IA do servidor.")
    async def persona_show(self, ctx: commands.Context):
        if not ctx.guild:
            return await ctx.send("Use num servidor.")
        p = await _get_persona(ctx.guild.id)
        await ctx.send(embed=info_embed("Persona", p[:1500]))

    @commands.hybrid_command(name="setpersona", description="Define persona IA (mod).")
    @is_mod()
    @commands.guild_only()
    async def persona_set(self, ctx: commands.Context, *, texto: str):
        if len(texto) > 2000:
            return await ctx.send(embed=error_embed("Persona", "Max 2000 chars."))
        async with get_session() as s:
            cfg = await s.get(GuildConfig, ctx.guild.id)
            if not cfg:
                cfg = GuildConfig(guild_id=ctx.guild.id, persona=texto)
            else:
                cfg.persona = texto
            s.add(cfg)
            await s.commit()
        await ctx.send(embed=success_embed("Persona", "Atualizada! Vale p/ !ask/!chat."))

    @commands.hybrid_command(name="clearpersona", description="Volta persona padrao.")
    @is_mod()
    @commands.guild_only()
    async def persona_clear(self, ctx: commands.Context):
        async with get_session() as s:
            cfg = await s.get(GuildConfig, ctx.guild.id)
            if cfg:
                await s.delete(cfg)
                await s.commit()
        await ctx.send(embed=success_embed("Persona", "Removida. Voltou ao padrao."))

    @commands.hybrid_command(name="resumir", description="Resume ultimas msgs do canal.")
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @commands.guild_only()
    async def resumir(self, ctx: commands.Context, qtd: int = 20):
        if qtd < 5 or qtd > 50:
            return await ctx.send(embed=error_embed("Resumir", "Use 5 a 50."))
        msgs = [m async for m in ctx.channel.history(limit=qtd + 1)]
        msgs = [m for m in msgs if m.id != ctx.message.id and not m.author.bot][:qtd]
        if not msgs:
            return await ctx.send("Sem mensagens.")
        convo = "\n".join(f"{m.author.display_name}: {m.content[:200]}" for m in reversed(msgs))
        convo = convo[:settings.AI_SUMMARY_MAX * 2]
        persona = await _get_persona(ctx.guild.id)
        prompt = f"{persona}\nResuma a conversa abaixo em pt-BR, tópicos curtos (max {settings.AI_SUMMARY_MAX} chars):\n{convo}"
        async with ctx.channel.typing():
            import asyncio
            model, err = ai_core._get_model()
            if err:
                return await ctx.send(f"AVISO {err}")
            # injeta persona temporária
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                m2 = genai.GenerativeModel(model_name=settings.GEMINI_MODEL, system_instruction=persona)
                resp = await asyncio.to_thread(m2.generate_content, prompt)
                txt = (resp.text or "").strip()[:1900] or "Vazio."
            except Exception as e:
                txt = f"Erro: {e}"[:500]
        await ctx.send(embed=info_embed(f"Resumo ({len(msgs)} msgs)", txt))


async def setup(bot: commands.Bot):
    await bot.add_cog(Persona(bot))

    return settings.AI_PERSONA or ai_core.SYSTEM_PROMPT
