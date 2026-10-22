# CRM Factory Telegram bot

A Telegram bot for [CRM Factory](https://github.com/EvgeniyK96/CRM-example), an ERP for a confectionery factory.
The factory team gets the things that need attention straight in Telegram, without opening the CRM:

- 📦 **Low stock**: a raw material drops below its minimum
- ⏳ **Expiry control**: a batch is about to expire or has expired (the CRM consumes stock FEFO)
- 🔄 **Live activity**: orders, production tasks, purchase orders and goods receipts change status
- 📊 **Daily digest** at 09:00: revenue, open orders, shop load and a "needs attention" list

Every alert has an **Open in CRM** button that leads to the exact record.

| Command | What it shows |
|---|---|
| `/today` | Daily digest |
| `/orders` | Open orders by delivery date, overdue ones flagged |
| `/stock` | Raw materials below minimum |
| `/expiring` | Batches expiring or expired |
| `/feed` | Latest CRM activity |
| `/alerts` | Turn alerts on/off for this chat |

## How it works

```
CRM (Django + DRF) ◄── JWT, read-only ── watcher (every 60 s) ──► Telegram subscribers
                                          │
                                   SQLite: subscribers,
                                   last seen event, active alerts
```

The CRM has no webhooks, so the bot polls its REST API and compares snapshots:

- **activity feed**: entries newer than the last seen id;
- **warehouse**: alert keys like `shortage:41` or `expired:73` that were not active on the previous check.
  A key that goes away (stock replenished, batch written off) is forgotten, so the alert fires again if the problem comes back.

The first run only records a baseline, so a fresh deploy doesn't flood the chat with old news.
Access tokens are refreshed automatically on `401`. The bot never writes to the CRM.

**Stack:** Python 3.12, aiogram 3, httpx, SQLite, Docker, pytest.

## Run

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. `cp .env.example .env` and fill in `BOT_TOKEN`, `CRM_USERNAME`, `CRM_PASSWORD`.
   Use a CRM account with read-only access.
3. Start it:

```bash
docker compose up -d --build
# or locally
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
set -a && . ./.env && set +a && .venv/bin/python -m bot
```

Set `BOT_LANG=ru` for Russian. Set `ALLOWED_USER_IDS` to keep the bot private.

## Tests

```bash
.venv/bin/pytest
```

The tests cover the watcher's baseline and de-duplication logic, token refresh against a mocked API, and message formatting.
