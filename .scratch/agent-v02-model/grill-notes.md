# Charting notes — effort `agent-v02-model` (destination redraw, 2026-11-09)

User redirected the project destination mid-grill (grilling session, 2026-11-09). Recorded here until the map is charted.

## Destination (draft, approved in grill)

**Build-ready v0.2 spec: multi-source, multi-pair crypto agent on the existing freqtrade harness — ML classifier Decide (walk-forward-disciplined) consuming market + news inputs across a small static USDT pair set; integrated only after the v0.1 gate.**

## Grill decisions (2026-11-09, user)

- **Keep the harness** — v0.1 infra ("it works well") stays live untouched; nothing torn down; the running dry-run is the lab the v0.2 model plugs into.
- **Stocks**: signal *inputs* only, not a trading venue. Fallback decided: if input integration proves too difficult, a research agent investigates whether automated stock trading is viable at all (→ `research/stocks-input-feasibility.md`).
- **Multi-pair**: small **static** pair set (candidate shortlist by liquidity evidence → `research/pair-shortlist.md`), exact list decided inside this effort's map.
- **Model ordering**: **ML classifier first** ("we need something robust, not vibes of an LLM") — walk-forward-disciplined; LLM-hybrid layer later (map fog v0.2+), benefiting from an already-measurable classifier to reflect on.
- **Data-source core/stretch**: **core** = multi-pair candles + financial news/sentiment; **stretch** = on-chain metrics, stocks-inputs, other exogenous sources (each addition must earn its place in walk-forward evidence).
- **Gate intact**: v0.1 dry-run + 2-week gate continue untouched; v0.2 research/design may proceed in parallel; *integrating* any new model into the running bot waits for gate evidence.
- **Session style**: same solo map-only override as v0.1 (this effort, same rules); **no production code in map sessions**; research runs as subagents with findings under `research/`.
- User sanctioned parallel research subagents ("spin up as many as you need").

## Research wave fired (2026-11-09, 5 parallel subagents)

1. `research/news-sentiment-sources.md` — news/sentiment APIs usable by a Python bot (costs, limits, historical availability for backtesting, licensing, 1h suitability)
2. `research/onchain-data-sources.md` — on-chain feeds + literature-backed metrics (stretch-source case)
3. `research/stocks-input-feasibility.md` — stocks-as-input feeds + automated-stock-trading-from-Ireland viability verdict
4. `research/freqtrade-multipair-freqai.md` — multi-pair mechanics (pairlists, stake sizing, rail redesign under multi-pair) + FreqAI classifier architecture & walk-forward cadence
5. `research/pair-shortlist.md` — liquidity-evidenced candidate pairs for the small static set

## Parked

- Lesson 0002 ("reading the loop") — parked by the redirect; original transaction-costs promise from 0001 unresolved.
- v0.1 gate clock: started 2026-11-09 ~18:52Z, running in dev mode (see `docs/playbook.md`, `docs/reviews/weekly-0001.md`).

## Open after research (next grill round, with facts in hand)

- News→signal mechanism (how headlines become features on 1h candles)
- Classifier shape (target labels, model choice mapped to 2407.18334 shortlist)
- Rail redesign under multi-pair (StoplossGuard `only_per_pair`, MaxDrawdown global)
- Pair-set final list
