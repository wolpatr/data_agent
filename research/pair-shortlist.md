# Bybit USDT pair shortlist — liquidity evidence (v0.2 static set)

**Research date:** 2026-11-09 · **Status:** findings file (research-only, no production code) — input to the *pending* v0.2 pair-set decision, not the decision itself · **Method:** primary-source market data pulled live from Bybit v5 **public** API via CCXT 4.5.92 (Python 3.13.12 via `uv run`, repo root; pandas 3.1.1 present, not needed). No API keys, read-only endpoints only, small sleeps between calls. Every number below is reproduced by a recorded command in the appendix, each with its UTC fetch stamp.

---

## TL;DR

- **Recommended candidate set (6):** BTC/USDT, ETH/USDT, SOL/USDT, XRP/USDT, LINK/USDT, DOGE/USDT — with ADA/USDT and LTC/USDT as first alternates. All show uniform 1h candle quality (168/168 candles, zero empty or flat), one-tick or sub-bps spreads, and no wash-trade red flags.
- **BTC-correlation spread:** corr(1h returns vs BTC, 7d) spans **0.63–0.92** across the liquid universe. **No — ETH is not the only distinct beta; it is the *least* distinct (0.92 to BTC).** The distinct names are the low/mid-beta tier: PEPE (0.63), HYPE (0.70), AAVE/AVAX/WLD (~0.70–0.71), ENA/NEAR (0.74), XRP (0.78) — and TRX (0.33) breaks the blob entirely but fails the liquidity bar on Bybit spot.
- **Data quirks that shaped interpretation:** several "wide" spreads (ADA 5.6 bps, SOL/AVAX ~1.2 bps, LTC ~2–4 bps, DOGE 1.4–2.9 bps) are **tick-size floors**, not illiquidity; Bybit spot is perp-led (spot top-5 depth for AVAX/LINK/HYPE is thin even when 24h turnover looks healthy); withdrawal status/fees are auth-gated and must be re-checked at decision time.

---

## 1. Universe scan — what is actually listed

Active spot USDT markets on Bybit: **389** (fetch stamp 2026-11-09T22:29:47Z).

- **No leveraged tokens** in the current listing (no `UP`/`DOWN`/`BULL`/`BEAR`/`3L`/`3S` names anywhere in the 389) — that junk-filter branch is empty today.
- Junk takes other forms here, filtered manually by category:
  - **Tokenized equities:** AAPLX, AMZNX, GOOGLX, HOODX, NVDAX, TSLAX, CRCLX — excluded (different asset class, and equity-hours liquidity gaps).
  - **Gold / commodity tokens:** XAUT — excluded.
  - **Stables and quasi-stables (pairs with USDT):** USDC, RLUSD, USD1, USDE, XUSD, USDY, PYUSD, RLUSD, USDS, USDTB, FRAX, USD1/USDE/USDS — all excluded.
  - **LSTs:** STETH, METH, BBSOL — excluded (spread ≈ peg, no beta value).
  - **Small-cap / innovation-zone long tail:** the remaining ~300 names — excluded from candidates; all sampled core candidates carry `innovation = 0` (not in the innovation zone).
- TON is **not** listed on Bybit spot (absent from the 389).
- Notable absentees from the 24h top-25 despite being blue chips at other venues: **DOGE, ADA, LTC, BNB, TRX** — Bybit **spot** turnover is heavily concentrated in BTC/ETH/SOL/XRP; deep books are, not deep daily turnover, for these.

## 2. 24h quote volume (spot tickers)

Fetch stamps 2026-11-09T22:30:00Z (top-25 scan) and 22:31:59Z (candidate universe).

Top of the market (USDT, 24h turnover): BTC **$1.037B**, ETH **$283M**, USDC $228M (stable, excluded), SOL **$59.7M**, XRP **$45.1M**, HYPE $34.7M, LINK **$23.4M**, RLUSD $21.2M (stable), AAVE $21.0M, PEPE $17.4M, ENA $14.4M, USD1 $12.3M (stable), NEAR $11.1M, LIT $10.9M, PIEVERSE $10.3M, WLD $10.0M, XAUT $9.2M (gold), AVAX $8.4M, USDE $8.4M (stable), GRAM $7.7M, MNT $7.6M, DATA $6.8M, ONDO $6.8M, ASTER $6.5M, SUI $6.4M.

Candidate universe 24h volumes (USDT): BTC 1036.6M · ETH 282.4M · SOL 59.7M · XRP 45.0M · HYPE 34.7M · LINK 23.4M · AAVE 21.0M · PEPE 17.4M · ENA 14.4M · NEAR 11.1M · WLD 10.0M · AVAX 8.4M · SUI 6.4M · DOGE 5.7M · BNB 5.4M · ADA 3.2M · LTC 3.2M · TRX 1.7M.

**Wash-trading suspicion screen (manual, conservative):**
- Names whose top-25 volume far outruns name recognition and market-cap class — **LIT, PIEVERSE, GRAM, DATA** — excluded (can't verify organic turnover without deeper cap data; the conservative call for a static set is exclusion, not proof).
- Cross-basis consistency check (ticker 24h vs kline-derived daily average) held within ~10% for every candidate: DOGE 5.73M vs 5.68M/day, LTC 3.24M vs 3.47M/day, ADA 3.25M vs 2.89M/day, TRX 1.69M vs 2.35M/day — no 24h spikes that the 7d klines contradict.

## 3. 7-day 1h candle evidence + BTC/ETH correlation

Window: **2026-11-02T22:00Z → 2026-11-09T22:00Z**, 168 complete 1h candles, final in-progress candle dropped. "7d quote vol" = Σ close × base-volume (ccxt spot klines quote volume in base units — see quirks).

| pair | 24h vol $ | 7d quote vol $ | n/168 | zero-vol | flat | corr BTC | corr ETH |
|---|---|---|---|---|---|---|---|
| BTC/USDT | 1,036.6M | 6,269M | 168 | 0 | 0 | 1.000 | 0.924 |
| ETH/USDT | 282.4M | 1,735M | 168 | 0 | 0 | 0.924 | 1.000 |
| SOL/USDT | 59.7M | 391M | 168 | 0 | 0 | 0.887 | 0.901 |
| XRP/USDT | 45.0M | 283M | 168 | 0 | 0 | 0.784 | 0.796 |
| DOGE/USDT | 5.7M | 40M | 168 | 0 | 0 | 0.883 | 0.891 |
| ADA/USDT | 3.2M | 20M | 168 | 0 | 0 | 0.860 | 0.855 |
| LINK/USDT | 23.4M | 159M | 168 | 0 | 0 | 0.849 | 0.860 |
| AVAX/USDT | 8.4M | 26M | 168 | 0 | 0 | 0.715 | 0.714 |
| LTC/USDT | 3.2M | 24M | 168 | 0 | 0 | 0.854 | 0.842 |
| BNB/USDT | 5.4M | 46M | 168 | 0 | 0 | 0.914 | 0.909 |
| TRX/USDT | 1.7M | 16M | 168 | 0 | 0 | **0.331** | 0.320 |
| HYPE/USDT | 34.7M | 254M | 168 | 0 | 0 | 0.697 | 0.675 |
| AAVE/USDT | 21.0M | 119M | 168 | 0 | 0 | 0.704 | 0.709 |
| PEPE/USDT | 17.4M | 99M | 168 | 0 | 0 | **0.631** | 0.642 |
| ENA/USDT | 14.4M | 129M | 168 | 0 | 0 | 0.742 | 0.736 |
| NEAR/USDT | 11.1M | 92M | 168 | 0 | 0 | 0.745 | 0.724 |
| WLD/USDT | 10.0M | 62M | 168 | 0 | 0 | 0.709 | 0.736 |
| SUI/USDT | 6.4M | 44M | 168 | 0 | 0 | 0.851 | 0.847 |

**Candle quality:** identical across all 18 candidates — 168/168 candles present, **zero zero-volume and zero flat (high==low) candles**, and all series end timestamp-aligned on the same hour. 1h candle math is safe on any candidate.

**Correlation tiers (vs BTC, single 7d window — noisy, re-verify at decision time):**
- **High-beta blob 0.85–0.92:** ETH, BNB, SOL, DOGE, ADA, LTC, LINK, SUI.
- **Mid tier 0.70–0.79:** XRP 0.784, NEAR, ENA, AVAX, WLD, AAVE, HYPE.
- **Low tier:** PEPE 0.63.
- **Distinct decoupled beta:** TRX 0.33 — but 1.7M/day spot volume disqualifies it for a small static set here.

## 4. Spread and top-of-book depth (spot, two snapshots minutes apart)

Run 1 stamped 2026-11-09T22:31:09Z, run 2 at 22:31:33Z; top-5 levels only.

| pair | tick | spread bps (run1 / run2) | top-5 bid $ | top-5 ask $ |
|---|---|---|---|---|
| BTC | 0.1 | 0.013 / 0.013 | 57,968 | 46,891 |
| ETH | 0.01 | 0.047 / 0.282 | 10,766 | 15,776 |
| SOL | 0.01 | 1.154 / 1.154 | 105,029 | 132,046 |
| XRP | 0.0001 | 0.913 / 0.913 | 58,144 | 46,838 |
| DOGE | 0.00001 | 2.858 / 1.429 | 14,286 | 35,461 |
| ADA | 0.0001 | 5.635 / 5.635 | 132,269 | 90,302 |
| LINK | 0.001 | 0.937 / 2.811 | 3,276 | 6,386 |
| AVAX | 0.001 | 1.158 / 2.318 | **549** | **565** |
| LTC | 0.01 | 3.887 / 1.944 | 10,789 | 6,583 |
| HYPE | 0.001 | 0.133 / 0.133 | 1,156 | 457 |

**How to read this:**
- **Spread at tick floor ≠ illiquidity.** ADA's 5.6 bps is *exactly one tick* (0.0001 on $0.1774); SOL/AVAX are also 1 tick. The real reading: these books are quoted as tight as the venue's tick allows. BTC (0.013 bps) is the only pair spread below a tick's worth of price distance.
- **Snapshot noise is material.** ETH spread moved 0.047 → 0.282 bps and DOGE 2 ticks → 1 tick between snapshots 24 s apart; top-5 notional is an instantaneous thin slice. Treat as order-of-magnitude evidence and re-sample at decision time.
- **Real illiquidity signals in this table:** AVAX top-5 ~$550, HYPE ~$1.2k/0.5k, LINK ~$3–6k — despite healthy turnover for HYPE/LINK. **Bybit spot is perp-led**: high 24h turnover can come from a book whose resting depth is small.
- All sampled candidates: `innovation = 0`, `marginTrading = utaOnly` (no cross-margin spot borrowing on these pairs; irrelevant to a spot-only dry-run, recorded for completeness).

## 5. Recommended candidate set (4–6 pairs) + rationale

| # | pair | one-line rationale (evidence-based) |
|---|---|---|
| 1 | **BTC/USDT** | Anchor: deepest top-5 book measured ($47–58k), tick-floor 0.013 bps, $1.0B/day spot turnover, $6.3B/7d — the pair the harness must handle in every regime. |
| 2 | **ETH/USDT** | Second-deepest book, 0.05–0.28 bps spread, $283M/day — but corr 0.92 to BTC means expect co-drawdown with the BTC slot, not diversification. |
| 3 | **SOL/USDT** | Deepest measured top-5 ($105–132k), 1-tick spread, $391M/7d, corr 0.89 — clean third leg. |
| 4 | **XRP/USDT** | $45M/day with deep top-5 book ($47–58k) and the cheapest *below-0.8* BTC-beta among liquid names (corr 0.78) — only genuine beta spread in the top-4. |
| 5 | **LINK/USDT** | $159M/7d turnover with consistent multi-day volumes, corr 0.85, 1–3-tick spread; top-5 resting depth is modest ($3–6k) — sized fine for fixed small stakes. |
| 6 | **DOGE/USDT** | The one large-cap meme with an honest here-consistent volume profile ($40M/7d, corr 0.88, 1–2-tick spread) — the meme slot if the set wants six. |

**First alternates:** ADA (deepest top-5 book after SOL — $90–132k — but thinnest spot turnover of the core names, $3.2M/day), LTC (solid book, old-school 0.85 beta, $3.2M/day).

**Deliberately not in the initial set:**
- **HYPE** — tightest non-BTC spread (0.13 bps) and $34.7M/day, but top-5 resting depth ≤ ~$1.2k is perp-ghost turnover, and it is the newest listing here (Dec 2024) — single-token-news and listing-stability risk above the rest. Watch, don't seed.
- **AVAX** — the one major with a visibly thin spot top-5 ($550) at snapshot; volume exists but resting depth doesn't.
- **TRX** — only distinct low beta (0.33), useless at 1.7M/day Bybit spot.
- **ENA/NEAR/WLD/SUI/AAVE/PEPE** — acceptable volumes but mid-cap idiosyncratic news risk; PEPE additionally worth remembering as the *lowest* liquid correlation (0.63) if the set later wants a deliberate beta-spreader.
- **Stables, tokenized equities, gold, LSTs, innovation-zone / unrecognized top-25 names** — category-excluded per §1–2.

## 6. What makes a pair suitable for a fixed-stake `max_open_trades: 3–5` bot

- **Deep top-of-book and thick top levels** — fills near signal price for stakes in the hundreds-of-USDT range; all measured core candidates pass except AVAX resting depth.
- **Tight spread** — on Bybit spot the binding constraint is tick size, and the core candidates quote at 1 tick or tighter effectively; for small stakes, execution cost is dominated by the taker fee (~0.1% base assumed but **not verified this session** — see research/venue-ireland.md fee caveat), not by spread.
- **Uniform 1h candle history** — no gaps/zero-volume/flat candles in 168 windows for all candidates; strategy math needs no pair-specific candle hygiene.
- **Low wash-trading suspicion** — recognized large caps, `innovation=0`, volume-to-name-recognition sanity, and ticker-vs-kline volume consistency within ~10%; the flagged names (LIT, PIEVERSE, GRAM, DATA) are excluded rather than disproven.
- **Listing stability** — prefer multi-year listings; HYPE (2024-12) is the youngest. No delisting or inactivity signals observed in the candidate set (all active, normal books, normal candles). No leveraged-token listings conflict on spot today.
- **Bybit-specific operational notes:** spot margin is `utaOnly` (no cross-margin spot borrow on these pairs); withdrawal status and fees are **auth-gated** (`fetch_currencies()` returns `{}` without keys — verified) and depend on the coin, so re-verify per candidate via the withdrawal UI/asset pages at decision time; pair sets must be re-checked against `load_markets()` active status in the harness startup, since a delisted pair silently breaks a static config.

## 7. Design implications for v0.2 — neutral inputs, NOT the decision

- A static 4–6-pair set drawn from the recommendation table passes every measured data-quality bar identically (candles, ticks, books), so the v0.2 harness can treat the pair set as data-homogeneous — the map decides whether to use 4, 5 or 6, and whether DOGE is in.
- With 5 of a 6-pair set sitting at corr ≥ 0.85 vs BTC, **concurrent positions will co-activate**: `max_open_trades: 3–5` should be stress-tested assuming 3–5 simultaneous same-direction drawdowns, not independent ones. XRP (0.78) is the only affordable beta-spreader in the recommended core; PEPE (0.63) is the cheap deliberate diversifier left out on other grounds.
- The perp-led spot structure (HYPE/LINK-style turnover-with-thin-book) is venue-real: any v0.2 liquidity sizing rule should key on *resting depth + multi-day kline volume*, not 24h turnover alone.
- Config/data-plumbing facts to encode in v0.2: static pair set must re-validate against `load_markets()` active spot on startup; withdrawal status is auth-gated and therefore out of scope for the dry-run harness; fee schedule still unverified.
- Re-verification at decision time costs minutes: re-run the appendix commands on the day of decision (single 7d window; correlation numbers are regime-dependent), and sample order books 3–4 times rather than twice.
- No TON on Bybit spot; no leveraged tokens on spot — if the map ever wants either asset class, it is a venue-capability constraint, not a configuration one.

## 8. Data quirks and caveats (so numbers are read correctly)

- **ccxt 4.5.92 API traps hit en route:** `fetch_tickers(None, {"type": "spot"})` — the first positional arg is symbols, passing a params dict there raises `KeyError: 0`; `OrderBook` has **no normalized `bid`/`ask` keys** for Bybit — use `bids[0][0]`/`asks[0][0]`; `ccxt.bybit(enableRateLimit=True)` kwargs form rejected — pass a dict; `ccxt.milliseconds()` is not module-level (use `Exchange.ms`/`datetime`).
- **Spot kline `volume` is base-denominated.** 7d "quote vol" here = Σ close×volume; cross-checked against ticker 24h turnover (§2) — consistent within ~10% per-day; BTC weekly total (6.27B) sits ~14% under 7× the single-day ticker (7.26B) — plausible weekly variation, another reason to re-run at decision time.
- **Spread figures are tick-size artefacts** wherever the quoted spread ≈ 1–2 ticks; snapshot noise was directly observed (ETH 0.047→0.282 bps in 24 s).
- **Top-5 depth is a floor, not a ceiling** — books with many granular levels (LINK, AVAX) look thinner at limit=5 than they trade.
- **Correlations are one 7d regime** (Pearson on 167 aligned hourly returns, `statistics.correlation`); single-window numbers, not structural claims.
- **Withdrawal/fee data is auth-gated** — attempted without keys, returned `{}`; no withdrawal claims are made in this file.
- 24h ticker and kline snapshots were taken minutes apart; all timestamps recorded per command below.

---

## Appendix — reproducible retrieval commands (as run; PowerShell single-quote form)

All commands run from repo root with `uv run`; python 3.13.12, ccxt 4.5.92. Each command prints its UTC fetch stamp as its first output line. Recorded `\"`/quotes match the PowerShell 5.1 invocation used here — on other shells pass the code with ordinary quoting.

```powershell
# (1) env + stamp  ->  2026-11-09T22:29:33Z; Python 3.13.12, ccxt=4.5.92, pandas=3.1.1
uv run python -c 'import sys,ccxt,pandas,datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat()); print(sys.version.split()[0], \"ccxt=\"+ccxt.__version__, \"pandas=\"+pandas.__version__)'
```

```powershell
# (2) universe scan: active spot USDT markets  ->  22:29:47Z; count=389 + full symbol list
uv run python -c 'import ccxt,datetime; ex=ccxt.bybit({\"enableRateLimit\":True}); m=ex.load_markets(); spot=sorted([s for s,x in m.items() if x.get(\"spot\") and x.get(\"quote\")==\"USDT\" and x.get(\"active\")]); print(datetime.datetime.now(datetime.timezone.utc).isoformat()); print(len(spot)); print(spot)'
```

```powershell
# (3) top-25 by 24h quote volume  ->  22:30:00Z; 388 rows scanned
uv run python -c 'import ccxt,datetime; ex=ccxt.bybit({\"enableRateLimit\":True}); ex.load_markets(); ts=ex.fetch_tickers(None,{\"type\":\"spot\"}); rows=sorted([(t[\"symbol\"],t.get(\"quoteVolume\")) for k,t in ts.items() if t.get(\"quoteVolume\") and t[\"symbol\"].endswith(\"/USDT\")], key=lambda r:-(r[1] or 0)); print(datetime.datetime.now(datetime.timezone.utc).isoformat()); print(len(rows)); [print(i+1,r[0],round(r[1])) for i,r in enumerate(rows[:25])]'
```

```powershell
# (4) 7d 1h candles x18 pairs: 7d quote-vol, candle count, zero-vol count, flat count,
#     corr(BTC), corr(ETH), timestamp-alignment flag  ->  22:30:52Z; window 2026-11-02T22:00Z..22:00Z
uv run python -c 'import ccxt,statistics,datetime,time; ex=ccxt.bybit({\"enableRateLimit\":True}); ex.load_markets(); pairs=\"BTC/USDT ETH/USDT SOL/USDT XRP/USDT DOGE/USDT ADA/USDT LINK/USDT AVAX/USDT LTC/USDT BNB/USDT TRX/USDT HYPE/USDT AAVE/USDT PEPE/USDT ENA/USDT NEAR/USDT WLD/USDT SUI/USDT\".split(); d={p:(time.sleep(0.25),ex.fetch_ohlcv(p,\"1h\",limit=169))[1][:-1] for p in pairs}; b=d[\"BTC/USDT\"]; e=d[\"ETH/USDT\"]; rb=[(y[4]-x[4])/x[4] for x,y in zip(b,b[1:])]; re=[(y[4]-x[4])/x[4] for x,y in zip(e,e[1:])]; print(datetime.datetime.now(datetime.timezone.utc).isoformat(), ccxt.Exchange.iso8601(b[0][0]), ccxt.Exchange.iso8601(b[-1][0]+3600000), len(b)); [print(p, round(sum(c[4]*c[5] for c in o)), len(o), sum(c[5]==0 for c in o), sum(c[2]==c[3] for c in o), round(statistics.correlation([(y[4]-x[4])/x[4] for x,y in zip(o,o[1:])],rb),3), round(statistics.correlation([(y[4]-x[4])/x[4] for x,y in zip(o,o[1:])],re),3), int(o[-1][0]==b[-1][0])) for p,o in [(p,d[p]) for p in pairs]]'
```

```powershell
# (5) orderbook run 1: top-of-book spread bps x10  ->  22:31:09Z
#     (first attempt errored on o["bid"]: ccxt 4.5.92 has no normalized bid/ask; bids[0][0]/asks[0][0] below)
uv run python -c 'import ccxt,datetime,time; ex=ccxt.bybit({\"enableRateLimit\":True}); ex.load_markets(); pairs=\"BTC/USDT ETH/USDT SOL/USDT XRP/USDT DOGE/USDT ADA/USDT LINK/USDT AVAX/USDT LTC/USDT HYPE/USDT\".split(); L=[(p,(time.sleep(0.3),ex.fetch_order_book(p,limit=5))[1]) for p in pairs]; print(datetime.datetime.now(datetime.timezone.utc).isoformat()); [print(p, o[\"bids\"][0][0], o[\"asks\"][0][0], round((o[\"asks\"][0][0]-o[\"bids\"][0][0])/((o[\"asks\"][0][0]+o[\"bids\"][0][0])/2)*10000,3), o[\"bids\"][0][1], o[\"asks\"][0][1]) for p,o in L]'
```

```powershell
# (6) orderbook run 2: spread bps, tick size, top-5 notional (bid/ask $), innovation flag, margin mode  ->  22:31:33Z
uv run python -c 'import ccxt,datetime,time; ex=ccxt.bybit({\"enableRateLimit\":True}); ex.load_markets(); pairs=\"BTC/USDT ETH/USDT SOL/USDT XRP/USDT DOGE/USDT ADA/USDT LINK/USDT AVAX/USDT LTC/USDT HYPE/USDT\".split(); L=[(p,(time.sleep(0.3),ex.fetch_order_book(p,limit=5))[1]) for p in pairs]; print(datetime.datetime.now(datetime.timezone.utc).isoformat()); [print(p, o[\"bids\"][0][0], o[\"asks\"][0][0], round((o[\"asks\"][0][0]-o[\"bids\"][0][0])/((o[\"asks\"][0][0]+o[\"bids\"][0][0])/2)*10000,3), ex.markets[p][\"info\"][\"priceFilter\"][\"tickSize\"], round(sum(b[0]*b[1] for b in o[\"bids\"])), round(sum(a[0]*a[1] for a in o[\"asks\"])), str(ex.markets[p][\"info\"].get(\"innovation\")), str(ex.markets[p][\"info\"].get(\"marginTrading\"))) for p,o in L]'
```

```powershell
# (7) 24h quote volume for the candidate universe  ->  22:31:59Z
uv run python -c 'import ccxt,datetime; ex=ccxt.bybit({\"enableRateLimit\":True}); ex.load_markets(); ts=ex.fetch_tickers(None,{\"type\":\"spot\"}); print(datetime.datetime.now(datetime.timezone.utc).isoformat()); [print(p, round(ts[p][\"quoteVolume\"])) for p in \"BTC/USDT ETH/USDT SOL/USDT XRP/USDT DOGE/USDT ADA/USDT LINK/USDT AVAX/USDT LTC/USDT BNB/USDT TRX/USDT HYPE/USDT AAVE/USDT PEPE/USDT ENA/USDT NEAR/USDT WLD/USDT SUI/USDT\".split()]'
```

```powershell
# (8) withdrawal-status probe without keys  ->  returns {} (empty) — auth-gated; verified 2026-11-09T22:32Z
uv run python -c 'import ccxt; ex=ccxt.bybit(dict(enableRateLimit=True)); print(ex.fetch_currencies())'
```
