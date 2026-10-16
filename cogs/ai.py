"""Cog de IA gratuita usando Google Gemini."""
import asyncio
import logging
import discord
from discord import app_commands
from discord.ext import commands
from config.settings import settings

log = logging.getLogger("bot.ai")
SYSTEM_PROMPT = (
    "Voce e um assistente util e amigavel no Discord. "
    "Responda em portugues (pt-BR), claro e conciso. "
    "Limite a ~1500 caracteres."
)
_chat_history: dict[int, list[dict]] = {}
MAX_HISTORY = 10

def _get_model():
    if not settings.GEMINI_API_KEY:
        url = "https://aistudio.google.com/app/apikey"
        return None, f"GEMINI_API_KEY nao configurada. Pegue gratis em {url}"
    try:
        import google.generativeai as genai
    except ImportError:
        return None, "Lib google-generativeai nao instalada. Rode pip install -r requirements.txt"
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        return model, None
    except Exception as e:
        log.exception("Erro ao configurar Gemini")
        return None, f"Erro ao configurar Gemini: {e}"

async def _generate(prompt: str, history=None, use_cache: bool = True) -> str:
    model, err = _get_model()
    if err:
        return f"AVISO {err}"
    # Cache só p/ perguntas únicas (sem histórico) — economiza quota
    ckey = None
    if use_cache and not history and settings.AI_CACHE_ENABLED:
        try:
            from core.ai_cache import cache_get
            from models import cache_key
            ckey = cache_key(settings.GEMINI_MODEL, SYSTEM_PROMPT, prompt)
            hit = await cache_get(ckey)
            if hit:
                log.info("IA cache HIT")
                return hit
        except Exception:
            pass
    try:
        if history:
            chat = model.start_chat(history=history)
            resp = await asyncio.to_thread(chat.send_message, prompt)
        else:
            resp = await asyncio.to_thread(model.generate_content, prompt)
        text = (resp.text or "").strip()
        if not text:
            return "AVISO A IA retornou vazio. Tente reformular."
        if len(text) > 1900:
            text = text[:1900] + "\n\n...(cortada)"
        if ckey:
            try:
                from core.ai_cache import cache_set
                await cache_set(ckey, prompt, text, settings.AI_CACHE_TTL_HOURS)
            except Exception:
                pass
        return text
    except Exception as e:
        log.exception("Erro Gemini")
        msg = str(e)
        if "API_KEY_INVALID" in msg or "API key not valid" in msg:
            return "AVISO Chave Gemini invalida. Verifique GEMINI_API_KEY."
        if "429" in msg or "quota" in msg.lower():
            return "Limite gratuito atingido. Tente em alguns segundos."
        return f"Erro na IA: {msg[:500]}"
class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ask", help="Pergunte a IA. Ex: !ask o que e Python?")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask_prefix(self, ctx: commands.Context, *, pergunta: str):
        async with ctx.channel.typing():
            answer = await _generate(pergunta, None)
        em = discord.Embed(title="Gemini", description=answer, color=discord.Color.purple())
        em.set_footer(text=f"Modelo: {settings.GEMINI_MODEL}")
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(name="chat", help="Conversa com memoria. Ex: !chat ola!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def chat_prefix(self, ctx: commands.Context, *, mensagem: str):
        async with ctx.channel.typing():
            uid = ctx.author.id
            hist = _chat_history.get(uid, [])
            answer = await _generate(mensagem, hist)
            if not answer.startswith("AVISO"):
                h = _chat_history.setdefault(uid, [])
                h.append({"role": "user", "parts": [mensagem]})
                h.append({"role": "model", "parts": [answer]})
                del h[:-MAX_HISTORY * 2]
        em = discord.Embed(title="Gemini chat", description=answer, color=discord.Color.purple())
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(name="clearchat", help="Limpa sua memoria com a IA.")
    async def clearchat(self, ctx: commands.Context):
        _chat_history.pop(ctx.author.id, None)
        await ctx.send("Memoria limpa!")

    @app_commands.command(name="ask", description="Pergunte a IA Gemini gratis.")
    async def ask_slash(self, interaction: discord.Interaction, pergunta: str):
        await interaction.response.defer(thinking=True)
        answer = await _generate(pergunta, None)
        em = discord.Embed(title="Gemini", description=answer, color=discord.Color.purple())
        em.set_footer(text=f"Modelo: {settings.GEMINI_MODEL}")
        await interaction.followup.send(embed=em)

    @app_commands.command(name="chat", description="Converse com a IA com memoria.")
    async def chat_slash(self, interaction: discord.Interaction, mensagem: str):
        await interaction.response.defer(thinking=True)
        uid = interaction.user.id
        hist = _chat_history.get(uid, [])
        answer = await _generate(mensagem, hist)
        if not answer.startswith("AVISO"):
            h = _chat_history.setdefault(uid, [])
            h.append({"role": "user", "parts": [mensagem]})
            h.append({"role": "model", "parts": [answer]})
            del h[:-MAX_HISTORY * 2]
        em = discord.Embed(title="Gemini chat", description=answer, color=discord.Color.purple())
        await interaction.followup.send(embed=em)

    @app_commands.command(name="pesquisar", description="Realiza uma pesquisa estruturada utilizando IA.")
    async def search_slash(self, interaction: discord.Interaction, *, topico: str):
        await interaction.response.defer(thinking=True)
        prompt_pesquisa = f"Pesquise mentalmente e elabore um resumo detalhado, tecnico e estruturado em topicos sobre: {topico}"
        answer = await _generate(prompt_pesquisa, None)
        em = discord.Embed(title=f"🔍 Pesquisa IA: {topico}", description=answer, color=discord.Color.blue())
        em.set_footer(text=f"Gerado via Google Gemini ({settings.GEMINI_MODEL})")
        await interaction.followup.send(embed=em)


async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))

