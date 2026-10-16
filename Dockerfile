FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Deps do sistema (minimo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Usuario nao-root por seguranca
RUN useradd -m botuser && mkdir -p logs && chown -R botuser:botuser /app
USER botuser

# Healthcheck: bot escreve /tmp/bot_alive no on_ready
HEALTHCHECK --interval=60s --timeout=10s --start-period=90s --retries=3 \
  CMD python -c "import os,sys; sys.exit(0 if os.path.exists('/tmp/bot_alive') else 1)"

CMD ["python", "main.py"]