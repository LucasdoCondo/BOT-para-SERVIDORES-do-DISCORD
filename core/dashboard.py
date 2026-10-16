"""Dashboard FastAPI — /healthz, /metrics, /cache/stats."""
import logging
import threading
from datetime import datetime
from typing import Any

from fastapi.responses import HTMLResponse
import os


def _stats() -> dict[str, Any]:
    total = 0
    expired = 0
    async def _count():
        nonlocal total, expired
        async with engine.begin() as conn:
            r = await conn.execute(AICache.__table__.select().with_only_columns(AICache.__table__.count()))
            total = r.scalar()
            r2 = await conn.execute(AICache.__table__.select().with_only_columns(AICache.__table__.count()))
            expired = r2.scalar()
    asyncio.run(_count())
    now = datetime.utcnow()
    age = ""
    if total:
        async def _next_exp():
            async with engine.begin() as conn:
                row = await conn.execute(AICache.__table__.select().with_only_columns(AICache.expires_at).order_by(AICache.expires_at.asc()).limit(1))
                return await row.scalar()
        exp = asyncio.run(_next_exp())
        if exp:
            delta = (exp - now).total_seconds()
            if delta < 0:
                age = "EXPIRADO"
            elif delta < 3600:
                age = f"{delta:.0f}s"
            else:
                age = f"{delta/3600:.1f}h"
    return {"guilds": 0, "users": 0, "cogs": [], "db_ping": "ok", "cache_total": total, "cache_expired": expired, "cache_ttl_sec": age}


def start(host: str = "127.0.0.1", port: int = 8000, web_dir: str = "web") -> threading.Thread:
    app = FastAPI(title="Discord Bot Monitor", version="1.0.0")

    @app.get("/healthz")
    async def healthz():
        try:
            from core.db import get_session
            async with get_session() as s:
                await s.exec(text("SELECT 1"))
            db = "ok"
        except Exception as e:
            db = f"fail:{e}"
        return {"status": "ok", "db": db, "ts": datetime.utcnow().isoformat()}

    @app.get("/metrics")
    async def metrics():
        return _stats()

    @app.get("/cache/stats")
    async def cache_stats():
        total = 0
        async with engine.begin() as conn:
            r = await conn.execute(AICache.__table__.select().with_only_columns(AICache.__table__.count()))
            total = r.scalar()
        return {"total": total, "preview": "ver /metrics"}

    @app.get("/")
    async def index():
        try:
            with open(os.path.join(web_dir, "index.html"), encoding="utf-8") as f:
                return HTMLResponse(f.read())
        except Exception as e:
            return HTMLResponse(f"<h2>Dashboard indisponível</h2><p>mensagem: {e}</p>", status_code=503)

    @app.get("/web/{path:path}")
    async def web_index(path: str):
        return HTMLResponse("redirecting", status_code=302)

    threading.Thread(target=app.run, kwargs={"host": host, "port": port, "log_level": "warning"}, daemon=True).start()
    log.info(f"Dashboard FastAPI em http://{host}:{port}/healthz")

