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
- **Headline results get embedded into a relational store** (2026-11-10, grill, user requirement): experiment records land in a relational database with an embedding/vector layer for retrieval — groundwork for the later RAG explainability idea. **Vector-store selection is an open decision below** (research fired: local-first options sqlite-vec/pgvector/Chroma/LanceDB/DuckDB-VSS + small embedding models); the runner stays file-based, the store is an index built *from* run records, not a runtime dependency.

## Open decisions

1. **Results store + embeddings** (awaits research) — relational schema for experiment records, what gets embedded (run summaries, model cards, later: news articles), vector-store choice, write-path placement in the runner.
2. **Declaration schema + runner contract** — exact YAML fields, artifact conventions (`docs/experiments/<exp-id>/`), how folds map to backtest invocations, how results are scored/aggregated, plugging a strategy/model in or out.
3. **Split-window policy** — concrete timeranges against the BTC 1h archive (2025→), holdout freeze-date policy, fold counts vs sweep breadth, multi-pair window rules.
4. **Author the experimentation spec** (awaits 1–3) — closes this map into the hand-off; implementation sessions follow (TDD, pre-agreed seams).

## Not yet specified

- **RAG explainability layer** (user background idea): embeddings over what corpus (experiments? news? strategy code?), retrieval UX, LLM role — deliberately deferred; the vector layer above is its only groundwork.
- Hyperopt integration into the runner; multi-model ensemble comparisons.
- On-chain / GDELT features as experiment feature-groups (parked sources).
- Weekly-review learnings feeding experiment design.

## Out of scope

- **LOOCV** (cost rationale recorded in the split-protocol decision).
- LLM-driven trading decisions (per user stance); touching the live v0.1 bot.
- Production code in map sessions; paid data sources.
