# Stocks: inputs vs venue — feasibility fact-finding (v0.2)

**Research date:** 2026-11-09 · **Status:** findings file (research-only, no production code) · **Question:** (a) stocks/indices/macro as *signal inputs* to the multi-source ML-classifier Decide for the crypto agent (BTC/USDT 1h, freqtrade dry-run v0.1 → v0.2), and (b) as fallback: is *automated stock trading* even viable from Ireland, given the mission's 24/7 autonomy rationale.

**Method:** primary-source verification (vendor docs, broker docs, regulator/exchange pages, arXiv paper text, pandas docs) over a live-fetch session on 2026-11-09. Each fact carries **Verified** (fetched this session, from the owning party) or **Unverified** (blocked/broken fetch, JS-shell page, or widely-published figure not confirmed from a primary page here). Blocked-fetch list at the end explains the Unverified marks.

---

## TL;DR

- **Inputs (recommended path):** viable at **low integration difficulty**. Core stack: **FRED free API** (daily macro/rates/VIX/USD-index series, free key, verified this session) + **yfinance for Yahoo** daily equity/futures/indices closes (unofficial client; Yahoo ToS makes it personal-use-grade — an accepted grey zone for signal inputs, not redistribution). **Alpha Vantage free tier (25 req/day)** is a compliant key-based backup, too small for a 24/7 loop but fine for daily closes of a handful of tickers. **Stooq's one-line CSV reputation is outdated** — this session, its endpoints serve a JavaScript proof-of-work challenge to scripted clients (verified live), which disqualifies it for unattended Python fetching.
- **Cadence reality:** the free layer of every candidate feed is **daily-native** (FRED macro calendar-day; equities daily-close). A daily series enters an hourly feature set via a **last-known-value (as-of) join** — the standard approach, and one with first-party tooling: pandas `merge_asof` documents exactly this semantics ("A 'backward' search selects the last row in the right DataFrame whose 'on' key is less than or equal to the left's key").
- **Venue (fallback):** automated stock trading from Ireland is **possible but expensive in effort and in direct conflict with the mission's 24/7 autonomy**. Equities core hours are fixed (13:30–20:00 Irish time weekdays with a holiday calendar); US brokers with good APIs (IBKR Ireland, Alpaca) exist, but IBKR's API tier is a heavy operational surface and Alpaca's EU offering is B2B-partner-first (its Irish retail availability could not be verified this session). DEGIRO and eToro publish **no official public trading API** (not verifiable from their blocked pages this session — flagged Unverified). PDT-style margin rules are US-broker-dealer territory (IBKR Ireland clients sit under a Central Bank of Ireland entity, not a FINRA member), and FINRA itself has approved replacing PDT with an intraday-margin regime.
- **Verdict:** stocks-as-inputs and stocks-as-venue touch different problem spaces; **v0.2 should ship inputs-only**, which also matches the user's decision. The venue fallback is not "impossible" but is a different project (market-hours-constrained, margin-regulated, much heavier ops).

---

## Comparison table — (a) input feeds

| Source | Cost / limits | Historical depth | Cadence (free layer) | Legal/terms status | Verdict for v0.2 inputs |
|---|---|---|---|---|---|
| **FRED API** (St. Louis Fed) | **Free**; free API key mandatory | Decades for most series | **Daily/calendar-native** (rates, VIX, USD index, SP500 daily) | ToS: free; no cloaking, no excessive load; numeric quota at Fed's discretion; third-party copyrighted series carry owner restrictions | **CORE. Macro/rates/VIX/dollar. Verified this session.** |
| **yfinance** (Yahoo unofficial client) | Free; no published quota; aggressive undocumented rate limits reported (Unverified) | Very long for most tickers | Daily + intraday, but intraday reality is rate-limit fragile (Unverified) | Yahoo API "intended for personal use only" (client README, Verified); Yahoo ToS pages themselves 404'd this session | **CORE for daily equity/futures closes only** (SPX, NQ/QQQ, gold, VIX, DXY). Grey zone: unofficial client. |
| **Alpha Vantage** | Free key: **25 requests/day**; premium $49.99+/mo for more/some endpoints | 25+ years for stocks | Daily (free: latest **100 points**, `full` needs premium); intraday is **premium** | Vendor ToS pages are explicit; personal-use language on premium page | **Backup only** — 25/day is too small for a loop; fine for daily backfill of ≤10 tickers. Verified. |
| **Stooq** | Free (bulk + per-symbol CSV); captcha authorisation for downloads | Long history; bulk folders (daily/hourly/5-min) | Daily (world indices/fx/gold/crypto folders); hourly + 5-min bulk exist | ToS page exists (not fetched); **live endpoints JS-challenge-gated** (verified) | **Quarantine.** Not scriptable unattended this session. Bulk manual pulls only. |
| **Finnhub stocks endpoints** | Free tier exists; limits unconfirmable this session (docs are JS shell); community figure 60 calls/min (Unverified) | Quotes/candles/fundamentals endpoints exist (client README Verified); free-tier candle history reportedly restricted (Unverified) | Mixed (real-time quotes; candles D/W/M) | Vendor ToS not fetched | **Defer.** Needs a hands-on free-key test before any commitment. |

### Crypto-relevant series and why (with literature)

- **The survey the user asked for:** Fang, Ventre, Basios, Kanthan, Li, Martinez-Regoband & Wu, *Cryptocurrency Trading: A Comprehensive Survey*, arXiv:2003.11352 (v5, 28 Jan 2022), verified this session (abstract page + full text). Quotable findings from its "correlation between cryptocurrency and others" discussion:
  - > "By the effects of monetary policy and business cycles that are not controlled by the central bank, cryptocurrency is always negatively correlated with overall financial market trends. There have been some studies discussing correlations between cryptocurrencies and other financial markets."
  - On bubbles: > "correlation between cryptocurrency bubbles and indicators like volatility index (VIX) (which is a 'panic index' to measure the implied volatility of S&P…)" — i.e., VIX as a crypto-cycle indicator is already in the literature the survey reviews.
  - On gold: the survey reports Kang et al. "examined the hedging and diversification properties of gold futures versus Bitcoin prices by using dynamic conditional correlations (DCCs) and wavelet coherence" — gold as a Bitcoin hedge/diversifier is likewise supported there.
  - **Caveat (neutral):** the survey's own summary line is the authors' characterisation of a mixed literature, and it immediately notes "the correlation between cryptocurrency and other assets still requires further research." Treat crypto-stock correlation as **regime-dependent input signal, not a law**.
- **What to feed the classifier (facts per source coverage):** dollar strength (FRED broad dollar index series family, e.g. `DTWEXBGS`; Unverified identifiers — FRED's series pages unreachable this session, but the API host is reachable), US 10y / Fed-funds-era rates (FRED `DGS10`, `SOFR`, `DFF` — Unverified identifiers), **VIX** (FRED `VIXCLS`, CBOE-sourced; Alpha Vantage also has a free-key VIX endpoint but its **Index Data APIs are marked Premium** in the docs ToC — Verified), **SPX / Nasdaq / QQQ** (FRED `SP500` daily exists but is S&P-licensed data and rolling-history-limited; yfinance daily `^GSPC`, `^IXIC`, `QQQ`, `ES=F`, `NQ=F`, `GC=F`, `^VIX`, `DX-Y.NYB` is the practical path — ticker conventions widely used, Unverified from primary docs), **gold** (stooq has gold/fx folders Verified-in-archive, but live access is JS-gated; yfinance `GC=F` practical, Unverified).

### Cadence reality: daily-native macro into an hourly feature set

- **Fact:** the free layers above are daily (FRED macro series update at day frequency; equity daily bars). Intraday equities (1h) on the free web tier is where candidates fall over: Alpha Vantage intraday = premium (Verified); Yahoo intraday = rate-limit fragile (Unverified); stooq hourly bulk exists but is captcha/JS-gated (Verified).
- **Standard mechanism (cited):** a lower-frequency series joins to a higher-frequency panel by carrying the **last known value forward** until the next observation. First-party definition, pandas `merge_asof` docs (fetched 2026-11-09): > "A 'backward' search selects the last row in the right DataFrame whose 'on' key is less than or equal to the left's key." — i.e., for each hourly row, take the most recent daily/macro row at or before that hour. This *is* the last-known-value join; no vendor hype needed, pandas documents it.
- **Leakage guard that the same docs give us:** `merge_asof(..., allow_exact_matches=False)` excludes same-timestamp matches (strictly-prior only), which is the documented knob for "don't grant the model information that arrived exactly at the candle close it is predicting" (parameter semantics Verified in the docs). Design rule below.

---

## Comparison table — (b) automated stock trading from Ireland (fallback)

| Route | Official API? | Ireland availability | Automated-trading stance | Effort tier (docs-supported) |
|---|---|---|---|---|
| **Interactive Brokers Ireland** | **Yes** — Web API (REST+WS), FIX, TWS API (Python client, GPL, open source) | Yes — IBKR Ireland Ltd, regulated by the Central Bank of Ireland: "reference number C423427" (Verified) | Explicitly markets algorithmic automation: "Automate algorithmic trading strategies, advanced programmatic investing or trading systems"; "Programmatically place orders including advanced order types and algos and trade in extended/overnight trading hours" (Verified) | **High.** TWS/Gateway JVM session, 2FA re-auth, full order-type surface. Doable, but heavy ops. |
| **Alpaca** | Yes — API-first Trading/Broker API | US entity (Alpaca Securities LLC, FINRA/SIPC member — Verified); EU entity is "Alpaca Europe A.V. SLU", CNMV-regulated, "**designed primarily for B2B partnerships**" (Verified). Irish *retail individual* availability **Unverified** this session (help centre unreachable) | Explicitly API-first, 24/5 trading documented; crypto 24/7 | **Medium,** if retail intl signup is open; EU path is via partner apps, not DIY.
| **DEGIRO** | **No official public trading API** (Unverified from vendor — pages JS/consent-walled this session; consistently community-reported as none; unofficial reverse-engineered libraries exist off-vendor) | Yes, Irish retail presence | No official automation path | **Not viable** for an agent (official-API absence; unofficial libs are ToS-fragile). |
| **eToro** | **No public retail trading API** (Unverified from vendor — pages unreachable this session) | Yes, Irish retail presence | No official automation path | **Not viable** for an agent. |

### Regulator / market-structure facts

- **PDT rule (classic form) — Unverified this session (FINRA site 403-blocked):** FINRA's day-trading margin rules require a pattern day trader (4+ day trades in 5 business days in a margin account) to maintain **$25,000** equity. This rule is a FINRA member-firm obligation, i.e., it attaches to **accounts at US broker-dealers**.
- **PDT is being replaced — Verified via Alpaca's broker documentation (fetched 2026-11-09):** "FINRA has approved a comprehensive overhaul of Rule 4210… the legacy Pattern Day Trading (PDT) framework is being replaced with a modern 'intraday margin' system… By eliminating the $25,000 equity threshold and the 'four trades in five days' rule…" with "a 12-month interim transition period" after SEC approval, under FINRA's "FINRA Forward" modernisation. So any v0.3 venue plan must re-check FINRA's status at build time.
- **Does PDT bite IBKR-Ireland clients? (neutral synthesis, not verbatim primary):** IBKR Ireland's own footer identifies only **Interactive Brokers LLC** as "member NYSE - FINRA - SIPC", while Interactive Brokers Ireland Limited is "regulated by the Central Bank of Ireland" (both Verified from interactivebrokers.ie). FINRA margin rules govern FINRA member firms; an Irish retail client of IBKR Ireland Ltd is therefore not served by a FINRA member for the account relationship. **Unverified as a rule application** — IBKR's own authoritative answer should be confirmed in their docs/support before any venue work.
- **Market hours — Verified (NYSE):** "Core Trading Session: 9:30 a.m. to 4:00 p.m. ET" with pre-market from 4:00 a.m. on some venues and "Late Trading Session: 4:00 p.m. to 8:00 p.m. ET"; full annual holiday calendar with half-days (e.g., day after Thanksgiving closes 1:00 p.m. ET). 9:30–16:00 ET = **14:30–21:00 Irish time** (standard/winter offset; arithmetic, not a doc citation).
- **The 24/7 conflict (explicit):** the project's autonomy requirement is round-the-clock BTC/USDT on a 24/7 crypto venue (dry-running against Bybit per `research/venue-ireland.md`). Equity markets run ~6.5h/day on weekdays with holidays and half-days — **an equity-venue agent is idle for roughly three-quarters of the week and cannot act during weekend crypto volatility, which is when Bitcoin gap-moves concentrate**. IBKR markets "Trade Around the Clock. Access 10,000+ US Stocks and ETFs day and night." (Verified) — an overnight-session mitigation with thin-liquidity caveats, not parity with a 24/7 crypto venue.
- **Currency:** equities settle USD; the agent's base is EUR (Ireland). Multi-currency conversion/FX spreads are part of venue cost (IBKR lists 29 funding currencies — Verified from the IE site nav). No deep research done; flagged for the fallback phase.
- **Irish tax pointer (one line, not tax advice):** Irish CGT on share disposal gains is commonly cited at the **33%** standard rate; revenue.ie's CGT section moved during the fetch attempts this session, so treat the rate as **Unverified** and confirm the current Revenue page (revenue.ie → Gains, Inheritance and Gifts → CGT) with a professional before acting.

### Ireland verdict

Automated stock trading from Ireland **is viable at a cost tier**: IBKR Ireland is the one route where automated trading is officially on the product page and there is a Python path (TWS API, GPL client) plus a modern REST Web API; Alpaca is the API-first alternative with an unverified-fore-Ireland retail path; DEGIRO/eToro drop out for lack of an official API. But the venue itself contradicts the mission: **equity hours + holidays are a structural mismatch with a 24/7 autonomous crypto agent**, mitigable only partially (IBKR overnight sessions). Effort estimate: IBKR tier = a distinct infrastructure project (gateway session management, entity rules, FX funding, PDT-landscape re-verification); inputs tier = a data-pipeline feature within the existing codebase.

---

## Verdict — comparing (a) vs (b)

| Axis | (a) Stocks as signal inputs | (b) Stocks as a trading venue |
|---|---|---|
| Regulatory surface | Consumer-data terms (Yahoo ToS grey zone; FRED ToS; copyright flags on licensed series) | Broker regulation: CBI (IB Ireland), FINRA/SIPC (US entities), SEPA/FX funding, CGT reporting |
| Cost | €0 feasible (FRED key + yfinance), AV 25/day as compliant backup | Commissions + FX conversion + market-data subscriptions (IBKR) — not researched in depth here |
| Fit to 24/7 autonomy | **Good — passive inputs, updated daily, joined as-of** into hourly features; no interaction with market hours | **Poor — structurally bounded by 13:30–21:00 IST weekdays + holidays** |
| Integration difficulty | **Low.** Two HTTP fetchers + a pandas `merge_asof` join + caching | **Medium-high (IBKR)** / not viable (DEGIRO, eToro) / unverified (Alpaca retail intl) |
| Literature support | Survey (arXiv:2003.11352) documents crypto-asset correlation studies (stocks/VIX/gold/dollar) and flags them as research-grade, regime-dependent signals | Not applicable (venue question) |
| Recommendation fit | Matches the user's **signal-inputs-only** decision | Matches the **fallback** decision; conclusion: keep as fallback only |

**Difficulty rating for the inputs-only case (docs-supported):** LOW. Evidence: (1) FRED's key gate and API are reachable and free (Verified — live 400 XML naming the key doc; archived key/ToS pages); (2) the join mechanism is a documented pandas primitive, not custom code (Verified); (3) all free tiers are daily-native, eliminating the fragile intraday layer entirely (Verified for AV/FRED/stooq-cadence; Unverified for Yahoo intraday fragility). Expected build: fetcher + cache + as-of join + staleness guard; no new infrastructure.

---

## Design implications for v0.2 (neutral)

1. **Ship daily-native macro/equity inputs only.** No hourly stock feed in v0.2: every free path either is premium (Alpha Vantage intraday — Verified), rate-limit-fragile (Yahoo intraday — Unverified), or JS-gated (stooq — Verified). Daily last-known-value closes cover DXY/USD-broad, SPX, Nasdaq/QQQ, gold, VIX, rates.
2. **Join with an as-of (last-known-value) semantic** — `pandas.merge_asof(direction='backward')`; consider `allow_exact_matches=False` for the candle at the macro publication timestamp to avoid same-instant information bleed (both semantics Verified in pandas docs). Log the "observation timestamp" per macro row so backtests can enforce publication-aware joins (e.g., rates/VIX close values are safe for joins *after* their close hour, which needs an explicit timezone-aware rule).
3. **Source policy:** FRED (free key) as the CORE macro store; yfinance for daily equity/futures closes as pragmatic secondary with the Yahoo personal-use constraint acknowledged in the design doc (signal inputs, no redistribution of raw data); Alpha Vantage free key registered for compliant small-volume backfill/repair, aware of the 25/day ceiling; Finnhub parked until a free-key hands-on test; stooq quarantined for scripted use.
4. **Cache + staleness flags:** daily series must produce a feature only when the as-of row exists within a max age (e.g., >3 calendar days stale → feature set to NaN/masked), so weekends/holidays degrade gracefully instead of leaking stale values silently.
5. **Treat correlation signals as regime-dependent.** The survey quote (both directions of evidence) argues for inputs that let the classifier *learn* when equity/macro regime matters (VIX state, dollar direction, SPX momentum) rather than fixed-weight priors.
6. **Keep the venue fallback parked with explicit re-check triggers:** FINRA 4210 intraday-margin transition status (Verified as in-flight via Alpaca docs), IBKR Ireland's own PDT-applicability statement, Alpaca retail-Ireland availability, and the Irish CGT rate page (when it lives again) — all four are the open items before any venue work is justified.
7. **Mission alignment:** do not let venue-feasibility creep into v0.2 scope. The inputs path adds decision quality to a 24/7 agent; the venue path would trade that autonomy away.

---

## Contradictions and caveats found this session

- **Yahoo ToS links in yfinance's README 404 on fetch** (legal.yahoo.com terms URLs, 2026-11-09). The README itself (Verified) is the operative statement: "yfinance is not affiliated, endorsed, or vetted by Yahoo… uses Yahoo's publicly available APIs, and is intended for research and educational purposes… the Yahoo! finance API is intended for personal use only." The actual ToS text could not be inspected; rights to use downloaded data remain user-responsibility per the README.
- **Stooq's "simple free CSV endpoint" reputation is outdated.** Verified live test: `stooq.com/q/d/l/` and site pages serve a JavaScript SHA-256 proof-of-work browser-verification challenge (`/__verify` flow) to scripted HTTP clients. Scripted/Python access requires browser emulation or manual session cookies — a material operational contradiction with its common usage pattern.
- **Finnhub free-tier limits are folklore-grade.** finnhub.io docs/pricing are JS single-page apps (fetch and Wayback capture of the pricing page rendered no plan text); the widely-cited "60 API calls/minute" and free-tier candle restrictions could not be verified from a primary page this session.
- **PDT is simultaneously "active" and "being abolished."** FINRA's own pages were unreachable (403) so the classic rule could not be quoted from the regulator; meanwhile Alpaca's broker documentation (Verified) describes the approved Rule 4210 overhaul that removes the $25k/4-of-5 framework after a SEC-approved transition. Net: PDT specifics are **time-volatile**; re-verify before any margin-account plan.
- **Alpha Vantage marketing vs structure:** "free JSON APIs for realtime and historical stock market data" (docs header) coexists with intraday + daily-adjusted being **premium** and free daily returning only the latest 100 points (both Verified). The practical free tier is narrower than the headline.
- **FRED is free but not ownerless:** its ToS (Verified via archived capture) warns that individual series "may be owned by third parties and subject to copyright restrictions" and requires contacting the owner for non-personal use; licensed series on FRED (e.g., SP500 from S&P DJI, VIXCLS from CBOE) are personal-use-grade here. Same shape as the Yahoo situation, but with a clearer, regulator-issued ToS.
- **Network-blocked during research (affects Unverified marks):** fred.stlouisfed.org web docs (host unreachable from this machine; API host `api.stlouisfed.org` reachable and key-gated), finra.org (403), finnhub.io docs/pricing (JS shell), help.alpaca.markets (transport error), revenue.ie CGT section (404s/403s), legal.yahoo.com (404s). Wayback Machine (web.archive.org) snapshots of the FRED key/ToS pages and stooq's data page were used and are dated in-line.

---

## Source list (all fetched 2026-11-09 unless marked)

- yfinance README + disclaimers — https://github.com/ranaroussi/yfinance (Verified)
- Alpha Vantage documentation (intraday/daily premium markers, 25+ years, intervals) — https://www.alphavantage.co/documentation/ (Verified)
- Alpha Vantage premium page (free tier "standard API usage limit (25 API requests per day)", premium plans) — https://www.alphavantage.co/premium/ (Verified)
- FRED API key doc (archived capture dated <2026-01-07>) — https://fred.stlouisfed.org/docs/api/api_key.html via https://web.archive.org/web/20260107151459/https://fred.stlouisfed.org/docs/api/api_key.html (Verified-via-archive; live host unreachable)
- FRED API Terms of Use (archived capture dated <2026-01-01>) — https://fred.stlouisfed.org/docs/api/terms_of_use.html via https://web.archive.org/web/20260101062052/https://fred.stlouisfed.org/docs/api/terms_of_use.html (Verified-via-archive)
- FRED live API key-gate (400 XML: "Variable api_key is not set") — https://api.stlouisfed.org/fred/series?series_id=VIXCLS (Verified, live probe)
- Stooq "Free Historical Market Data" page (daily/hourly/5-min ASCII+Metastock bundles, folder inventory incl. macro, indices, fx, gold, crypto; captcha download flow) — https://stooq.com/db/h/ via https://web.archive.org/web/20251230121126/https://stooq.com/db/h/ (Verified-via-archive, dated <2025-12-30>) + live JS-challenge probe (Verified)
- Finnhub Python client (endpoint methods incl. `stock_candles`, `quote`) — https://raw.githubusercontent.com/Finnhub-Stock-API/finnhub-python/master/README.md (Verified); free-tier limits (Unverified)
- Fang et al., *Cryptocurrency Trading: A Comprehensive Survey*, arXiv:2003.11352v5 — abstract https://arxiv.org/abs/2003.11352 and full text https://ar5iv.labs.arxiv.org/html/2003.11352 (Verified, quotations above)
- pandas `merge_asof` reference (as-of join semantics, `direction`, `allow_exact_matches`) — https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html (Verified)
- Interactive Brokers Ireland — IB API product page (Web API/ FIX/TWS, automation use-cases, overnight orders) and entity/regulation footer (CBI C423427; IBKR LLC "member NYSE - FINRA - SIPC") — https://www.interactivebrokers.ie/en/trading/ib-api.php (Verified); TWS API docs intro (Python support, Campus notice) — https://interactivebrokers.github.io/tws-api/ (Verified)
- Alpaca docs: About Alpaca (Alpaca Securities LLC FINRA/SIPC), EU About (Alpaca Europe A.V. SLU, CNMV, B2B-first), Intraday-margin/PDT-end explainer — https://docs.alpaca.markets/us/docs/about-alpaca.md, https://docs.alpaca.markets/eu/docs/about-alpaca.md, https://docs.alpaca.markets/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt-1.md (Verified)
- NYSE Holidays & Trading Hours (core 9:30–16:00 ET, late session, half-days) — https://www.nyse.com/markets/hours-calendars (Verified)
- FINRA PDT investor page & Rule text — blocked (403) this session (Unverified)
- DEGIRO / eToro vendor pages — fetch attempts blocked/JS-walled this session (API-position statements Unverified)
- Irish CGT rate — revenue.ie CGT pages relocated; rate 33% not verifiable from a reached primary page this session (Unverified; not tax advice)
