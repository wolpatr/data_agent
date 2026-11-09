# Playbook — agent v0.1 (freqtrade dry-run, Bybit BTC/USDT)

Spec: `.scratch/agent-v01-spec/spec.md` · Decisions: `.scratch/agent-v01-spec/map.md` · Strategy: `bot/user_data/strategies/EmaCrossBaseline.py`

All commands run from the **repo root**. Dependencies are managed by **uv** (`pyproject.toml` + `uv.lock`): run `uv sync` once to build `.venv`, and run every Python command as `uv run <command>` inside the project.

## 0. One-time setup

1. `uv sync` — creates `.venv` from `uv.lock` (freqtrade + pytest + ruff).
2. `uv run freqtrade install-ui` — downloads freqUI, served by the REST API.
3. Copy `bot/config-private.example.json` → `bot/config-private.json` (gitignored) and set a long random password.
4. `uv run freqtrade download-data -c bot/config.json --timeframes 1h --timerange 20250101-` — fills the feather store (public OHLCV, no keys).
5. `uv run freqtrade recursive-analysis -c bot/config.json --timerange 20260901- -v` — confirm indicator variance ≈ 0% for the 100-candle startup window; raise `startup_candle_count` if not.
6. Optional backtest sanity: `uv run freqtrade backtesting -c bot/config.json --timerange 20260101-`.

## 1. Daily operation

**Start** (from repo root):

```
uv run freqtrade trade --config bot/config.json --config bot/config-private.json --logfile bot/bot.log
```

**Re-arm** (the bot boots `STOPPED` by design — human-in-the-loop; use `curl.exe`, not PowerShell's `curl` alias):

```
curl.exe -s -X POST http://127.0.0.1:8080/api/v1/start -u "username:password"
```

**Dashboard**: open `http://127.0.0.1:8080` (freqUI).

**Daily check (dev mode)** — a 5-second look: freqUI state = `running`, no new `ERROR` lines in `bot/bot.log`. The bot runs in dev mode with **no uptime investment** (decided in the integration-readiness grill): if the machine sleeps or the process dies, the loop just stops (kill-switch semantics) and you restart + re-arm manually. The gate clock honestly pauses during downtime — note any such gaps in the weekly review file.

## 2. Control surface (localhost REST)

| Action | Command (`curl.exe` — PowerShell's `curl` alias has no `-u`) | Effect |
|---|---|---|
| Pause entries (exits keep managed) | `POST /pause` | blocks new entries; resets on restart |
| Full stop | `POST /stop` | halts loop; with `cancel_open_orders_on_exit` cancels unfilled orders |
| Force-exit a trade | `POST /forceexit` | exits open trade immediately |
| List/add/delete locks | `GET/POST/DELETE /locks` | manual entry-ban; persists in the DB |

Aliases: `/stopentry` ≡ `/stopbuy` ≡ `/pause`. There is **no** `/stopexit`.

**External kill switch** = stop the process (`Ctrl+C`; SIGTERM takes the same shutdown path). Open positions are never force-exited on shutdown; they survive in the DB and are picked up after the next start + re-arm.

**Graceful unwind** (freqtrade docs pattern): `/pause` → let open trade close by signal/stoploss or `/forceexit` → `/stop`.

## 3. Interventions policy

Allowed: **pause entries, force-exit, full stop, manual locks**.
Forbidden: **force-entering trades, editing the dry-run DB** — both poison attribution.

Every manual action gets one line in `docs/interventions.md`: date · action · command · reason · bot state.

## 4. Weekly review (gate evidence)

Record the output in **`docs/reviews/weekly-NNNN.md`** — one file per week, then anomalies and the eventual gate verdict (verdict lives in week 2's file, linked from `docs/interventions.md`). Refresh the feather store manually whenever a backtest is needed during the gate (re-run the `download-data` command — no scheduling).

Trade export for reports: `uv run freqtrade show-trades --db-url sqlite:///bot/tradesv3.dryrun.sqlite` (or `--print-json` for export).

SQL against the dry-run DB (open in any SQLite tool; inspect table names with `SELECT name FROM sqlite_master WHERE type='table';`):

- All closed trades: `SELECT id, pair, open_date, close_date, close_profit, close_profit_abs, exit_reason FROM trades WHERE is_open=0 ORDER BY close_date;`
- Stoploss-family exits: `SELECT * FROM trades WHERE exit_reason LIKE '%stop%';`
- Protection locks fired: inspect the `pair_locks`-equivalent table by lock reason (`Auto lock` = the always-on 1-candle lock; named locks = protections).
- Errors: scan `bot/bot.log` for `ERROR`/`WARNING` in the review window.

## 5. Gate to v0.2 (from the map)

Dry-run ends (and v0.2 model work unlocks) only when **all** hold:

1. ≥2 weeks in dry-run (dev mode: downtime gaps noted per week; a strict-continuous requirement, if ever disputed, applies only to a post-realism-upgrade run),
2. ≥30 closed trades,
3. incident review clean: no unexplained restarts/crashes in the final week.

Record the gate verdict in `docs/interventions.md` with the numbers.

## 6. Realism upgrade — strictly AFTER the gate (one explicit step)

1. Create a Bybit **demo account** + demo funds on Bybit's demo page.
2. Create **demo-scoped API keys** there.
3. New config overlay: `"exchange": {"name": "bybit", "demo_trading": true, "api_key": ..., "secret": ...}` with `"dry_run": false` (the two are incompatible — verified).
4. Fresh database file (`dry-run trades must not taint stats`) via a new `db_url`.
5. Run in demo mode until the next evidence gate. The **real-money** switch (fresh DB, `dry_run: false`, real keys with no-withdrawal permissions, IP restriction, dedicated subaccount) is a separate future effort with its own verified checklist in the map's Decisions.

## 7. First-run smoke checklist

- [ ] `install-ui` done, freqUI reachable on `127.0.0.1:8080` after start
- [ ] `download-data` populated `bot/user_data/data/bybit/` with feather files
- [ ] `recursive-analysis` variance ≈ 0%
- [ ] `trade` starts without configuration errors
- [ ] `/ping` answers; `/start` re-arms; a golden-cross entry (or lock) eventually appears in freqUI
- [ ] `Ctrl+C` kills cleanly; restart boots STOPPED; re-arm works

## 8. v0.2 cutover (post-gate — `bot/config-v02.json`)

1. Record the v0.1 gate verdict in `docs/reviews/` and `docs/interventions.md`.
2. Stop the v0.1 process; the dry-run DB stays as the historical record.
3. Set `ALPHAVANTAGE_API_KEY` in the environment (news features need the archive; CryptoPanic `auth_token` optional later).
4. Start v0.2: `uv run freqtrade trade --config bot/config-v02.json --config bot/config-private.json --logfile bot/bot-v02.log`, re-arm via REST as usual.
5. News self-archive grows under `bot/user_data/news/av/`; features only exist from archive start — expect the classifier to train without news signal depth for the first ~3 weeks (train_period_days 30 vs archive age); that gap is a known limitation, noted in the weekly reviews.
6. The **same gate criteria re-apply to the v0.2 dry-run** (≥2 weeks, ≥30 trades, clean incident review) before any realism upgrade.
7. Backtest validation command: `uv run freqtrade backtesting --config bot/config-v02.json --freqaimodel LightGBMClassifier --timerange <range> --enable-protections`.
