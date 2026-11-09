# Autonomous Crypto Trading Agent — Resources

All links verified live during session 1 (2026-11-09) unless marked otherwise.

## Knowledge

- [Repo findings: Open-source agents to adopt or borrow — `research/open-source-agents.md`](research/open-source-agents.md)
  Primary-source-verified 2026-11-09: **freqtrade = adopt-and-configure recommendation** (matches v0.1 point-for-point: Python, 1h, single-pair whitelist, Bybit spot officially supported with `exchange.demo_trading: true`, unattended dry-run documented, monthly releases, GPL-3.0 acceptable for private use, FreqAI ships the later model phase). Hummingbot: no Bybit spot candles feed (fatal). Jesse: live/paper gated behind a license-keyed plugin. OctoBot: Bybit currently impaired. CryptoTrade/FinRL: inspiration-only (stale / non-commercial license). Use for: the adopt-vs-build decision and v0.1 shape.
- [Repo findings: Risk rails fact-finding — `research/freqtrade-risk-rails.md`](research/freqtrade-risk-rails.md)
  Primary-source-verified 2026-11-09: stoploss mechanics (negative fee-inclusive ratio, mandatory, config-overrides-strategy; **Bybit spot ❌ exchange-side stoploss** — futures-only), config-level protections removed 2024.10 (strategy-only), per-protection params/defaults, DB-persisted locks block entries only, REST `/pause`=`/stopentry`=`/stopbuy` + `/stop` + `/locks` semantics (in-memory vs persisted), shutdown/`cancel_open_orders_on_exit` behavior. Use for: rails wiring and the kill-switch surface.
- [Repo findings: Trigger baseline fact-finding — `research/trigger-strategy-baseline.md`](research/trigger-strategy-baseline.md)
  Primary-source-verified 2026-11-09: minimal strategy anatomy (interface v3, ROI-disable via `minimal_roi = {}`, closed-candle → next-open execution), EMA 12/26 grounding (TA-Lib MACD conventions; 9/21 & 50/200 = community lore), survey-cited MA-rule baseline framing (Fang et al. §3.2/§6.1) and v0.2-classifier seam, freqtrade-strategies Strategy001 asymmetry note. Use for: the v0.1 strategy file.
- [Repo findings: Venue selection for Ireland — `research/venue-ireland.md`](research/venue-ireland.md)
  Primary-source-verified 2026-11-09: **Bybit EU** recommended (FMA/MiCA CASP 2025-05-28; official demo API `api-demo.bybit.com` + CCXT sandbox wiring); OKX runner-up; Kraken licensed in Ireland but CLI-only paper; Coinbase sandbox = canned mocks; **Binance blocked from EU operations May 2026**. Use for: venue wiring, paper path, and the signup verification checklist.

- [Survey: *Cryptocurrency Trading: A Comprehensive Survey* — Fang et al., arXiv 2003.11352](https://arxiv.org/abs/2003.11352)
  Maps 146 research papers: platforms, trading signals, strategies, risk management. The field map. Use for: deciding what to adopt and citing any claim in the Decide module.
- [Paper: *ML-Based Bitcoin Trading Under Transaction Costs: Walk-Forward Forecasting* — Bysik & Ślepaczuk, arXiv 2606.00060](https://arxiv.org/abs/2606.00060)
  ~70k hourly observations; XGBoost/LSTM/iTransformer under 27-fold walk-forward. Naive sign strategies die once fees hit; a cost-aware execution filter restores profitability. Use for: designing the buy/sell trigger and the cost model. XGBoost descriptively strongest.
- [Paper: *A Comprehensive Analysis of ML Models for Algorithmic Trading of Bitcoin* — Jabbar & Jalil, arXiv 2407.18334](https://arxiv.org/abs/2407.18334)
  41 classifiers/regressors benchmarked with both ML and trading metrics (P&L, Sharpe); Random Forest and SGD stand out. Use for: shortlisting classifier candidates for the Decide module.
- [Paper: *CryptoTrade — A Reflective LLM-based Agent to Guide Zero-shot Cryptocurrency Trading* — Li et al., arXiv 2407.09546 (EMNLP 2024)](https://arxiv.org/abs/2407.09546)
  LLM agent combining on-chain + off-chain data, with a reflection mechanism that reviews past decisions to refine the next ones. Use for: the Evaluate module and LLM-agent design patterns.
- [Paper: *An Ensemble Method of Deep RL for Automated Cryptocurrency Trading* — Wang & Klabjan, arXiv 2309.00626](https://arxiv.org/abs/2309.00626)
  Deep RL ensemble for intraday crypto portfolios; periodic retraining for non-stationarity. Use for: later, if the RL route ever opens.
- [Docs: CCXT manual](https://docs.ccxt.com/)
  Unified TypeScript/JS-first API for 100+ exchanges (markets, tickers, OHLCV, orders, balances; also CCXT Pro WebSockets). Use for: the Observe and Execute layers. `npm install ccxt`.
- [Docs: Freqtrade](https://www.freqtrade.io/en/stable/)
  Most battle-tested open-source crypto bot (Python): dry-run mode, strategy callbacks, backtesting, hyperopt, FreqAI. **Now first-class (2026-11-09 language flip)**: the build is Python — read freqtrade source as a working reference, not just docs.
- [Repo: freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies/)
  Open collection of example strategies. Use for: Decide-module inspiration from working, community-tested signals.

## Wisdom (Communities)

- [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
  Active bot-building community; strategy critique, dry-run debugging, realistic expectations. The user's primary community.
- [CCXT Discord](https://discord.gg/dhzSKYU)
  Exchange-API implementation help with the library maintainers.

## Gaps

- Vet [r/algotrading](https://www.reddit.com/r/algotrading/) — fetch returned an empty shell this session; content unverified.
- Free historical OHLCV data for backtesting in the Python pipeline (candidates: Binance public data dumps — account-blocked for EU users since May 2026 but public archives unaffected; Bybit OHLCV via CCXT/freqtrade `download-data`) — rides the data-pipeline open decision on the map.
- Survey of Python backtesting options beyond freqtrade's built-in backtester — only worth researching if the built-in fails a need.
