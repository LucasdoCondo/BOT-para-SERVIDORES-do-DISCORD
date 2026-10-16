"""Cog de Reprodução de Lo-Fi via YouTube para desenvolvedores e membros."""
import asyncio
import logging
import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed, info_embed

log = logging.getLogger("bot.music")

# Link padrão de stream 24/7 de Lo-Fi (ex: Lofi Girl no YouTube)
DEFAULT_LOFI_URL = "https://www.youtube.com/watch?v=jfKfPfyJRdk"

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="lofi", description="Conecta ao canal de voz e toca Lo-Fi 24/7.")
    @commands.guild_only()
    async def lofi(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(embed=error_embed("Lo-Fi", "Você precisa estar em um canal de voz!"))
        
        voice_channel = ctx.author.voice.channel
        vc = ctx.guild.voice_client

        if vc and vc.is_connected():
            await vc.move_to(voice_channel)
        else:
            try:
                vc = await voice_channel.connect()
            except Exception as e:
                return await ctx.send(embed=error_embed("Lo-Fi", f"Erro ao conectar no canal: {e}"))

        await ctx.send(embed=info_embed("🎵 Lo-Fi", f"Conectado em **{voice_channel.name}**. Carregando stream do YouTube..."))

        # Configuração do yt-dlp otimizada para extrair o stream de áudio direto
        ytdl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, DEFAULT_LOFI_URL, download=False)
                audio_url = info['url']
        except Exception as e:
            log.exception("Erro ao extrair link do YouTube")
            return await ctx.send(embed=error_embed("Lo-Fi", f"Erro ao processar o YouTube: {e}"))

        # Opções do FFmpeg para otimizar streaming contínuo
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        if vc.is_playing():
            vc.stop()

        try:
            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            vc.play(source, after=lambda e: log.error(f"Erro no player: {e}") if e else None)
            await ctx.send(embed=success_embed("Lo-Fi Ativo", "Aproveite as batidas relaxantes de Lo-Fi! 🎧"))
        except Exception as e:
            log.exception("Erro ao reproduzir áudio")
            await ctx.send(embed=error_embed("Lo-Fi", f"Não foi possível iniciar o player: {e}"))

    @commands.hybrid_command(name="stop", description="Para o som e desconecta o bot do canal de voz.")
    @commands.guild_only()
    async def stop(self, ctx: commands.Context):
        vc = ctx.guild.voice_client
        if vc and vc.is_connected():
            await vc.disconnect()
            await ctx.send(embed=success_embed("Lo-Fi", "Desconectado do canal de voz."))
        else:
            await ctx.send(embed=error_embed("Lo-Fi", "Eu não estou em nenhum canal de voz."))

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))