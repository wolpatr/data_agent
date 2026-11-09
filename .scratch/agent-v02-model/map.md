---
labels: wayfinder:map
---

# Map: v0.2 — multi-source ML Decide on the live harness

## Destination

A **build-ready v0.2 spec**: multi-source, multi-pair crypto agent on the existing freqtrade harness — ML classifier Decide (walk-forward-disciplined) consuming market + news inputs across a small static USDT pair set; integrated only after the v0.1 gate. Same rules as v0.1: decisions-in-map, **no production code in map sessions**; order of attack: data/features first, sophistication only through walk-forward evidence.

## Notes

- **Session rules** (same solo map-only override as v0.1): one decision per session, top-first, unless the user names one; grilling + domain-modeling by default; research runs as subagents with findings under `research/` at repo root.
- **Ground truth**: `MISSION.md`, `RESOURCES.md`, and `.scratch/agent-v01-spec/map.md` (the v0.1 decisions carry into here unchanged; this redraw was user-declared 2026-11-09 — "restart the plan, not the build").
- **Harness status**: v0.1 dry-run LIVE since 2026-11-09 ~18:52Z (dev mode per `docs/playbook.md`; gate clock in `docs/reviews/weekly-0001.md`). Nothing in this map may touch the running bot before gate evidence.
- **Courseware**: Lesson 0002 ("reading the loop") parked by the destination redraw; sequencing decision deferred.
- **User stance anchor**: "we need something robust, not vibes of an LLM" — every feature and knob earns its place in walk-forward evidence.

## Decisions so far

- **Harness kept; gate intact** (2026-11-09, grill): v0.1 infra stays live untouched ("it works well"); v0.2 research/design proceeds in parallel; **integrating** any new Decide into the running bot waits for gate evidence (≥2 weeks / ≥30 closed trades / clean incident review per `docs/playbook.md` §5).
- **Stocks: inputs-only; on-chain parked** (2026-11-09, grill + [stocks research](../../research/stocks-input-feasibility.md) + [on-chain research](../../research/onchain-data-sources.md)): stocks are never a trading venue in this effort (recorded facts: from Ireland only the IBKR tier is viable and it's high-effort; PDT is US-margin territory; equities hours 14:30–21:00 IST structurally conflict with 24/7 autonomy). Instead: **FRED + yfinance macro dailies become built-in ablation candidates** in the v0.2 feature matrix (low difficulty; last-known-value `merge_asof` joins with publication-timestamp hygiene; Stooq verified unusable unattended). **On-chain stays parked**: no free feed offers hourly aggregated BTC on-chain metrics (hourly = $584–799/mo tiers), free feeds are daily-native with revision-hygiene needs, and none of the cited papers uses on-chain features.
- **Multi-pair set & capital** (2026-11-09, grill + [pair-shortlist research](../../research/pair-shortlist.md)): static whitelist **BTC, ETH, SOL, XRP, LINK, DOGE** (alternates ADA/LTC; Bybit withdrawal/fee status auth-gated — re-verify at decision time); **`max_open_trades: 3`**, wallet/stake unchanged (1000/250) ⇒ ≤75% engaged. Evidence note: hour-returns are 0.78–0.92 BTC-correlated across majors — diversification gain modest, favoring a small set.
- **ML-first Decide via FreqAI** (2026-11-09, grill + [multipair/FreqAI research](../../research/freqtrade-multipair-freqai.md)): **LightGBMClassifier** first (SKLearnRandomForestClassifier mirrors 2407.18334's top performer; CatBoost removed from stable 2026.10); **long-only probability-threshold entries gated by the 2606.00060 cost-aware filter** (verified: λ=2.0, c=10bp ⇒ trade only when |r̂| > 20bp), exits stay the strategy's own signals + rails — the v0.1 `enter_long`/`exit_long` contract carries the swap. Per-pair models are the only documented FreqAI mode; cross-pair context via `include_corr_pairlist` features. **`live_retrain_hours: 24`** to start (fresh model per pair per day, staleness via `expiration_hours`), swept in backtesting. LLM-hybrid layer stays late fog.
- **News stack: free-first** (2026-11-09, grill + [news research](../../research/news-sentiment-sources.md)): **Alpha Vantage NEWS_SENTIMENT** as per-ticker core (pre-scored, second-level timestamps, 25 req/day), GDELT free archive available as aggregate-tone secondary (15-min files since 2015), CryptoPanic live-only and **self-archived from day 1** (no history API). **No paid source yet** — GNews (€49.99/mo, history since 2020, CryptoTrade's own source) is bought only if walk-forward evidence shows news features earn their keep. Survey anchor (§7.2.4): sentiment "has to be combined with Machine Learning".
- **Rails under multi-pair** (2026-11-09, grill + [multipair/FreqAI research](../../research/freqtrade-multipair-freqai.md)): CooldownPeriod pair-level (unaffected); **StoplossGuard stays `only_per_pair: False`** ⇒ global portfolio circuit breaker (2 losing stoploss-family exits in 24h freeze all entries 4h — doc-quoted behavior); MaxDrawdown global-only as designed (`equity` mode, realized closed-trade drawdown). Knobs (per-pair escape) recorded for later sweeps.
- **News→1h feature pipeline** (2026-11-09, grill + [news research](../../research/news-sentiment-sources.md)): **Alpha Vantage NEWS_SENTIMENT core** — incremental fetches inside the 25 req/day budget using `time_from` = last-fetch marker; per-ticker articles bucketed per hour per pair into **`news_sentiment_mean` (relevance-weighted) + `news_count`**; merged onto the 1h frame **lookahead-safe** (only articles published ≤ candle close enter that candle) via the docs-verified informative `ffill` join. **CryptoPanic self-archived hourly from day 1** (no history API — its features grow from archive start). **GDELT parked** (aggregate tone, not per-coin). Raw responses archived as JSONL under `bot/user_data/news/` (gitignored) so backtests rerun on the exact news seen.
- **Labels + exits** (2026-11-09, grill): **fee-aware binary FreqAI classification label** — target = 1 when future 6h return clears **0.30%** (round-trip taker ≈0.20% + 0.10% buffer), recomputed per window by FreqAI (no lookahead, verified). **Classifier gates entries only** via probability threshold (start 0.55); **exits stay v0.1 behavior** — EMA death-cross + stoploss + rails — keeping gate-boundary attribution comparable.
- **Feature matrix + sweep plan** (2026-11-09, grill): three config-toggled groups — **market** (1/6/24h returns, RSI14, ATR/close ratio, volume z-score, EMA12/26 distance), **news** (the two pipeline features per pair), **macro ablation** (DXY/VIX/SPX/gold daily closes as last-known-value, publication-time-safe) — plus `include_corr_pairlist` BTC-context features for non-BTC pairs. Sweep = label horizon, proba threshold, retrain cadence; hyperopt stays fog.
- **Strategy/config/cutover** (2026-11-09, grill): new strategy **`FreqaiEmaExit`** (`EmaCrossBaseline` untouched and running until cutover); new **`bot/config-v02.json`** — 6-pair whitelist, rails verbatim, dry-run, separate DB (`tradesv3.dryrun.v02.sqlite`), freqai block (identifier, 24h retrain, expiry). **Post-gate cutover** = stop v0.1 bot → start v0.2 with fresh DB → the same gate criteria re-applied to the v0.2 dry-run before any realism upgrade. Pre-agreed TDD seams: news archive/aggregation (pure functions), feature/label engineering, config-v02 validation, strategy contract + no-lookahead tests.

## Open decisions

_(none — map complete, 2026-11-09. Build per `spec.md`; the TDD build ran in the same session as the spec under the user's fast-path authorization.)_

---

*(Decisions index continues — see the spec-authoring entry below.)*

- **v0.2 spec authored — map complete** (2026-11-09): spec at `.scratch/agent-v02-model/spec.md` covering pipeline/labels/features/strategy/config/cutover with fact-checked numbers (`research/fact-check-av-cryptopanic-freqai.md`); pre-agreed TDD seams S-A–S-F all built green (31 tests), `FreqaiEmaExit` resolves from `config-v02.json`. Build artifacts: `newsfeed.py`, `featurelab.py`, `newsstore.py`, `FreqaiEmaExit.py`, `config-v02.json`, archive layout `bot/user_data/news/` (gitignored). User authorization: fast path chosen after this map reached one open decision (spec authoring) — batched decisions + build in one session, per the recorded override pattern.

## Not yet specified

- LLM-hybrid reflection layer (CryptoTrade pattern) — after a measurable classifier exists.
- On-chain re-evaluation trigger (payment-tier appetite; PIT hygiene discipline).
- GDELT aggregate-tone features (free, but global-press, not per-coin).
- Hyperopt of model hyperparameters; FreqAI identifier/DataPath persistence details.
- Weekly-review learnings from the live gate feeding v0.2 (incident patterns, rail behavior).
- VPS/unattended ops (supervisor, alerting) and the realism upgrade (Bybit demo wallet) — v0.1 fog carries over unchanged post-gate.
- Signup-time verifications (`research/venue-ireland.md` checklist) — unchanged.

## Out of scope

- Stock trading as a venue (IBKR facts recorded; separate future effort if ever).
- Real-money go-live (gates define criteria only).
- Production code authored by map sessions (plan, don't do; build follows the spec hand-off).
- LLM-driven decision logic in v0.2 (user stance: walk-forward evidence first).
- Courseware authoring inside this effort.
