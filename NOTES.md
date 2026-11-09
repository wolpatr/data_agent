# Teaching notes

## Preferences & working notes
- **Correction (2026-11-09)**: user is MORE familiar with Python (session-1 "TypeScript basic" was incomplete). **Resolved: build language = Python for v0.1, user-confirmed** (see MISSION.md + map decision). Teach pivots: Lesson 0002 onward is Python-flavored; freqtrade becomes a hands-on reference; lesson 0001 (language-agnostic agent loop) unchanged; TS remains a side learning track.
- Workspace location chosen by user: `C:\Users\patri\Documents\Projects\data_agent` (they did not want files in the VS Code install folder).
- User originally wrote "typesafe jev" for the decision classifier. In session 1 they clarified: they meant a system to *analyse market data and trigger when to buy/sell*, research-grounded — NOT Zod specifically. Zod may still be a useful tool later for validating structured agent decisions; mention it opportunistically.
- Experience (self-assessed session 1): TypeScript basic. Trading concepts and LLM/agent APIs unselected → assume new to both until demonstrated otherwise. Teach vocabulary explicitly, link the glossary often.
- Research-heavy stance: lessons must carry citations; prefer adapting published work over inventing strategies.
- Crypto over stocks. Crypto chosen for 24/7 autonomy; stocks possible later but out of scope.

## Roadmap sketch (drift as evidence dictates)
> Superseded 2026-11-09: the build plan now lives on the wayfinder map at `.scratch/agent-v01-spec/map.md` (solo, map-only — open decisions worked one per session). Lessons below remain an indication of course sequence.
1. 0001 agent loop (anatomy) — DONE, plus glossary + loop-sim asset
2. Transaction costs & why naive strategies die (arXiv 2606.00060) + fee param in loop-sim
3. First real CCXT data pull in TS (project milestone)
4. Research feature/signals set for Decide (survey + 2407.18334)
5. Decision classifier v1 from research (hold out data; walk-forward idea)
6. Backtesting harness → dry-run deployment loop
