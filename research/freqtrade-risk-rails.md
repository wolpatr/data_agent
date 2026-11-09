# Risk rails fact-finding — freqtrade protections & kill switches (Bybit spot, dry-run v0.1)

**Date:** 2026-11-09
**Scope:** freqtrade stable docs (https://www.freqtrade.io/en/stable/) cross-checked against freqtrade develop source (`api_trading.py`, `worker.py`, `freqtradebot.py`, `pairlock*.py`, protection classes, `config_schema.py`, `deprecated_settings.py`) to resolve naming and default questions. Target: BTC/USDT Bybit spot, dry-run, 1h candles, `max_open_trades: 1`, `stake_amount: 250`.

---

## 1. `stoploss` mechanics

- `stoploss` is a **ratio, expressed as a negative number**: `stoploss = -0.10` means "exit when trade profit dips below -10%". Simplified math from docs: buy at 100, stoploss -10%, triggers when price < 90. **Stoploss calculations include fees** — a -10% stoploss is placed exactly 10% below the entry point (fee-adjusted).
  - Verified — https://www.freqtrade.io/en/stable/stoploss/
- Config values **override** strategy values; `stoploss` is a [Strategy Override] parameter and is **mandatory**. Config schema requires `stoploss < 0` (`maximum: 0, exclusiveMaximum`) — a value of 0 raises `ConfigurationError` ("stoploss needs to be different from 0 to avoid problems with sell orders").
  - Verified — https://www.freqtrade.io/en/stable/configuration/ and develop source `freqtrade/config_schema/config_schema.py`, `freqtrade/configuration/config_validation.py`
- **Dry-run stoploss is fully bot-managed (simulated)**: no orders are sent to the exchange; the bot loop (default `internals.process_throttle_secs = 5`, aligned to candle boundary +1s) evaluates stop/trailing in code and creates a simulated market/limit order per `order_types.stoploss`. Source confirms dry-run never touches exchange orders for updates: `startup_update_open_orders()` returns early in dry-run ("Updating open orders in dry-run does not make sense and will fail").
  - Verified — develop source `freqtrade/freqtradebot.py`; https://www.freqtrade.io/en/stable/configuration/ (dry-run)
- **`stoploss_on_exchange` support matrix** (docs table, "Supported exchanges"):
  - **Bybit spot: ❌ (not available)**
  - Bybit futures (isolated margin): market + limit
  - Same table appears in both the stoploss page and the exchange notes page; exchange notes additionally state: "Bybit (futures only) supports `stoploss_on_exchange` and uses `stop-loss-limit` orders… On futures, Bybit supports both `stop-limit` as well as `stop-market` orders."
  - Verified — https://www.freqtrade.io/en/stable/stoploss/ and https://www.freqtrade.io/en/stable/exchanges/
- Default `order_types.stoploss = "limit"`, `stoploss_on_exchange = False` (IStrategy defaults); `stoploss_on_exchange_interval` (default 60s) and `stoploss_price_type` are only relevant where stoploss-on-exchange is supported (futures-only for Bybit).
  - Verified — https://www.freqtrade.io/en/stable/stoploss/

## 2. `trailing_stop` family

- `trailing_stop = True` builds **on top of `stoploss`** — it is *not* mutually exclusive with it (docs: "Enables trailing stoploss (based on `stoploss` in either configuration or strategy file)"), and "The initial value for this is `stoploss`, just as you would define your static Stop loss". The trailing stop is kept at `-stoploss` below the **highest observed price** (buy 100 → stops at 90 → price 102 → stop now 91.8, never lowered).
  - Verified — https://www.freqtrade.io/en/stable/stoploss/ and https://www.freqtrade.io/en/stable/configuration/ (parameters table)
- `trailing_stop_positive` (float, e.g. `0.02` = -2%): once profit reaches the offset, a **new, tighter trailing stop** value is used; before that the base `stoploss` is used. Base config: `stoploss: -0.10, trailing_stop: True, trailing_stop_positive: 0.02`.
- `trailing_stop_positive_offset` (default `0.0`, positive float): profit ratio at which `trailing_stop_positive` takes over. Docs tip: keep the offset **lower than minimal ROI**, otherwise minimal ROI exits first.
- `trailing_only_offset_is_reached` (default `False`): `True` = static stoploss until the offset is reached, then trail with `trailing_stop_positive` (which may be omitted; offset alone activates trailing with the base value).
- Startup validation rules (source, `config_validation.py`):
  - `stoploss == 0` → error (always, trailing or not)
  - `trailing_stop_positive == 0` if set → error
  - if `trailing_stop_positive > 0` then `trailing_stop_positive_offset` must be **>` `trailing_stop_positive`
  - `trailing_only_offset_is_reached` requires `trailing_stop_positive_offset > 0`
- Limitation: a stoploss on an open trade cannot be changed via `/reload_config` once trailing has already adjusted it.
  - Verified — https://www.freqtrade.io/en/stable/stoploss/ + develop source

```python
# Strategy-side rails example (strategy is the only place protections can live since 2024.10)
stoploss = -0.10
trailing_stop = True
trailing_stop_positive = 0.02
trailing_stop_positive_offset = 0.03
trailing_only_offset_is_reached = True
```

## 3. Protection plugins — structure, parameters, defaults

**Where protections live:** config-level `"protections": [...]` was **removed** — it now raises `ConfigurationError("DEPRECATED: Setting 'protections' in the configuration is deprecated.")`. The deprecated-features page: "Setting protections from the configuration via `\"protections\": [],` has been **removed in 2024.10**, after having raised deprecation warnings for over 3 years." Protections can **only** be defined in the strategy (attribute or `@property def protections`).
- Verified — https://www.freqtrade.io/en/stable/deprecated/#removal-of-protections-from-configuration; develop source `freqtrade/configuration/deprecated_settings.py` (also: neither the config JSON schema nor `StrategyResolver` maps a `protections` config key)

The JSON *structure* is unchanged (a list of dicts) — it simply lives in the strategy:

```python
@property
def protections(self):
    return [
        {
            "method": "CooldownPeriod",
            "stop_duration_candles": 5
        },
        {
            "method": "MaxDrawdown",
            "calculation_mode": "equity",
            "lookback_period_candles": 48,
            "trade_limit": 20,
            "stop_duration_candles": 12,
            "max_allowed_drawdown": 0.2
        },
        {
            "method": "StoplossGuard",
            "lookback_period_candles": 24,
            "trade_limit": 4,
            "stop_duration_candles": 4,
            "required_profit": 0.0,
            "only_per_pair": False,
            "only_per_side": False
        },
        {
            "method": "LowProfitPairs",
            "lookback_period_candles": 6,
            "trade_limit": 2,
            "stop_duration": 60,      # minutes variant allowed
            "required_profit": 0.02
        },
    ]
```

**Common settings (docs table + IProtection source):**

| Parameter | Meaning | Default (when omitted) | Mutually exclusive with |
|---|---|---|---|
| `method` | one of `StoplossGuard`, `MaxDrawdown`, `LowProfitPairs`, `CooldownPeriod` | — | — |
| `stop_duration` / `stop_duration_candles` | lock length in **minutes** (float) / **candles** (int) | `stop_duration` = 60 min if neither is set | each other, and `unlock_at` (hard `ConfigurationError`) |
| `lookback_period` / `lookback_period_candles` | window of closed trades considered, minutes / candles | `lookback_period` = 60 min if neither set | each other (hard `ConfigurationError`) |
| `trade_limit` | minimum number of trades required for the protection to evaluate | per-protection (see below) | — |
| `unlock_at` | `"HH:MM"` — unlock daily at fixed time instead of fixed duration | — | `stop_duration*` |

- Candle variants exist and are the docs' recommended style ("all below examples will use the 'candle' definition"); both are converted to minutes internally via the bot timeframe (1h → `lookback_period_candles: 24` = 1440 min). Lock **end times are rounded up to the next candle** (`PairLocks.lock_pair` → `timeframe_to_next_date`) to avoid intra-candle entries.
- Verified — https://www.freqtrade.io/en/stable/plugins/#protections + develop source `freqtrade/plugins/protections/iprotection.py`, `freqtrade/persistence/pairlock_middleware.py`

**StoplossGuard** (global + per-pair capable; `has_global_stop=True`, `has_local_stop=True`, source):
- Counts closed trades within lookback whose exit reason is `"stop_loss"`, `"stoploss_on_exchange"`, `"trailing_stop_loss"` (plus `LIQUIDATION`, futures-only) **with profit < `required_profit`** (default `0.0` → only losing stoplosses count). If ≥ `trade_limit` such trades → trading stops for `stop_duration` after the **last trade's close date**.
- Defaults (source): `trade_limit: 10`, `required_profit: 0.0`, `only_per_pair: False`, `only_per_side: False`.
- `only_per_pair: true` → evaluate on that pair's trades only and *disables the global stop* (source stores it as `_disable_global_stop`).
- `only_per_side: true` ("for futures bots") → only trades on the triggered side count, and only that side (`long`/`short`) is locked. On a spot long-only bot this has no effect.
- Verified — https://www.freqtrade.io/en/stable/plugins/#stoploss-guard + develop source `stoploss_guard.py`

**MaxDrawdown** (**global-only**; `has_local_stop=False` in source; no `only_per_pair` exists for it):
- Evaluates **closed** trades within the lookback window; needs ≥ `trade_limit` (default `1`).
- `max_allowed_drawdown` (default `0.0`, ratio 0.2 = 20%): if observed drawdown **exceeds** it, all-pairs (`*`) lock for `stop_duration` after the last trade.
- `calculation_mode` (new; default `"ratios"`):
  - `"ratios"` (legacy, default): drawdown derived from cumulative trade profit **ratios** (`close_profit`); can differ from account-level drawdown when position sizing changes over time.
  - `"equity"` (docs-recommended): standard peak-to-trough drawdown on the **equity curve**, using starting balance + cumulative *absolute* profit (source uses `wallets.get_starting_balance()` and all closed trades' `close_profit_abs`).
  - "With fixed stake amount configurations, ratio-based behavior is easier to reason about" — with v0.1's fixed 250 USDT stake the two modes are close, but they are not identical metrics.
- Verified — https://www.freqtrade.io/en/stable/plugins/#maxdrawdown + develop source `max_drawdown_protection.py`

**LowProfitPairs** (pair-level only; no global stop, source):
- Sum of `close_profit` over ≥ `trade_limit` (default `1`) closed trades of a pair within the lookback < `required_profit` (default `0.0`) → lock that pair for `stop_duration`. `only_per_side` applies (futures).
- Verified — https://www.freqtrade.io/en/stable/plugins/#low-profit-pairs + develop source `low_profit_pairs.py`

**CooldownPeriod** (pair-level only; never locks globally — docs note):
- Locks a pair for `stop_duration` after an exit, "avoiding a re-entry"; **ignores `lookback_period`** (docs: "does not consider lookback_period as it only looks at the latest trade"). No `trade_limit`. Source: considers closed trades within lookback and locks from the max close_date + stop_duration.
- Verified — https://www.freqtrade.io/en/stable/plugins/#cooldown-period + develop source `cooldown_period.py`

- `max_retries` is **not** a protection parameter in any current docs or source (unrelated existing knob: `unfilledtimeout.exit_timeout_count`, repeat-exit-order handling). Verified by inspection of all four protection sources + docs.
- All protections are evaluated **in the sequence defined**, in `handle_protections()`, which runs **after each trade close** (including stoploss exits); additionally **every** closed trade gets an automatic 1-candle pair lock (reason `"Auto lock"`) before protections are evaluated.
- Backtesting/hyperopt support requires `--enable-protections`.
- Docs quirk: the "Full example of Protections" LowProfitPairs entry shows `"stop_duration_candles": 60` (= 60 **hours**) where the individual example and accompanying prose use `"stop_duration": 60` (60 **minutes**) — treat the full example's units with caution.
- Verified — https://www.freqtrade.io/en/stable/plugins/ (both snapshots), source `freqtradebot.py`

## 4. Protection lock semantics + REST/Telegram kill switches

- Protections create **`PairLock` records** — `{pair, side ('long'|'short'|'*'), reason, lock_time, lock_end_time, active}`. Global locks are `pair = "*"`; per-pair locks use the pair name. Stored in the **database** in dry-run/live (`PairLocks.use_db = True`; sqlite default `sqlite:///tradesv3.dryrun.sqlite` in dry-run) — and therefore **survive process restarts** until `lock_end_time` passes (queries filter `lock_end_time > now AND active = true`). Backtesting uses in-memory locks only. Locks are also created manually via REST/Telegram and are equally persistent. Deleting/resetting the dry-run database clears them.
  - Verified — develop source `freqtrade/persistence/pairlock.py`, `pairlock_middleware.py`; https://www.freqtrade.io/en/stable/faq/ ("I want to reset the bot's database")
- Locks **block new entries only, never exits**: `enter_positions()` bails on any global lock (`PairLocks.is_global_lock(side="*")`), `create_trade()` checks `strategy.is_pair_locked(pair, candle_date, side=signal)`; the exit paths check no locks. A per-side (`long`/`short`) lock blocks entries for that side only.
  - Verified — develop source `freqtradebot.py`, `interaction interface.py`
- REST endpoints (source `api_trading.py` is definitive; the stable REST docs table matches for /locks, /stop, /pause, /stopbuy):
  - `GET /locks` — list current locks; `POST /locks` — add lock(s) (`{pair, until, side?, reason?}`, `until` rounded up to the next timeframe; docs say `side` defaults to `long`); `DELETE /locks/{lockid}`; `POST /locks/delete` (by lockid/pair).
  - `POST /stop` — "Stops the trader" → state `STOPPED`: the trader loop halts entirely (no entries **and** no exit processing; open trades are left open in the DB).
  - `POST /pause` — "Gracefully handle open trades according to their rules. Do not enter new positions." → state `PAUSED`: open trades continue to be managed (ROI/exit signals/stoploss still active); position adjustment remains active but exit-side only.
  - **`/stopentry` and `/stopbuy` are the same endpoint as `/pause`** — source stacks three routes on one handler (`@router.post("/pause") @router.post("/stopentry") @router.post("/stopbuy")` → `_rpc_pause()`). Telegram docs likewise document "`/pause | /stopentry | /stopbuy`" as one command. The stable REST page's table still lists only `/stopbuy` + `/pause` — docs lag, not a behavior difference.
  - There is **no `/stopexit`** endpoint (nothing stops exits alone; `/forceexit` is the per-trade exit tool). Verified against the full route set in `api_trading.py`.
  - Persistent state vs not: `/pause`/`/stopentry` and `/stop` set **in-memory bot state, not persisted** — docs say explicitly for pause/stopentry: "The pause/stopentry signal is ONLY active while the bot is running, and is not persisted anyway, so restarting the bot will cause this to reset." After a process restart, `initial_state` governs: the config schema has **no default** and the bot falls back to `State.STOPPED` when unset (idle until `/start`); the freqtrade config wizard template explicitly writes `"initial_state": "running"`. So a hand-written config without `initial_state` boots idle; with `"initial_state": "paused"` the bot boots without entries but manages open trades.
  - Telegram mirrors: `/locks`, `/unlock <pair or lock_id>`, `/start`, `/stop`, `/pause|/stopentry|/stopbuy`.
  - Verified — https://www.freqtrade.io/en/stable/rest-api/ , https://www.freqtrade.io/en/stable/telegram-usage/ , develop source `api_trading.py`, `freqtradebot.py`, `config_schema.py`, `templates/base_config.json.j2`

## 5. `cancel_open_orders_on_exit` and shutdown semantics

- Parameter (default `false`): "Cancel open orders when the `/stop` RPC command is issued, `Ctrl+C` is pressed or the bot dies unexpectedly. When set to `true`, this allows you to use `/stop` to cancel unfilled and partially filled orders in the event of a market crash. **It does not impact open positions.**"
  - Verified — https://www.freqtrade.io/en/stable/configuration/
- Signal handling: the trading entrypoint registers a `SIGTERM` handler that raises `KeyboardInterrupt`, so **SIGINT (Ctrl+C) and SIGTERM take the same path**: worker loop unwinds → `worker.exit()` → `FreqtradeBot.cleanup()`:
  - if `cancel_open_orders_on_exit`: `cancel_all_open_orders()` (unfilled/partial orders are cancelled — in dry-run these are simulated orders)
  - always (even with the flag off): `check_for_open_trades()` → warning: "`<N>` open trades active. Handle these trades manually on <exchange>, or `/start` the bot again and use `/stopentry` to handle open trades gracefully." (+ "Note: Trades are simulated (dry run)." in dry-run).
  - While in `STOPPED` state the loop only calls `process_stopped()`, which **also** repeatedly cancels open orders when the flag is set.
- **Freqtrade never force-exits open positions on shutdown.** There is no auto-`forceexit` at shutdown; open positions are held in place in the trade database (with `cancel_open_orders_on_exit=false` even unfilled orders survive and are picked up on restart; startup calls `Trade.stoploss_reinitialization` to apply the current stoploss to open trades and re-syncs orders where possible — live only; skipped in dry-run). The graceful unwind pattern the docs push is: `/stopentry` → wait for `/forceexit all` via ROI/signals or explicit force exit → then `/stop`.
  - Verified — develop source `freqtrade/commands/trade_commands.py`, `freqtrade/worker.py`, `freqtradebot.py` (`cleanup`, `process_stopped`, `check_for_open_trades`, `startup`); https://www.freqtrade.io/en/stable/faq/ ("only Exit the trades being held…")

## 6. Interaction with `max_open_trades = 1` / single pair

- With a single-pair whitelist and `max_open_trades: 1`, *per-pair and global are the same scope*: `StoplossGuard` with `only_per_pair: true` evaluates exactly the trades a global `StoplossGuard` would. `MaxDrawdown` is global-only anyway; `CooldownPeriod`/`LowProfitPairs` are pair-level anyway.
- Static `stake_amount` caps engaged capital at `stake_amount × max_open_trades` = 250 USDT (docs: "The maximum capital engaged in trades is `stake_amount * max_open_trades`"; respects `tradable_balance_ratio`).
- Protections do **not** close the open trade: with 1 slot, the sole slot can be occupied by a live loser while every protection is in force — the only mechanism that closes it is the stoploss (or ROI/exit signal/force exit). Protections will simply keep the slot from being refilled after it frees up.
- Verified — https://www.freqtrade.io/en/stable/configuration/ (Static stake amount) + source

## 7. Realized vs unrealized drawdown; wallet interplay

- `MaxDrawdown` uses **closed trades only** (source: `Trade.get_trades_proxy(is_open=False, close_date=…)`) — it is a **realized** drawdown metric. Unrealized (floating) P&L of the currently open trade is invisible to it (same for `StoplossGuard`/`LowProfitPairs` — all operate on `is_open=False`). For a `max_open_trades=1` bot mid-drawdown, the running loss is bounded only by `stoploss`; MaxDrawdown reacts only *after* the loss has been realized.
- `calculation_mode: "equity"` baseline is "starting balance + cumulative absolute profit before the window" (source passes `wallets.get_starting_balance()`), i.e. the dry-run wallet trajectory — `dry_run_wallet` (default `1000`) seeds the wallet, `tradable_balance_ratio` (default `0.99`) only trims what's tradable; both indirectly define the equity curve the protection measures, but no protection reads wallet balance directly except as that baseline.
- Verified — develop source `max_drawdown_protection.py`, `freqtradebot.py` (`handle_protections`), https://www.freqtrade.io/en/stable/plugins/#maxdrawdown , https://www.freqtrade.io/en/stable/configuration/ (dry-run wallet / tradable balance)

---

## Docs-version notes / contradictions found

- **Config-level `"protections"`**: removed in **2024.10** (hard error since). Older configs and older third-party write-ups that show a config `"protections"` section will now fail startup.
- **`MaxDrawdown.calculation_mode`**: current stable docs document `"ratios"` (default) + `"equity"` (recommended). The **2024.10** docs snapshot has no `calculation_mode` at all — older guides describe ratio-based behavior only.
- **`/stopentry`**: exists as a REST route (source, develop), aliased to `/pause` along with `/stopbuy`, but the **stable REST docs table still only lists `/stopbuy` and `/pause`** — trailing docs, not behavior difference. Telegram docs list all three aliases.
- Old (2024.10) plugins page contained the wording bug "If the drawdown is **below** `max_allowed_drawdown`, trading will stop…"; current stable correctly says "**exceeds**".
- `initial_state`: docs table says "Defaults to `stopped`" — matches source fallback (no schema default; `State.STOPPED` when unset). Not a contradiction, but a practical gotcha: the config wizard writes `"initial_state": "running"` for you; hand-rolled configs must set it.

## Design implications for v0.1

- Protections must be declared **in the strategy file** (config-level is now rejected); the strategy is the single carrier of both the stoploss/trailing rails and the protection rails.
- Bybit spot has **no exchange-side stoploss** (futures-only on Bybit); in dry-run this is moot (everything is bot-simulated anyway), but any future live spot build accepts a gap/crash risk equal to the bot loop interval (~5 s polling, candle-aligned).
- Trailing stop requires a negative base `stoploss` and has strict validation ordering (`offset > positive`, `positive ≠ 0`); with `trailing_only_offset_is_reached` the base stoploss stays the disaster brake until offset.
- All protection entry-blocking is **entries-only** — an open loser keeps its trade slot; the stoploss is the only in-trade risk bound.
- `MaxDrawdown` is realized-only; with `max_open_trades=1` a single open position's floating loss is unbounded except by the stoploss. Equity vs ratios mode differ mildly under fixed 250 USDT stake; current docs recommend `equity` for new setups and it becomes the default-equivalent anchor only via the `wallets.get_starting_balance()` baseline.
- Every closed trade is already auto-locked for one candle ("Auto lock"); a visible `CooldownPeriod` of >1 candle is needed if a longer post-exit pause is desired.
- Locks are DB-persisted and survive restarts (dry-run sqlite); `/stop` and `/pause`/`/stopentry` do not survive — restart behavior is governed by `initial_state` (unset → idle `stopped`; set `"running"` for an autonomous v0.1 service).
- Kill-switch surface available to the harness over REST: `POST /stopentry` (a.k.a. `/pause`, `/stopbuy`) for no-new-entries, `POST /stop` for full halt, `POST /locks` for scoped timed locks, `POST /forceexit` for explicit unwind; `cancel_open_orders_on_exit: true` makes `/stop`/SIGINT/SIGTERM also cancel unfilled orders while never touching open positions.
- Durations can be expressed in candles (`*_candles`) which is the cleaner unit for the 1h timeframe; mixing candle+minute variants for the same dimension (or `unlock_at` + durations) is a hard startup error.
- StoplossGuard counts trailing-stop and (futures-only) liquidation exits too; `required_profit: 0.0` (only losing stoplosses) is the default and docs-recommended value.
