"""Testes rápidos sem Discord/banco (lógica pura). Rode: python -m pytest -q"""
from cogs.levels import xp_for_next
from cogs.reminders import parse_dur
from models import cache_key


def test_xp_curve():
    assert xp_for_next(1) == 5 + 50 + 100
    assert xp_for_next(2) < xp_for_next(3) < xp_for_next(10)


def test_parse_dur():
    assert parse_dur("10s") == 10
    assert parse_dur("5m") == 300
    assert parse_dur("2h") == 7200
    assert parse_dur("1d") == 86400
    assert parse_dur("xx") is None
    assert parse_dur("5x") is None


def test_cache_key_stable():
    a = cache_key("m", "p", "Ola Mundo")
    b = cache_key("m", "p", "  ola mundo ")
    assert a == b and len(a) == 64
