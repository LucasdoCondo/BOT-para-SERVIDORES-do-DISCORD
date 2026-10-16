"""Helpers de embeds padronizados."""
import discord


def success_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=f"✅ {title}", description=description, color=discord.Color.green())


def error_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=f"❌ {title}", description=description, color=discord.Color.red())


def info_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=f"ℹ️ {title}", description=description, color=discord.Color.blurple())
