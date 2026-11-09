# Spec: agent v0.1 — freqtrade dry-run build

**Status:** build-ready (2026-11-09). Source of truth: the map in this directory (`map.md`, Decisions so far) + `research/` scans. User pre-authorized the TDD build; no separate review gate.

## 1. Mission recap

Autonomous crypto trading agent: **BTC/USDT spot on Bybit, 1h candles, paper-first (freqtrade `dry_run`), Python, long-only, one open trade, fixed stake, decision logic simple-but-cited in v0.1 with the ML/model phase deferred to v0.2**. See `MISSION.md` and the map's Decisions so far for every "why".

## 2. Artifacts & repo layout

```
bot/
  config.json                    # public run config (tracked)
  config-private.example.json    # template for the private overlay (tracked); real file gitignored
  user_data/
    strategies/EmaCrossBaseline.py
    data/                        # feather OHLCV store (gitignored)
  tradesv3.dryrun.sqlite         # runtime dry-run DB (gitignored)
  tests/
    test_ema_cross_baseline.py   # seam: signal logic + rails
    test_config.py               # seam: config validation
docs/playbook.md                 # runbook, gate, REST commands, weekly review, realism upgrade
docs/interventions.md            # manual-intervention log (append-only)
.gitignore
```

All commands run from the **repo root**.

## 3. Config design

`bot/config.json` (public — nothing secret in it):

| Key | Value | Why |
|---|---|---|
| `max_open_trades` | `1` | attribution (map: execution & sizing) |
| `stake_currency` / `stake_amount` | `USDT` / `250` | fixed 250 USDT stake (map) |
| `dry_run` / `dry_run_wallet` | `true` / `1000` | paper-first (map) |
| `db_url` | `sqlite:///bot/tradesv3.dryrun.sqlite` | explicit runtime DB location |
| `cancel_open_orders_on_exit` | `true` | kill switch (map: risk rails) |
| `dataformat_ohlcv` | `feather` | data-pipeline decision (map) |
| `trading_mode` | `spot` | spot-only v0.1 |
| `exchange.name` | `bybit` | venue decision (map) |
| `exchange.pair_whitelist` | `["BTC/USDT"]` | single pair (map) |
| `pairlists` | `[{"method": "StaticPairList"}]` | static single-pair default made explicit |
| `order_types` | entry/exit `market` | market orders both sides (map) |
| `entry_pricing` / `exit_pricing` | freqtrade sample defaults | required blocks; market orders make them near-moot |
| `unfilledtimeout` | `{entry: 10, exit: 10, exit_timeout_count: 0, unit: "minutes"}` | sample defaults |
| `strategy` / `user_data_dir` | `EmaCrossBaseline` / `bot/user_data` | runbook needs no `--strategy` flag |
| `bot_name` | `data-agent v0.1` | identification in freqUI |

Deliberately **absent from the public config**:

- `api_server` — lives in `config-private.json` (overlay merged via a second `--config`; creds are local-only secrets). Template tracked as `config-private.example.json` with `CHANGE_ME` placeholders. Real file created from the template is **gitignored**.
- `initial_state` — omitted on purpose: freqtrade boots `STOPPED` when unset; the human **re-arms** with `/start` (map: risk rails re-arm).
- `timeframe` — owned by the strategy (`"1h"`); no double declaration.
- `stoploss` — owned by the strategy; config must **not** override (single source of truth).

## 4. Strategy design: `EmaCrossBaseline`

freqtrade strategy class (interface v3), per the trigger decision (map) + `research/trigger-strategy-baseline.md`:

- `timeframe = "1h"`, `can_short = False`, `process_only_new_candles = True`, `use_exit_signal = True`, `exit_profit_only = False`, `ignore_roi_if_entry_signal = False`, `INTERFACE_VERSION = 3`
- `minimal_roi = {}` (ROI disabled — documented disable; exits = signals/rails only)
- `stoploss = -0.05` (bot-managed; Bybit spot has no exchange-side stoploss)
- `startup_candle_count = 100` (~4× slow EMA; confirm with `freqtrade recursive-analysis` before first dry-run — playbook)
- `@property protections`: the three decided rails, candle units:
  - `CooldownPeriod`: `stop_duration_candles: 2`
  - `StoplossGuard`: `lookback_period_candles: 24, trade_limit: 2, stop_duration_candles: 4, required_profit: 0.0, only_per_pair: False`
  - `MaxDrawdown`: `calculation_mode: "equity", lookback_period_candles: 168, trade_limit: 5, max_allowed_drawdown: 0.2, stop_duration_candles: 24`
- `populate_indicators`: `ema_fast = ta.EMA(close, 12)`, `ema_slow = ta.EMA(close, 26)`
- `populate_entry_trend`: `enter_long = 1` where `qtpylib.crossed_above(ema_fast, ema_slow)` and `volume > 0` (golden cross)
- `populate_exit_trend`: `exit_long = 1` where `qtpylib.crossed_below(ema_fast, ema_slow)` and `volume > 0` (death cross)
- Execution semantics: signals computed on the **closed** candle; trade executes at the **next candle open**.

**Seam for v0.2:** the model phase replaces only the two `populate_*_trend` bodies (or the signal columns) — same `enter_long`/`exit_long` contract, same rails, same config. Everything else must not churn.

## 5. Evaluate & reporting

- Baseline record: dry-run SQLite DB (`bot/tradesv3.dryrun.sqlite`) + trade export (`freqtrade show-trades`).
- Human channel: **freqUI** served by the already-enabled localhost REST API (`freqtrade install-ui` once, then open `http://127.0.0.1:8080`).
- REST surface (localhost only): `GET /ping`, `POST /start` (re-arm), `POST /pause` (≡ `/stopentry` — blocks entries, keeps managing exits), `POST /stop` (full halt), `POST /forceexit`, `GET/POST/DELETE /locks`. No `/stopexit` exists.
- Telegram: out of scope for v0.1 (fog — revisit with VPS ops).

## 6. Data pipeline

- Download/refresh: `freqtrade download-data -c bot/config.json --timeframes 1h --timerange <start>-` into the feather store under `bot/user_data/data/`. Public OHLCV needs no API keys.
- Backtesting/study/hyperopt read the same store. **No custom data layer in v0.1.**

## 7. Playbook

Lives in `docs/playbook.md` (full runbook). Anchors:

- **Start**: `freqtrade trade --config bot/config.json --config bot/config-private.json --logfile bot/bot.log`, then re-arm: `POST /start`.
- **Kill switch**: process stop (`Ctrl+C`/SIGTERM) with `cancel_open_orders_on_exit: true`; open positions never force-exit; restart boots `STOPPED`; re-arm via `/start`.
- **Graceful unwind** (docs pattern): `/pause` → manage/force-exit → `/stop`.
- **Gate to v0.2**: ≥2 weeks continuous dry-run AND ≥30 closed trades AND incident review (no unexplained restarts in the final week). Realism upgrade (dry-run → Bybit demo-wallet `demo_trading: true` with demo-scoped keys, fresh DB note) only **after** the gate, as one explicit step. Real-money switch is a separate future effort with its own verified procedure (map: playbook decision).
- **Interventions log**: `docs/interventions.md` — one append per manual action (date, action, command, reason, bot state).
- **Weekly review**: documented SQL/`freqtrade show-trades` queries (closed trades, stoploss-family exits, pair locks, errors).

## 8. TDD plan — pre-agreed seams

Tooling: **pytest** in the uv-managed environment (`uv sync` from root; `uv run pytest bot/tests -q` — freqtrade, TA-Lib, pandas all inside `uv.lock`). Lint/typecheck: **ruff** (same env; `uv run ruff check bot`) — mypy not configured on this machine; reported in the build summary.

Tests (red → green, in order):

- **T1 indicators** — `ema_fast`/`ema_slow` equal a pandas EWM reference (`span=12`/`26`, `adjust=False`) on synthetic candles.
- **T2 entry** — synthetic price ramp produces `enter_long = 1` on exactly the golden-cross candle.
- **T3 exit** — reverse ramp produces `exit_long = 1` on exactly the death-cross candle.
- **T4 neutrality** — no cross ⇒ no signals anywhere.
- **T5 rails static** — stoploss `-0.05`, `minimal_roi == {}`, `can_short False`, `timeframe "1h"`, `INTERFACE_VERSION 3`, `process_only_new_candles True`, exit triple `True/False/False`, `startup_candle_count >= 26`.
- **T6 protections property** — exactly the three rails, in order, with the decided params incl. `equity` mode; config is not a carrier of protections.
- **T7 public config** — `bot/config.json` validates against freqtrade's schema and carries every decided key; no `api_server`, no `timeframe`, no `stoploss`, no `initial_state`.
- **T8 private overlay** — `config-private.example.json` (placeholders filled) merges cleanly with the public config and the merged dict validates; the real `config-private.json` must not exist in git.

## 9. Acceptance criteria

1. Full pytest suite green (T1–T8).
2. `freqtrade list-strategies` resolves `EmaCrossBaseline` from `bot/config.json`.
3. `freqtrade validate-config`(schema) passes for the public config and the merged overlay.
4. Code review (skill) passes; work committed to `master`.
5. First-run smoke (playbook checklist) is a manual step for the user: `install-ui`, `recursive-analysis`, `download-data`, then start + re-arm.

Evidence recorded in-build (2026-11-09): criterion 2 (`list-strategies` → `EmaCrossBaseline | OK`), criterion 3 (schema validation via T7/T8), lint (`ruff check bot` clean; `RUF012` scoped off for freqtrade's class-attribute convention in `ruff.toml`). Typechecking beyond ruff: none configured on this machine (mypy absent; report to user in the build summary).

## 10. Build amendments (2026-11-09, discovered during the TDD build)

1. **Import surface**: `freqtrade.vendor.qtpylib.indicators` is **deprecated in 2026.10** ("will be removed; import from `technical` instead") — signals use `from technical.qtpylib import crossed_above, crossed_below`. The trigger-research snippet's vendor import is doc-lag.
2. **`order_types` schema**: freqtrade requires `stoploss` + `stoploss_on_exchange` keys when the block is declared — config carries `"stoploss": "market"` (simulated in dry-run) and `"stoploss_on_exchange": false` (Bybit spot has none).
3. **Market-order pricing rule**: freqtrade validation rejects market entry with `entry_pricing.price_side = "same"` — both pricing blocks use `price_side: "other"` (fill against the opposite book side). Locked by test.
4. **TA-Lib EMA warm-up**: ta-Lib's EMA yields NaN for the first `timeperiod-1` candles; the pandas-ewm reference equality holds from that index onward (locked by test).
5. **Environment (2026-11-09, user-directed)**: dependencies are contained in **uv** — root `pyproject.toml` (main: `freqtrade>=2026.10`; dev group: `pytest`, `ruff`) + `uv.lock` + `.venv` (gitignored). One-time `uv sync`; every build/run command gets the `uv run` prefix (`uv run pytest bot/tests -q`, `uv run ruff check bot`, `uv run freqtrade ...`). The playbook's commands already reflect this.
