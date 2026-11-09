# Spec: agent v0.2 — FreqAI multi-source Decide on the live harness

**Status:** build-ready (2026-11-09). Source of truth: `.scratch/agent-v02-model/map.md` (Decisions so far) + `research/` scans + `research/fact-check-av-cryptopanic-freqai.md`. Pre-agreed sequencing: user chose the fast path (batched decisions → this spec → TDD build). v0.1 (`spec` in `agent-v01-spec/`) stays untouched and live until the cutover defined here.

## 1. What changes vs v0.1

Single-pair EMA baseline → **6-pair static set, FreqAI LightGBM classifier Decide gated by fee-aware labels and a probability threshold; news features injected into the 1h frame; macro features as ablation candidates; same rails verbatim**. The v0.1 bot keeps running and is not modified; the v0.2 bot boots only after the v0.1 gate verdict.

## 2. Artifacts & repo layout

```
bot/
  config-v02.json                      # public v0.2 run config (tracked)
  config-private.example.json          # unchanged; used by both bots via second -c
  user_data/strategies/
    EmaCrossBaseline.py                # untouched (v0.1 live)
    FreqaiEmaExit.py                   # v0.2 strategy (tracked)
    newsfeed.py                        # news bucketing + lookahead-safe merge (tracked)
    featurelab.py                      # market features + fee-aware label (tracked)
    newsstore.py                       # archive read/write + live fetch scheduling (tracked)
  user_data/news/                      # self-archive, gitignored: av/ and cryptopanic/ JSONL
  user_data/macro/                     # macro CSV store, gitignored (post-cutover population)
  tradesv3.dryrun.v02.sqlite           # runtime v0.2 dry-run DB (gitignored)
  tests/
    test_ema_cross_baseline.py         # v0.1 suite — must stay green
    test_config.py                     # v0.1 — stays green
    test_newsfeed.py                   # seam: news bucketing + lookahead-safe merge
    test_featurelab.py                 # seam: market features + fee-aware label
    test_newsstore.py                  # seam: AV adapter + archive round-trip
    test_freqai_ema_exit.py            # seam: strategy contract
    test_config_v02.py                 # seam: config-v02 validation
docs/playbook.md                       # v0.2 cutover procedure appended
```

## 3. Data sources

- **Alpha Vantage NEWS_SENTIMENT (core, free)** — verified schema (`research/fact-check-av-cryptopanic-freqai.md`): `function=NEWS_SENTIMENT`, `tickers=CRYPTO:BTC` (etc — verified format), `time_from=YYYYMMDDTHHMM` incremental; per article: `time_published` (`YYYYMMDDTHHMMSS`), `overall_sentiment_score`, and `ticker_sentiment[]` with `relevance_score` + `ticker_sentiment_score`. Free budget: 25 req/day (premium-badge ambiguity noted — the spec ships a quota scheduler that spreads fetches across the day and treats any 4xx/26 (premium notice) as "degrade to CryptoPanic-only", not a crash).
- **CryptoPanic self-archive** — verified: `auth_token` required, plan-qualified URL `https://cryptopanic.com/api/<api_plan>/v2/`, `currencies=` filters, posts carry `votes` (crowd votes, **no model sentiment**) and `published_at` ISO-8601. Hourly fetch, raw JSONL archive; features only from archive start.
- **GDELT**: parked (aggregate tone; re-evaluate later).
- **Archive layout**: `bot/user_data/news/<source>/<UTC-date>.jsonl` — append-only, each line = raw API payload + fetch timestamp; **the archive is the source of truth for features** so backtests and live runs consume identical data.

## 4. News→1h feature pipeline (verified hooks)

1. `newsstore.load_articles(source, timerange)` reads the archive into normalized articles (`pair`, `ts` UTC, `sentiment`, `relevance`); the AV adapter maps `CRYPTO:<COIN>` → `<COIN>/USDT` pairs on the whitelist, per-article sentiment = the matching `ticker_sentiment` entry's `ticker_sentiment_score`, relevance = its `relevance_score` (fallback to `overall_sentiment_score` with relevance 1.0 when no ticker row exists), time = `time_published`.
2. `newsfeed.bucket_hourly` → per pair-hour `news_sentiment_mean` (relevance-weighted) + `news_count`.
3. `newsfeed.merge_article_features(candles, features, pair)` — **availability = bucket end**: a candle's decision time is its close (`date + timeframe`); it may use any bucket with `bucket_end <= close` (all bucket articles published before the close by construction). Earlier candles get NaN (filled downstream as zero-count).
4. Injection into the strategy: **`feature_engineering_standard`** (base-timeframe, no auto-expansion) calls the pipeline per pair — verified `%-` prefix requirement for all feature columns.
5. CryptoPanic archive contributes a second feature pair (`cp_count`, `cp_sentiment` = mean of `votes.positive - votes.negative` normalized) from archive start.

## 5. Label + exits (verified FreqAI contract)

- **Label (classifier, string classes)** — in `set_freqai_targets`: with `label_period_candles: 6` (config), `&-up_flat = 'up'` where future-6h return > 0.30% (Bybit spot 0.1% taker verified ⇒ 0.20% round trip + 0.10% buffer; the numeric engine lives in `featurelab.fee_aware_labels`, string wrapper for FreqAI), else `'flat'`; last-horizon rows NaN (training drops them; verified recompute-per-window, no lookahead). **The fee-aware threshold IS the cost-aware λ·c discipline under a classifier** — λ sweep becomes label-threshold sweep.
- **Prediction surface (verified in `BaseClassifierModel.predict`)**: predicted class in `&-up_flat` + **per-class probability columns named by the model's classes** (`'flat'`, `'up'`).
- **Entry gate**: `do_predict == 1` AND prediction == `'up'` AND `df["up"] > 0.55` (swept).
- **Exits unchanged**: EMA death-cross exit signal + stoploss `-0.05` + the three rails (identical to v0.1) — exit behavior stays comparable across the gate boundary.

## 6. Features (three toggleable groups + FreqAI expansion)

Strategy reads group toggles from config (`bot_name`-level custom keys): `"v02_feature_groups": {"market": true, "news": true, "macro": false}`.
- **market** (in `feature_engineering_standard`/`basic`, `%-` prefixed): `%-f_ret_1/6/24`, `%-f_rsi14`, `%-f_atr_close`, `%-f_vol_zscore`, `%-f_ema12_26_dist` (`featurelab.market_features`).
- **news**: `%-news_sentiment_mean`, `%-news_count`, `%-cp_count`, `%-cp_sentiment`.
- **macro** (ablation, default OFF until a downloader exists): `%-macro_<series>` daily closes as last-known-value.
- **FreqAI expansion config**: `include_timeframes: ["1h"]`, `include_corr_pairlist: ["BTC/USDT"]` (spot naming verified), `include_shifted_candles: 2`.
- **Sweep plan** (backtests): label horizon (`label_period_candles`), proba threshold, retrain cadence, feature-group ablations (market/news/macro on-off matrix on the walk-forward results).

## 7. Strategy contract: `FreqaiEmaExit`

Verified method set (`feature_engineering_expand_all/_basic/_standard`, `set_freqai_targets`, `populate_indicators = self.freqai.start(...)`): `INTERFACE_VERSION = 3`, `timeframe = "1h"`, `can_short = False`, `process_only_new_candles = True`, `use_exit_signal = True`, `exit_profit_only = False`, `ignore_roi_if_entry_signal = False`, `startup_candle_count = 100`, `minimal_roi = {}`, `stoploss = -0.05`, `protections` property **identical to v0.1** (CooldownPeriod 2c; StoplossGuard 24c/2/4c `only_per_pair: False` global; MaxDrawdown `equity` 168c/5/0.2/24c). Entry per §5; exit EMA death-cross; colliding-signal rule docs-verified (entry ignored when both signal same candle).

## 8. Config: `bot/config-v02.json`

Same public shape as v0.1 config plus: `"pair_whitelist": ["BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","LINK/USDT","DOGE/USDT"]` (StaticPairList), `"max_open_trades": 3`, `"db_url": "sqlite:///bot/tradesv3.dryrun.v02.sqlite"`, `"freqaimodel": "LightGBMClassifier"` (schema-verified key), `"freqai": {"enabled": true, "identifier": "v02-ema-exit", "purge_old_models": 2, "train_period_days": 30, "backtest_period_days": 0.042, "live_retrain_hours": 24, "expiration_hours": 48, "feature_parameters": {"include_timeframes": ["1h"], "include_corr_pairlist": ["BTC/USDT"], "include_shifted_candles": 2, "label_period_candles": 6}, "data_split_parameters": {"test_size": 0.25}, "model_training_parameters": {}}` — custom `"v02_feature_groups"` block per §6. Timeframe/stoploss/initial_state/api_server ownership rules identical to v0.1 spec §3 (strategy owns timeframe+stoploss; private overlay owns api_server; boots STOPPED).

## 9. Cutover + gates

- **v0.1 gate verdict first** (playbook §5: ≥2 weeks, ≥30 trades, clean incident review) → then: stop v0.1 process → `uv run freqtrade trade -c bot/config-v02.json -c bot/config-private.json --logfile bot/bot-v02.log` → re-arm via REST → **the same gate criteria re-applied to the v0.2 dry-run** before any realism upgrade. v0.1 DB remains as historical record.
- Backtest validation pre-cutover: `uv run freqtrade backtesting -c bot/config-v02.json --freqaimodel LightGBMClassifier --timerange <range>` with `--enable-protections` for rail evidence.

## 10. TDD plan — pre-agreed seams

(Confirmed with the user in the batched grill; v0.1 suite must stay green throughout.)

- **S-A newsfeed bucketing** — relevance-weighted means/counts per pair-hour (independent literal expectations).
- **S-B lookahead-safe merge** — bucket-end availability semantics incl. the exact-match boundary and the future-article leak case.
- **S-C featurelab** — market features vs pandas/Wilder independent references; fee-aware label NaN tail + threshold crossing.
- **S-D AV adapter + newsstore** — normalized `CRYPTO:<COIN>`→`<COIN>/USDT` mapping on a literal verified-schema fixture; archive round-trip (JSONL append + read-back); quota scheduler decides fetch windows.
- **S-E config-v02** — schema validation incl. the `freqai` block keys verified against the installed schema + absences per §8 ownership rules.
- **S-F strategy contract** — attributes/rails identical to v0.1, `%-` feature prefixes, string-class target naming, entry gate composition (`do_predict` + class prediction + proba), exit death-cross.

## 11. Acceptance criteria

1. Full suite green (v0.1 tests included).
2. `uv run freqtrade list-strategies -c bot/config-v02.json` resolves `FreqaiEmaExit`.
3. Config-v02 schema-validates with the freqai block (and fails without required keys).
4. Code-review pass; committed.
5. Post-build manual step (user, post-gate): first live dry-run boot of v0.2 per §9; news archive begins accumulating immediately on every v0.2 start.
