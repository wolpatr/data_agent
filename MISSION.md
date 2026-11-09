# Mission: Autonomous crypto trading agent

## Why
Build and ship a fully autonomous agent that buys and sells crypto by itself — it observes the market, decides when to buy and when to sell, and executes trades with no human in the loop. The decision logic must be adapted from prior research (surveys, papers, battle-tested open bots), not invented from scratch.

## Success looks like
- A running agent that fetches market data on a schedule, emits a BUY / SELL / HOLD decision, places the order via an exchange API, and logs every decision — unsupervised
- The decision logic is adapted from published research and validated on historical data before it ever trades
- Every trade is auditable: the agent can explain *why* it acted
- Paper money first; real money only after the system proves itself in dry-run

## Constraints
- **Python** is the implementation language for v0.1 (user-confirmed flip, 2026-11-09: user is Python-forward; TS stays a learn-later skill). Typed decisions via pydantic; the whole Python research ecosystem is now in reach (freqtrade, ML training).
- Research-grounded: adapt prior work before inventing anything
- Crypto spot market first (24/7 markets suit full autonomy)

## Out of scope
- US stock day-trading (PDT rule, market hours) — possible later via Alpaca, not now
- Leverage, futures, and shorting at the start
- Training ML models from scratch before borrowing from published research
