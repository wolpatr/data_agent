# Autonomous crypto trading agent

Language for the v0.1 spec effort: a freqtrade-based BTC/USDT spot agent (paper/dry-run first) whose decision logic is cited from published research. Mission lives in `MISSION.md`.

## Language

### Cycle

**Observe**:
The agent reads market state (candles, account state) each cycle.
_Avoid_: watch, monitor

**Decide**:
The agent turns observations into a trade action: enter, exit, or hold.
_Avoid_: signal, trigger (that's the rule inside Decide, not the act)

**Execute**:
The agent places or cancels orders so the market matches the decision.
_Avoid_: trade, order placement

**Evaluate**:
The agent (and human) review closed cycles to judge behavior and tune the next ones.
_Avoid_: report, review

### Risk rails

**Risk rails**:
The standing limits that cap how badly the agent can behave before the strategy is any good: stoploss, protections, intervention policy. Decided in the v0.1 spec effort.
_Avoid_: safety net, guardrails

**Stoploss**:
A price below entry that closes a losing position automatically. Bot-managed in v0.1 (Bybit spot offers no exchange-side stoploss). Contrast: **trailing stop** (v0.2 candidate) rises with price; base stoploss never does.

**Protection**:
A freqtrade mechanism that, when triggered, places temporary locks on new entries; it never closes an open position.

**Lock**:
A temporary ban on new entries, for one pair or globally, expiring after its stop duration. Protections create locks; the human can too.
_Avoid_: cooldown (that's one protection's name)

**Kill switch**:
The external act of stopping the agent process itself: open orders are cancelled, the open position survives.
_Avoid_: emergency stop, shutdown (too broad)

**Re-arm**:
Trading resumes only on an explicit human `/start` after a restart — the agent never boots back into trading on its own.
_Avoid_: auto-resume

**Manual intervention**:
A deliberate human trade action on a running agent: pause entries, force-exit an open trade, or full stop. Force-entering trades and editing recorded trades are explicitly forbidden — they would poison attribution.

**Attribution**:
The property that each closed trade reflects exactly one agent decision cycle, uncontaminated by human trades or manual bookkeeping. The reason single-pair, one-open-trade, and no-force-entry rules exist.

### Signals

**EMA crossover**:
A trigger comparing a fast and a slow exponential moving average; the v0.1 baseline signal family.
_Avoid_: MACD (a distinct oscillator built from an EMA pair)

**Golden cross**:
The fast EMA crossing above the slow EMA — the v0.1 entry rule.
_Avoid_: buy signal, long signal

**Death cross**:
The fast EMA crossing below the slow EMA — the v0.1 exit rule.
_Avoid_: sell signal, exit signal

**Fee-aware label**:
A training label that only fires when the predicted move clears round-trip trading costs plus a buffer — the classifier-era form of the cost-aware execution discipline.
_Avoid_: profit target, signal threshold

**Self-archive**:
Recording a data source's raw responses locally from day one because it offers no queryable history — what makes live-only news backtestable later.
_Avoid_: caching, backups
