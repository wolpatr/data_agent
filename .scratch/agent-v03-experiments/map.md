---
labels: wayfinder:map
---

# Map: v0.3 experiments — pluggable strategies, governed splits, evidence store

## Destination

A **build-ready experimentation-infrastructure spec**: a convention-based runner that maps an experiment declaration → (strategy, model, feature-groups, split) → walk-forward/k-fold backtests → results indexed into a **relational store with embeddings** (vector layer for the later RAG explainability idea); governed train/validation/holdout splits with leakage hygiene; any classifier can plug in, any can be ruled out with evidence. No code in map sessions; worked in parallel with the live v0.1 gate.

## Notes

- **Session rules**: solo map-only override (as `agent-v01-spec`, `agent-v02-model`); one decision per session unless the user names one; grilling + domain-modeling default; research via subagents → `research/`.
- **Ground truth**: `MISSION.md`, `RESOURCES.md`, prior maps `.scratch/agent-v0{1,2}-*/map.md` (v0.2's Decide contract `enter_long/exit_long` + fee-aware labels is the pluggable unit).
- **Harness status**: v0.1 dry-run LIVE (gate clock from 2026-11-09 18:52Z, `docs/reviews/weekly-0001.md`); this effort never touches it. Backtest sweeps run offline.
- **User stance anchors**: "convention over framework" (runner = thin script + file conventions, no abstraction layer); **classifiers-first, "not vibes of an LLM"**; RAG-for-explainability = background idea only (see fog); LOOCV explicitly out of scope (cost on ~70k hourly rows).

## Decisions so far

- **Third effort charted** (2026-11-10, grill): experimentation infrastructure as its own map, parallel to the gate — motivated by the user's request for plug-in/plug-out strategies, cross-validation, train/test/validation sets, and a holdout.
- **Split protocol** (2026-11-10, grill + [walk-forward research](../../research/freqtrade-multipair-freqai.md) + 2606.00060): **walk-forward folds (12m-train/3m-val/3m-test-shape, sliding) for headline results; k-fold CV inside train windows for model selection; a sealed holdout timerange (recent ~3 months) computed exactly once per proposal**. LOOCV **out of scope** (computationally impractical at hourly granularity; k-fold + walk-forward give the evidence discipline).
- **Convention over framework** (2026-11-10, grill): the experiment unit is a **declaration file (one YAML per experiment)** naming the strategy file, FreqAI model adapter + params, feature-group toggles, split config, and label settings; a **thin runner script** resolves it into backtest invocations per fold and writes run records; strategies plug in/out by living/not-being-referenced under `bot/user_data/strategies/` (the existing `enter_long/exit_long` contract stays the seam); models plug in via FreqAI adapter names. Anything not reproducible from the declaration + archived data is invalid.
- **Holdout governance** (2026-11-10, grill): the holdout is **sealed by rule** — its results are computed once per proposal and recorded; any resweep against it is logged in `docs/interventions.md` (the anti-vibes policy extended to ML evidence).
- **Headline results get embedded into a relational store** (2026-11-10, grill, user requirement): experiment records land in a relational database with an embedding/vector layer for retrieval — groundwork for the later RAG explainability idea. The runner stays file-based, the store is an index built *from* run records, not a runtime dependency.
- **Results store chosen conditionally-verified** (2026-11-10, grill + [vector-store research](../../research/vector-stores-experiments.md)): **SQLite + sqlite-vec + all-MiniLM-L6-v2** — one file, zero services, local-first (matching the project's existing SQLite usage); pre-v1 status of sqlite-vec is managed by keeping the store a rebuildable index over retained source text with `model_id` versioning (upsert pattern). MiniLM condition met and verified (Apache-2.0, ungated HF download). Postgres + pgvector recorded as the upgrade path.
- **Split protocol amended by user: go straight to the paper protocol via open historical data** (2026-11-10, grill): the 12m-train/3m-val/3m-test sliding protocol (2606.00060-shaped) is the pinned headline protocol **now**, unlocked by extending the archive with open historical BTC 1h data ("we can absolutely get historical bitcoin data from an open source") — the 6/2/2 interim is dropped. Research fired: verify open sources (candidate: Binance public data dumps — public archives unaffected by EU restrictions per RESOURCES.md; bybit-via-CCXT depth) + the freqtrade `download-data`/import path; a task-type item follows to actually land the data.
- **Holdout seal: dates frozen now, policy grounded in literature** (2026-11-10, grill; grounded by [seal-literature research](../../research/holdout-seal-literature.md), receipt 2026-11-10): holdout #1 = **2026-08-10 → 2026-11-10**, frozen in the policy file; extension happens only via a logged intervention in `docs/interventions.md`. Literature receipt: the seal mirrors the competition pattern (Kapoor & Narayanan — no pre-competition access to the held-out set) and rolling-origin evaluation (Tashman 2000) — but Bailey et al.'s **PBO result means the seal must be paired with a persistent trials ledger** (every consulted run = one trial with its persisted Sharpe → deflated-Sharpe / PBO checks; Harvey et al.'s t>3 hurdle for post-sweep claims). The experiment index (decision: results store) IS that ledger — declaration-schema design must persist the trial matrix. Note: Bergmeir k-fold license conditions fail for hourly BTC (non-stationarity + overlapping labels) — k-fold stays selection-only, never headline. No primary source prescribes re-consult budgets for a sealed holdout (flagged novelty — policy file owns it).
- **Sharpe ratio is the goal indicator** (2026-11-10, grill, user): the ranking metric for experiment selection is **test-fold Sharpe** — the user's stated reason: it is the most stable indicator and accounts for volatility, applying across stocks and crypto. Headline table still reports the full stats set (annualized return, Sharpe, max drawdown, win rate, trade count).
- **k-fold stays opt-in** (2026-11-10, grill): runner defaults to walk-forward only; k-fold CV (k=5 within train windows) runs only when the experiment declaration sets `kfold: {k: 5}`.

## Open decisions

1. **Declaration schema + runner contract** — exact YAML fields, artifact conventions (`docs/experiments/<exp-id>/`), fold→backtest invocation mapping, strategy/model plug-in/plug-out mechanics (detailed sketch already agreed in grill; formalize).
2. **Author the experimentation spec** (awaits 1 + the two research receipts: historical-data sources, holdout-seal literature) — closes this map into the hand-off; implementation sessions follow (TDD, pre-agreed seams).

## Not yet specified

- **RAG explainability layer** (user background idea): embeddings over what corpus (experiments? news? strategy code?), retrieval UX, LLM role — deliberately deferred; the vector layer above is its only groundwork.
- Hyperopt integration into the runner; multi-model ensemble comparisons.
- On-chain / GDELT features as experiment feature-groups (parked sources).
- Weekly-review learnings feeding experiment design.

## Out of scope

- **LOOCV** (cost rationale recorded in the split-protocol decision).
- LLM-driven trading decisions (per user stance); touching the live v0.1 bot.
- Production code in map sessions; paid data sources.
