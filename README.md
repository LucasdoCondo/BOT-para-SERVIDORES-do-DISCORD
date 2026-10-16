# 🤖 Discord Bot Modular — Gemini IA + Moderação

Bot Discord em Python (`discord.py` 2.x) com arquitetura modular em **Cogs**, IA gratuita via **Google Gemini**, moderação, **PostgreSQL via Docker** + **SQLModel**, levels com XP/rank e deploy 24/7 pronto para VPS Ubuntu (Oracle Cloud).

## ✨ Features

- 🧩 **Modular com Cogs** — adicione recursos sem mexer no `main.py`
- 🤖 **IA Grátis (Gemini)** — `/ask`, `/chat` com memória + `/resumir` + persona por servidor
- 🎭 **Persona IA** — `/setpersona` (mod) por servidor ou `AI_PERSONA` global
- 🗄️ **Postgres + Alembic** — migrations versionadas (`alembic upgrade head` no boot) + backup auto
- 🛡️ **Moderação** — `kick`, `ban`, `unban`, `mute` (timeout), `unmute`, `clear` + filtro de palavras + canal modlog
- ⚠️ **Warns + automute** — `!warn`, `!warns`, `!clearwarns`, mute auto configurável (Postgres)
- 👋 **Welcome + autorole** — embed de boas-vindas + cargos auto
- 🚨 **Automod leve** — antiflood com mute auto + anti-invite
- 📊 **Status** — `!status`/`/status` (uptime, ping, banco)
- 🎫 **Tickets** — painel com botão → canal privado + `!ticket`/`!ticketclose` (Postgres)
- ⏰ **Reminders persistentes** — `!remind 10m texto` (sobrevive reboot)
- 🗄️ **PostgreSQL + SQLModel** — tabelas `user_levels`, `warns`, `tickets`, `reminders`, `guild_configs`
- 💾 **Backup auto** — `docker compose --profile backup run backup` ou `scripts/backup.sh` (cron)
- 🏆 **Levels** — XP por mensagem com cooldown, `!rank`, `!leaderboard`
- 📝 **Logs + erros amigáveis** — console + `logs/bot.log` rotativo, cooldowns e permissões tratados
- 🐳 **Docker 24/7** — `restart: unless-stopped`, healthcheck bot + Postgres, volume `pgdata`, CI GitHub
- ⚡ **Slash + Prefix** — hybrid commands (`/ping` e `!ping` funcionam)

## 📋 Pré-requisitos

1. Python 3.11+ (só p/ rodar local sem Docker)
2. Conta Discord Developer + Bot criado
3. Chave gratuita Gemini: https://aistudio.google.com/app/apikey
4. Docker + Docker Compose (local ou VPS)

### Portal Discord — obrigatório

Em https://discord.com/developers/applications → seu App → **Bot**:

- [x] `MESSAGE CONTENT INTENT` → ON
- [x] `SERVER MEMBERS INTENT` → ON
- `OAuth2 → URL Generator`: scopes `bot` + `applications.commands`, permissões `Administrator` (ou Kick/Ban/Timeout/Manage Messages) → convide p/ seu servidor

## 🚀 Quickstart Local (Windows)

```powershell
cd "c:\Users\Administrador\Documents\LDC\PROJETOS\BOTs DISCORD"
copy .env.example .env
notepad .env   # preencha DISCORD_TOKEN e GEMINI_API_KEY
pip install -r requirements.txt
python main.py
```

Teste no Discord: `!ping`, `!help`, `/ask o que é Python?`, `!rank`

> Local sem Docker precisa de Postgres rodando. Instale via Docker `docker run -d --name pg -e POSTGRES_USER=bot -e POSTGRES_PASSWORD=bot_secret_troque_aqui -e POSTGRES_DB=botdb -p 5432:5432 postgres:16-alpine` ou use o compose completo abaixo.

## 🗄️ Banco — PostgreSQL na VPS (via Docker)

O `docker-compose.yml` sobe 2 serviços: `db` (postgres:16-alpine, ~50-100MB RAM, volume `pgdata`) + `discord-bot` (espera o `db` ficar healthy via `depends_on` + `pg_isready`).

Tabelas criadas no boot via `SQLModel.metadata.create_all` (MVP em `core/db.py::init_db`):
- `user_levels` (guild_id, user_id, xp, level, message_count)
- `warns` (pré-criada p/ próximo Cog de warns)

Troque a senha padrão! No `.env`: `POSTGRES_PASSWORD=senha_forte` (o compose monta a `DATABASE_URL` interna `...@db:5432/...` sozinho).

Backup:
```bash
docker exec discord-bot-db pg_dump -U bot botdb > backup_$(date +%F).sql
cat backup_*.sql | docker exec -i discord-bot-db psql -U bot -d botdb
```

Acesso rápido:
```bash
docker exec -it discord-bot-db psql -U bot -d botdb -c "SELECT * FROM user_levels ORDER BY level DESC LIMIT 10;"
```

## 🐳 Rodar com Docker (local)

```powershell
copy .env.example .env  # se ainda não fez
docker compose up -d --build
docker logs -f discord-bot
# parar: docker compose down
```

## ☁️ Deploy Oracle Cloud (Ubuntu 22.04/24.04) — 24/7

### 1. Criar VM (Always Free)

1. OCI Console → Compute → Instances → Create.
2. Image: **Ubuntu 22.04 ou 24.04 Minimal** | Shape: `VM.Standard.E2.1.Micro` (free) ou Ampere A1.
3. Adicione sua chave SSH (`.pub`), crie a VCN padrão com internet.
4. Security List: libere **egress total** (bot só faz conexão de saída p/ Discord — nenhuma porta de entrada precisa ser aberta).

### 2. Preparar VPS

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git nano curl
# Docker oficial
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
docker --version && docker compose version
```

### 3. Subir o bot

```bash
git clone <SEU-REPO> bot && cd bot
cp .env.example .env && nano .env   # preencha DISCORD_TOKEN + GEMINI_API_KEY
mkdir -p logs
docker compose up -d --build
docker logs -f discord-bot
# deve mostrar: Logado como ... + slash commands sincronizados
```

### 4. Garantir 24/7 (auto-restart)

- O `restart: unless-stopped` no `docker-compose.yml` já faz o container voltar após reboot/crash.
- Habilite Docker no boot (geralmente já vem ativo):

```bash
sudo systemctl enable docker
sudo systemctl is-enabled docker
# teste reboot:
sudo reboot
# apos voltar:
docker ps --format '{{.Names}} {{.Status}}'
docker logs --tail 50 discord-bot
```

### 5. Atualizar versão

```bash
cd ~/bot
git pull
docker compose up -d --build
docker logs -f --tail 100 discord-bot
```

### 6. Operação

```bash
docker ps                          # status
docker logs -f discord-bot         # log ao vivo
docker logs --since 1h discord-bot # ultima hora
docker compose restart             # reiniciar
docker compose down                # parar
df -h && free -h                   # disco/RAM (free tier é apertado)
cat logs/bot.log | tail -n 50      # log em arquivo (via volume)
```

### Backup / restore

```bash
docker compose --profile backup run --rm backup   # backup manual (.sql.gz em ./backups, mantém 7)
bash scripts/backup.sh                            # mesmo via script
# cron diário 3h:
(crontab -l; echo "0 3 * * * cd ~/bot && docker compose --profile backup run --rm backup >> logs/backup.log 2>&1") | crontab -
# restore:
gunzip -c backups/botdb_XXXX.sql.gz | docker exec -i discord-bot-db psql -U bot -d botdb
```

### Migrations (Alembic)

Boot roda `alembic upgrade head` sozinho (fallback `create_all`). Nova mudança:
```bash
alembic revision --autogenerate -m "add coluna X"
docker compose up -d --build   # aplica no boot
```

## ⚙️ Variáveis de ambiente

| Var | Obrigatória | Padrão | Descrição |
|-----|-------------|--------|-----------|
| `DISCORD_TOKEN` | ✅ | — | Token do bot |
| `GEMINI_API_KEY` | ✅ p/ IA | — | Grátis em aistudio.google.com/app/apikey |
| `GEMINI_MODEL` | Não | `gemini-2.0-flash` | Modelo Gemini |
| `COMMAND_PREFIX` | Não | `!` | Prefixo comandos texto |
| `LOG_LEVEL` | Não | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `MOD_ROLE_IDS` | Não | — | Cargos mod ex: `123,456` |
| `MODLOG_CHANNEL_ID` | Não | `0` | Canal log moderação |
| `BANNED_WORDS` | Não | `spam,http://,https://` | Filtro separado por vírgula |
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://...` | No compose é montada sozinha; local use `@localhost:5432` |
| `POSTGRES_USER` | ✅ compose | `bot` | Usuário do banco |
| `POSTGRES_PASSWORD` | ✅ compose | — | **Troque!** Senha do banco |
| `POSTGRES_DB` | ✅ compose | `botdb` | Nome do banco |
| `XP_PER_MESSAGE_MIN` | Não | `5` | XP mínimo por msg |
| `XP_PER_MESSAGE_MAX` | Não | `15` | XP máximo por msg |
| `XP_COOLDOWN_SECONDS` | Não | `60` | Cooldown anti-flood XP |
| `WARN_MAX` | Não | `3` | Warns p/ automute |
| `WARN_AUTOMUTE_MINUTES` | Não | `60` | Minutos do automute |
| `AI_PERSONA` | Não | — | Persona global IA |
| `AI_SUMMARY_MAX_CHARS` | Não | `1500` | Max resumo |
| `TICKET_CATEGORY_ID` | Não | `0` | Categoria tickets |
| `TICKET_STAFF_ROLE_IDS` | Não | — | Cargos staff tickets |
| `TICKET_MAX_OPEN_PER_USER` | Não | `3` | Max abertos/user |

## 💬 Comandos

### Geral

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!ping` / `/ping` | hybrid | Latência |
| `!help` / `/help` | hybrid | Lista comandos |
| `!info` / `/info` | hybrid | Info bot + servidor |

### IA Gemini (grátis)

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!ask <pergunta>` / `/ask` | prefix+slash | Pergunta única (sem memória) |
| `!chat <msg>` / `/chat` | prefix+slash | Conversa com memória (por usuário, últimas 10 trocas) |
| `!clearchat` | prefix | Limpa sua memória |

> Limite Discord 2000 chars: respostas longas são cortadas. Cooldown 5s por usuário. Erros comuns (chave inválida, quota 429) retornam msg amigável.

### Persona IA + resumo

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!persona` / `/persona` | hybrid | Ver persona do servidor |
| `!setpersona <texto>` (mod) | hybrid | Define persona (max 2000) |
| `!clearpersona` (mod) | hybrid | Volta ao padrão |
| `!resumir [5-50]` | hybrid | Resume canal (cooldown 30s/canal) |

> Hierarquia: `guild_configs.persona` > `AI_PERSONA` global > padrão. Resumo usa últimas msgs (ignora bots) e economiza quota.

### Moderação (requer cargo mod/admin)

| Comando | Permissão Bot | Exemplo |
|---------|---------------|---------|
| `!kick @user motivo` | Kick Members | `!kick @troll flood` |
| `!ban @user motivo` | Ban Members | `!ban @troll raid` |
| `!unban <id>` | Ban Members | `!unban 123456789` |
| `!mute @user <min> motivo` | Timeout Members | `!mute @troll 60 spam` |
| `!unmute @user` | Timeout Members | `!unmute @troll` |
| `!clear <1-100>` | Manage Messages | `!clear 20` |

Filtro: deleta msg com palavra de `BANNED_WORDS` (ignora quem tem Gerenciar Mensagens) e avisa no `MODLOG_CHANNEL_ID` se configurado.

### Warns (Postgres + automute)

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!warn @user motivo` / `/warn` | hybrid | +1 warn (automute com 3) |
| `!warns @user` / `/warns` | hybrid | Últimos 10 warns |
| `!clearwarns @user` / `/clearwarns` | hybrid | Zera warns |

> Automute: `WARN_MAX=3` + `WARN_AUTOMUTE_MINUTES=60` no `.env`. Tabela `warns` no Postgres, log no modlog.

### Levels (Postgres)

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!rank [@user]` / `/rank` | hybrid | Nível, XP, barra de progresso |
| `!leaderboard` / `/leaderboard` | hybrid | Top 10 do servidor |

> XP automático: 5-15 por mensagem (configurável), cooldown 60s anti-flood, ignora bots e msgs curtas. Fórmula próximo nível: `5*lvl² + 50*lvl + 100`.

### Tickets (Postgres)

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!ticket [assunto]` | hybrid | Abre canal privado |
| `!ticketpanel` (mod) | hybrid | Posta painel com botão |
| `!ticketclose` | hybrid | Fecha ticket atual |

> Configure `TICKET_CATEGORY_ID`, `TICKET_STAFF_ROLE_IDS`, `TICKET_MAX_OPEN_PER_USER=3`. Views persistentes (botão funciona após reboot).

### Reminders (Postgres)

| Comando | Tipo | Descrição |
|---------|------|-----------|
| `!remind 10m texto` | hybrid | `10s/5m/2h/1d` (10s–30d) |
| `!reminders` | hybrid | Lista seus lembretes |

## 🗂️ Estrutura

```
.
├── main.py              # entry-point, automigrate alembic + fallback, sync tree
├── requirements.txt     # discord.py + Gemini + SQLModel + asyncpg + alembic + psycopg
├── Dockerfile           # python:3.12-slim, healthcheck /tmp/bot_alive
├── docker-compose.yml   # db + bot + backup(profile), pgdata
├── alembic.ini + alembic/  # migrations versionadas (0001_initial)
├── scripts/backup.sh    # pg_dump + gzip + prune 7
├── .env.example         # + AI_PERSONA, TICKET_*, etc.
├── .env.example         # DATABASE_URL, POSTGRES_*, XP_*, WARN_*, WELCOME_*, AUTOMOD_*, TICKET_*
├── config/settings.py   # lê .env (dataclass Settings)
├── core/logger.py       # console + RotatingFile logs/bot.log
├── core/db.py           # engine async + init_db retry + get_session
├── core/checks.py       # is_mod() reutilizável
├── models/levels.py     # UserLevel + Warn
├── models/tickets.py    # Ticket
├── models/reminders.py  # Reminder
├── models/guild_config.py  # Persona por servidor
├── .github/workflows/ci.yml  # compile + compose config + build
├── utils/embeds.py      # success/error/info
└── cogs/
    ├── general.py       # ping/help/info
    ├── ai.py            # Gemini ask/chat
    ├── moderation.py    # kick/ban/mute/clear/filtro
    ├── levels.py        # XP/rank/leaderboard
    ├── warns.py         # warn/warns/clearwarns + automute
    ├── welcome.py       # boas-vindas + autorole
    ├── automod.py       # antiflood + anti-invite
    ├── tickets.py       # painel + canal privado
    ├── reminders.py     # remind loop 30s
    ├── persona.py       # setpersona + resumir
    ├── status.py        # status/uptime/banco
    └── errors.py        # on_command_error + on_app_command_error
```

Adicionar Cog novo: crie `cogs/meucog.py` com `async def setup(bot)` + adicione `"cogs.meucog"` na lista `initial_cogs` no `main.py`.

## 🛠️ Troubleshooting

| Sintoma | Causa provável | Fix |
|---------|----------------|-----|
| `DISCORD_TOKEN não definido` | Sem `.env` | `cp .env.example .env` + preencher |
| `LoginFailure / 401` | Token inválido | Reset token no Portal Dev, atualize `.env`, rebuild |
| Prefix `!` não responde | `MESSAGE CONTENT INTENT` OFF | Ative no Portal + reinicie bot |
| kick/ban/mute falha | Intents/cargos | Ative `SERVER MEMBERS INTENT`, suba cargo do bot acima dos alvos |
| Slash não aparece | Sync global leva até 1h | Aguarde ou teste com sync de guild; `docker logs` mostra `X slash sincronizados` |
| `GEMINI_API_KEY inválida` | Chave errada | Regenere em AI Studio, confira `.env`, rebuild |
| `429 / quota` Gemini | Limite free | Aguarde, reduza uso, troque `GEMINI_MODEL` p/ `gemini-1.5-flash` |
| Container reiniciando | Erro no boot | `docker logs --tail 100 discord-bot` + `cat logs/bot.log` |
| `Falha ao conectar no banco` | Postgres down / URL errada | `docker ps` (db healthy?), `docker logs discord-bot-db`, confira `POSTGRES_*` e rebuild |
| `rank` diz sem XP | Tabela vazia | Fale no chat (XP tem cooldown 60s), confira `SELECT * FROM user_levels;` |
| Sem espaço (Oracle free) | Disco cheio | `docker system prune -f`, `df -h`, limite `logs/` |

## 🔒 Segurança

- Nunca commite `.env` (já está no `.gitignore`). Só `.env.example`.
- Regenere o token se vazar (Portal → Bot → Reset Token).
- Rode com usuário `botuser` no Docker (já configurado).
- No Oracle, mantenha `egress` liberado e **não abra portas de entrada** — o bot não precisa.

## 🗺️ Roadmap — próximos Cogs sugeridos

### Fase 1 — Engajamento
- [x] `cogs/levels.py` — XP/rank/leaderboard (Postgres)
- [x] `cogs/welcome.py` — boas-vindas + autorole
- [x] `cogs/reminders.py` — `!remind` + `!reminders` persistentes (Postgres)

### Fase 2 — Moderação Pro
- [x] `cogs/automod.py` — antiflood + anti-invite
- [x] `cogs/warns.py` — warns + automute (Postgres)
- [x] `cogs/tickets.py` — painel botão → canal privado (Postgres)

### Fase 3 — IA Avançada
- [x] `cogs/persona.py` — persona por servidor (`/setpersona`), `/resumir` canal
- [ ] Cache/resumo p/ economizar quota Gemini

### Fase 4 — Ops/Dashboard
- [x] `cogs/status.py` — `!status` (uptime, ping, banco)
- [x] Healthcheck Dockerfile (`/tmp/bot_alive`) + CI (compile + build)
- [x] Alembic migrations (`upgrade head` no boot + fallback) + backup auto (profile + cron)

> Núcleo completo ✅. Próximo: persona IA → Alembic → backup auto.

## 📄 Licença

MIT — use livremente. Veja `LICENSE` se adicionar.


