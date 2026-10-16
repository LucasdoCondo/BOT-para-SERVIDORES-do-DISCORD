"""Cog de administração para execução de tarefas sob comando."""
import logging
import discord
from discord.ext import commands
from core.checks import is_mod
from utils.embeds import success_embed, error_embed, info_embed

log = logging.getLogger("bot.admin_tasks")

class AdminTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="run", help="Executa rotinas administrativas customizadas.")
    @is_mod()
    async def run_task(self, ctx: commands.Context, tarefa: str, *, parametros: str = ""):
        """
        Exemplo de uso: !run limpar_cache
        """
        tarefa = tarefa.lower()
        await ctx.typing()

        if tarefa == "limpar_cache":
            try:
                from core.ai_cache_evict import evict_once
                removidos = await evict_once()
                return await ctx.send(embed=success_embed("Tarefa Executada", f"Cache de IA limpo com sucesso! `{removidos}` itens removidos."))
            except Exception as e:
                return await ctx.send(embed=error_embed("Erro na Tarefa", f"Não foi possível limpar o cache: {e}"))

        elif tarefa == "status_sistema":
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            desc = f"💻 **CPU:** `{cpu}%`\n🧠 **RAM:** `{ram}%`\n💽 **Disco:** `{disk}%`"
            return await ctx.send(embed=info_embed("Métricas da VPS Oracle", desc))

        else:
            await ctx.send(embed=error_embed("Comando Desconhecido", f"A tarefa `{tarefa}` não está cadastrada no sistema."))

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminTasks(bot))