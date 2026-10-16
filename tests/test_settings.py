"""Testes de config/env (sem rede)."""
import os


def test_settings_defaults():
    from config.settings import settings
    assert settings.COMMAND_PREFIX
    assert settings.XP_PER_MESSAGE_MIN <= settings.XP_PER_MESSAGE_MAX
    assert settings.WARN_MAX >= 1
    assert settings.AI_CACHE_TTL_HOURS >= 1


def test_env_example_has_keys():
    p = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example")
    txt = open(p, encoding="utf-8").read()
    for k in ["DISCORD_TOKEN", "DATABASE_URL", "AI_CACHE_ENABLED", "DASHBOARD_PORT", "TICKET_CATEGORY_ID"]:
        assert k in txt, k
