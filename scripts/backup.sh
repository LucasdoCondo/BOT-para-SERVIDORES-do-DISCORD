#!/usr/bin/env bash
# Backup Postgres -> ./backups (roda via cron ou docker compose service)
set -euo pipefail
mkdir -p backups
STAMP=$(date +%F_%H-%M)
FILE="backups/botdb_${STAMP}.sql"
echo "[backup] dumping to $FILE"
docker exec discord-bot-db pg_dump -U "${POSTGRES_USER:-bot}" "${POSTGRES_DB:-botdb}" > "$FILE"
gzip -f "$FILE"
echo "[backup] OK: ${FILE}.gz"
# Mantém últimos 7
ls -t backups/botdb_*.sql.gz | tail -n +8 | xargs -r rm --
echo "[backup] prune OK"
