"""Sistema básico de logs: console + arquivo rotativo."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(level: str = "INFO") -> None:
    os.makedirs("logs", exist_ok=True)
    numeric = getattr(logging, level.upper(), logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(numeric)

    # Evita handlers duplicados no reload
    if root.handlers:
        return

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        "logs/bot.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # Silencia libs barulhentas
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
