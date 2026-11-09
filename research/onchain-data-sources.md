# On-chain data sources — fact-finding (v0.2 stretch input)

**Research date:** 2026-11-09 · **Status:** findings file (research-only; no decisions made — the "should on-chain earn its place" call is explicitly out of scope) · **Method:** primary-source verification in one live-fetch session: vendor pricing/docs pages, live API probes, and the three assigned project papers. Every plan/limit was fetched or probed on **2026-11-09** unless marked `[Unverified]`. Contradictions are flagged in a dedicated section.

**Context:** freqtrade harness v0.1 in dry-run (BTC/USDT, Bybit spot, 1h candles, Python via uv). Next phase (v0.2): multi-source ML-classifier Decide across a small static USDT pair set, walk-forward-disciplined. On-chain metrics are a **decided STRETCH source** that must earn its place in walk-forward evidence.

**Scope note (BTC vs EVM):** the harness trades BTC/USDT. Several "on-chain" feeds below are EVM-chain explorers or DeFi-focused, and simply do not carry Bitcoin network metrics. This is stated per feed.

---

## TL;DR summary table

| Feed | Cost / free tier (verified 2026-11-09) | Historical depth | Native cadence vs our 1h candles | Python access | Verified |
|---|---|---|---|---|---|
| **Glassnode** | Free "Standard": T1 metrics, **24h**, Studio web only, **no API**. Advanced **$49/mo** (annual): 300+ metrics, **24h resolution per pricing page**, Light API (1d, 14d history, 50 calls/day). Professional **from $584/mo** (annual): 1,500+ metrics, **up to 10-min resolution, 15+ yrs**, full API = **credit-based add-on** (1 credit per BTC metric call) | Advanced 4 yr; Pro up to 15+ yr | Free/Advanced daily; **hourly+ on-chain only on Professional** | REST/JSON, CLI, CSV/JSON, MCP (Pro features credit-metered) | ✅ pricing + docs |
| **CryptoQuant** | Free "Basic": daily metrics, **3 yr history**, API = **market data only** (10K credits/mo). Advanced $39/mo (monthly; $29/yr): **hourly/block-level viewing**, 300K credits, still **market-data-only API**. Professional **$109/mo ($99/yr)**: **on-chain API endpoints — but daily resolution** — 500K credits, 120 req/min, daily CSV. Premium **$799/mo** (annual only): CSV for **all resolutions**, unlimited credits | Basic 3 yr; Advanced+ full history | Free/Advanced daily; on-chain API daily; **hourly on-chain data effectively only via Premium $799 CSV** | REST JSON API (keys on every plan incl. free) | ✅ pricing + FAQ |
| **Coin Metrics Community** | **Free, no key.** Community API + community CSV files (subset of metrics/assets); no client support for Community users | Single daily CSV per asset (btc.csv = 2.4 MB, full daily sample) | **Daily** (verified empirically) | REST JSON (`/v4/timeseries/asset-metrics`) + raw CSV | ✅ live probes |
| **Dune Analytics** | **Free = view-only: no query execution, no API.** New accounts: 14-day trial with Plus features, 2,500 trial credits. Analyst **$75/mo** (4,000 credits/mo); Plus **$399/mo** (25,000 credits/mo); extra credits billed as used; API export billed per MB | Raw chain tables as ingested (100+ chains; docs index seen today lists EVM networks; **BTC raw coverage `[Unverified]`**) | Any cadence you author (hourly aggregates possible) — but each execution costs credits | REST + official Python SDK | ✅ docs |
| **DefiLlama** | **Free, open, no key** (`api.llama.fi`, 31 free endpoints; rate limit published only as "Standard"). Pro API is a separate $300/mo service | Full TVL series (3,331 points fetched today) | **Daily** (verified empirically for TVL + stablecoins) | REST JSON | ✅ docs + probes. **Caveat:** DeFi/TVL/stablecoins only — **no BTC network metrics** |
| **Etherscan** | Free key: **3 calls/sec, 100k calls/day, community endpoints, "Personal & Research use"**; paid from $49→$399+/mo; commercial terms from $299/mo tier | Full raw tx/block history (EVM chains) | Raw layer only — you **assemble hourly aggregates yourself**; **Ethereum-family chains only, no BTC** | REST JSON (V2 = one key, 50+ EVM chains) | ✅ pricing page |
| **Blockchain.com charts** | **Free, no key** (`api.blockchain.info/charts/...`) | BTC network stats back years (not audited per chart) | **Daily** (`"period":"day"` verified) | Simple REST JSON | ✅ live probe |
| **Santiment** | Free $0: **30-day lag** in Sanbase, CSV limited to 2 yr; Pro $49/mo; **Max $249/mo = real-time API "no restrictions or time-lag"** (min plan for real-time API). Per FAQ "All Sanbase subscriptions offer some level of access to the API" | Pro/Max: full historical | Mostly daily/sub-daily vendor series; real-time API only at Max tier | SanAPI (Python-friendly REST) | ✅ pricing + FAQ; exact free-tier API rate limits `[Unverified]` |
| **CryptoCompare / CCData** | Portal now JS-only, rebranded "CoinDesk APIs" — pricing **not verifiable from static pages this session** | — | — | REST | ❌ **[Unverified]** |

---

## 1. Feeds inventory — verified detail per feed

### 1.1 Glassnode — VERIFIED (pricing page + docs)

- Plans (https://studio.glassnode.com/pricing, fetched 2026-11-09; prices exclude VAT):
  - **Advanced — $49/mo billed annually.** 300+ metrics (Metric Catalog: 40+ on-chain) at **Resolution: 24h**, history **4 Years**, includes **API Light: 14d history, daily resolution (1d), 50 calls/downloads per day**. License: **Personal Use**.
  - **Professional — from $584/mo billed annually.** Up to 1,500+ metrics (570+ on-chain) spanning On-chain/Futures/Options/ETFs, **Resolution: up to 10 minutes**, history **up to 15+ years**; **Professional API: "Matching your Studio access"**, usage **credit-based** ("choose between 50, 5,000, 50,000, 500,000, 5,000,000, and unlimited credits per month"; "API calls cost 1 credit for Bitcoin and 2 credits for any altcoin"). License: Commercial Use. Point-in-Time (immutable, backtest-safe) metrics: Professional.
- Docs (https://docs.glassnode.com/basic-api/api.md, fetched 2026-11-09): "The Glassnode API is available to **Professional subscribers**… **Advanced** subscribers have access to the more limited **Light API**"; Light API = "limited to 14 days of history, restricted to daily (`1d`) resolution, capped at 50 calls per day, no bulk endpoints."
- Docs FAQ (https://docs.glassnode.com/further-information/faq.md, fetched 2026-11-09): "A **Standard (Free)** account will have access to all Basic metrics at a **24 hour resolution**. The Advanced subscription will have access to all Basic and Essential metrics at **up to a 1 hour resolution** (as it is available). A Professional subscription … up to a **10-minute resolution** (as it is available)." Also: downloadable JSON/CSV files are **Professional-only**.
- Granularity reality: **hourly on-chain resolution is claimed in the docs-FAQ for paid Advanced, but contradicted by today's pricing page (24h on Advanced)** — see §Contradictions. The pricing-page reading makes "hourly on-chain" a Professional feature. Either way, the free tier is **24h, web-only, no API**.
- Python access: REST/JSON (docs give a `requests` + `pandas` example), plus Glassnode CLI and Excel add-in; download of CSV/JSON files gated behind Professional.
- Terms: licenses split **Personal Use** (Advanced) vs **Commercial Use** (Professional); redistribution Professional-only.

### 1.2 CryptoQuant — VERIFIED (pricing page)

Source: https://cryptoquant.com/pricing, fetched 2026-11-09.

- **Basic — Free**: "Basic metrics; **Low metric resolution (Daily)**; **3 years historic data**; 1 alert; **API access: market data**; 10K API credits/mo; 5 AI responses/day."
- **Advanced — $39/mo monthly, $29/mo billed yearly**: "High metric resolution (**Hourly, Block-level**); Full historic data; 5 Pro chart layouts; 5 alerts; **API access: market data** (300K credits/mo)."
- **Professional — $109/mo monthly, $99/mo billed yearly**: "All assets & advanced metrics; 30 Pro chart layouts; 20 alerts; **CSV download — limited** (daily-resolution chart CSV per FAQ); Research reports; **API access: market data and on-chain data** (500K credits/mo)." FAQ detail: "Professional also unlocks **on-chain API endpoints (daily resolution)**, 500,000 monthly credits, 120 requests/min and daily-resolution chart CSV download."
- **Premium — $799/mo, annual billing only**: "Everything in Professional and: 100 alerts; **CSV download** (all resolutions per FAQ); API access: market data and on-chain data; **Unlimited API credits**."
- Resolution FAQ quote: "Block resolution is the shortest unit for the on-chain data, meaning that data is updated whenever a new block is created… In order to view real-time data in block and hour resolution, **you must subscribe to an Advanced or higher plan**." Note the distinction: *viewing* hourly charts starts at Advanced, but the *on-chain API* starts at Professional and is **daily-resolution** there; hourly-resolution on-chain CSV is Premium.
- Terms: personal-use licence for downloads; non-refundable; 1 user/account; 7-day Advanced trial (payment method on file).

### 1.3 Coin Metrics — Community (free) — VERIFIED by live probe

- **Community API, no key required** (probed 2026-11-09):
  `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=AdrActCnt,CapMrktCurUSD,FlowInExNtv&page_size=3`
  → returned daily rows for BTC up to the previous day, with recent rows flagged `"FlowInExNtv-status": "flash"` plus `*-status-time` stamps (i.e., recent points are **pre-finalized and get revised later**).
- **Community CSV** (probed 2026-11-09): https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv → HTTP 200, 2.4 MB. Header verified to include, at daily `time` frequency: `AdrActCnt` (active addresses), `CapMVRVCur` (**MVRV**), `FlowInExNtv/FlowInExUSD` + `FlowOutExNtv/FlowOutExUSD` (**centralized-exchange netflow inputs**), `HashRate`, `BlkCnt`, `FeeTotNtv`, `IssTotNtv/USD`, `PriceUSD`/`ReferenceRateUSD`, `Sply*` supply metrics, `AssetEODCompletionTime` (EOD completion timestamp). Sample rows (2023-07-29 → 2023-07-31) confirm **one row per day**.
- Community = a subset of the full catalog (no client support for Community users per https://docs.coinmetrics.io/). Full/Pro asset-metrics (hourly frequencies etc.) are paid; paid pricing is quote-based (no public per-seat page found — `[Unverified]`).
- **No hourly on-chain metrics in the free community tier** (verified: community `time` buckets are daily).

### 1.4 Dune Analytics — VERIFIED (docs)

Sources (fetched 2026-11-09): https://dune.com/pricing, https://docs.dune.com/learning/how-tos/pricing-faqs.md, https://docs.dune.com/resources/credits-billing/how-credits-work.md.

- **Free tier is view-only**: "Free access is view-only: you can browse dashboards and queries… It does not include monthly credits, query execution, or API access. New accounts start with a 14-day trial with Plus plan features and 2,500 **total** credits" (trial allowance, ends at 14 days **or** when credits run out; free/trial cannot buy extra credits).
- Plans: **Analyst $75/mo** (annual: $65/mo) — 4,000 credits/mo; **Plus $399/mo** (annual: $349/mo) — 25,000 credits/mo; Enterprise custom. Credits are usage-based ("reflect compute actually used"); no published per-execution formula. API export on current plans billed by **exported MB** (API billing doc).
- You can compute *any* cadence (e.g., hourly BTC-bridge flows, exchange-wallet balances) from raw tables — cost is credits.
- **Coverage caveat:** the docs index fetched today enumerates EVM networks (and some non-EVM like Sei/Solan­a-style chains in catalog listings) — **raw Bitcoin data availability on Dune was not confirmed in today's index** `[Unverified]`.
- Python: official SDK (docs.dune.com/api-reference/sdks/python.md).

### 1.5 DefiLlama — VERIFIED (docs + live probes)

- Official docs (fetched 2026-11-09 via https://api-docs.defillama.com/llms.txt): "**Free API** — Base URL https://api.llama.fi — **Auth Required: No** — Rate Limit: Standard — 31 endpoints." Pro API is an entirely separate service at `pro-api.llama.fi`/`{KEY}` — **$300/mo**; no query-param/apikey mixing.
- Empirical probes (2026-11-09): `/v2/historicalChainTvl` → **3,331 points, daily spacing verified**; `https://stablecoins.llama.fi/stablecoincharts/all` → **last 20 points all +24h** (daily). `api.coins.llama.fi` was unreachable from this machine during the session (DNS) `[not retried further]`.
- **Fit caveat:** DefiLlama is **DeFi data** (TVL, fees, stablecoins, bridges) — it does **not** provide BTC network metrics (active addresses, MVRV, hash rate). For a BTC/USDT harness it can only supply derivative-market-context series (e.g., stablecoin mktcap), not BTC on-chain features.
- No numeric published rate limit in current docs ("Standard") `[Unverified number]`.

### 1.6 Etherscan (+ blockchain-native free APIs) — VERIFIED (pricing page + probe)

- https://etherscan.io/apis (fetched 2026-11-09): **Free — $0**: "**3 calls/second** limit, Up to **100,000 API calls/day**, Selected chains (90% coverage), **Community endpoints only**", license: **Personal & Research use**. Paid: Lite $49/mo (5 req/s), Standard $199/mo (10 req/s, Pro endpoints), Advanced $299/mo (**Commercial Application use** begins here), Professional $399/mo (30 req/s, 1M/day), Pro Plus $899/mo. **Etherscan API V2** = one key across **50+ EVM chains** (docs.etherscan.io).
- Nature of the data: raw balances/txs/logs per address/block — **no aggregated metric timeseries**; hourly aggregates (e.g., net flows of a known exchange-wallet cluster) would be self-assembled, and history assembly is limited by the daily call budget on free.
- **No Bitcoin**: Etherscan covers EVM chains only — irrelevant for BTC/USDT network metrics itself, relevant for any EVM-USDT pair in the static set.
- Blockchain.com charts API — live probe (2026-11-09): `https://api.blockchain.info/charts/n-transactions?timespan=5days&format=json` → `{"period":"day", ...}` with **daily** buckets, **no API key required**. Free BTC network counters (transaction count, hash rate, miners' revenue, unique addresses, etc.), trivially fetched in Python. Historical depth per chart not audited today.

### 1.7 Santiment — VERIFIED (pricing page)

Source: https://santiment.net/pricing/ (fetched 2026-11-09).

- **Free — $0**: "**30-day lag** in Sanbase"; chart CSV download "**Limited to 2 years**"; limited screener; "Metrics — Full access" to the metrics catalog as charts (with lag/watermark/CSV limits).
- **Sanbase Pro — $49/mo** ($529/yr): present-day + full historical data in Sanbase, Google Sheets plugin, limited reports.
- **Sanbase Max — $249/mo** ($2,700/yr): "**full API access to real-time data with no restrictions or time-lag**" (FAQ: "**Sanbase Max is the minimum plan required for accessing the real-time API data with no restrictions or time-lag**"); 20 alerts; full screener.
- FAQ: "**All Sanbase subscriptions offer some level of access to the API**" (i.e., the free tier's API access exists but inherits the 30-day lag / limitations `[Unverified details]`). Coverage FAQ: "As of February 2026 we cover Bitcoin, Ethereum, XRPL, BNB Chain, Bitcoin Cash, Litecoin, Cardano, Dogecoin, ICP, Polygon, Avalanche, Optimism, and Arbitrum… Available on-chain metrics vary depending on the blockchain."
- On-chain metrics are mostly **daily/sampled**; exact free-tier API rate limits not verified this session `[Unverified]` (academy SanAPI page 404'd during fetch).

### 1.8 CryptoCompare / CCData — UNVERIFIED this session

- https://developers.cryptocompare.com/landing/pricing (fetched 2026-11-09) is a **JS-only Nuxt SPA**, rebranded to "**CoinDesk APIs**" (config exposes ` developers.coindesk.com`, `data-api.ccdata.io`); **no static pricing text retrievable**. Widely-cited legacy facts (free key ≈ 100k calls/mo; some blockchain-data endpoints paid) could not be confirmed and are treated as **stale until re-verified**.

---

## 2. Which metrics the literature ties to crypto returns

### 2.1 arXiv 2003.11352 — *Cryptocurrency Trading: A Comprehensive Survey* (Fang et al.)

URL: https://arxiv.org/abs/2003.11352. Full text fetched and grepped (ar5iv HTML) on 2026-11-09.

- **§3.3.2 Machine Learning Technology** (verbatim quote):
  > "We may divide the input into several groups of features, for example, those based on **Economic indicators** (such as, gross domestic product indicator, interest rates, etc.), **Social indicators (Google Trends, Twitter, etc.)**, **Technical indicators (price, volume, etc.)** and other **Seasonal indicators** (time of day, day of the week, etc.)."
  
  **No on-chain/blockchain-metric feature bucket appears in the flagship survey's own feature taxonomy.**
- **§7.2.4 Sentiment Analysis**: the survey's most concrete return-predictability claims at short horizons come from *social* data, not on-chain: Smuts [190] (LSTM on Google Trends + Telegram/VADER, "76% accuracy… in predicting hourly prices", H1 2018); Nasir et al. [192] ("Google searches exert significant influence on Bitcoin returns, especially in the short-term intervals"); Kristoufek [193] (Google Trends/Wikipedia ↔ price); Li et al. [196] (hourly Twitter-sentiment XGBoost); Lamon et al. [189] (daily news + Twitter, LR best).
- **§10.4 Datasets used in Cryptocurrency Trading**: the reviewed dataset table is dominated by price/volume, LOB, Twitter/Reddit/Telegram, Google Trends; closest to "on-chain" are (a) **Coin Metrics** as a source for one bubble/crash study and (b) an **MIT Bitcoin transaction-network graph dataset [307]** (senseable2015-6.mit.edu/bitcoin) used for transaction-network prediction — network *graphs*, not timeshares of on-chain indicators.
- Closest supply-side variables in the review: Yao et al. [186] used "market capitalization, trading volume, **circulating supply and maximum supply**" with RNN/LSTM — listing/exchange-side data, still not on-chain metrics.
- **Bottom line (fact):** the survey's reviewed evidence ties returns to market microstructure + social/search data; on-chain metrics appear only at the datasets-table margin, with no quotable finding that isolates on-chain metrics as a return driver.

### 2.2 arXiv 2606.00060 — *Machine Learning-Based Bitcoin Trading Under Transaction Costs: Evidence From Walk-Forward Forecasting* (Bysik & Ślepaczuk, June 2026)

URL: https://arxiv.org/abs/2606.00060. This is the single closest published analogue to our v0.2 (hourly BTC/USDT + walk-forward). Full text fetched and read on 2026-11-09.

- Setup (verbatim): "approximately **70,000 hourly BTC/USDT observations** and a **27-fold walk-forward protocol** covering the 2018–2025 out-of-sample evaluation period"; architectures XGBoost / LSTM / iTransformer; costs 10 bps.
- **§4.3 Feature engineering** (verbatim): "Three nested feature sets are evaluated. The **first contains only OHLCV variables**. The second augments OHLCV data with selected technical-analysis features. The third further adds **EGARCH-derived volatility-regime features**." — **No on-chain data anywhere in the study.**
- Findings (verbatim fragments): naive sign strategies "collapse after transaction costs because they trade too frequently"; "the cost-aware filter reduces turnover by more than an order of magnitude"; best long-only cost-aware XGBoost "annualised return exceeds 65% and the Sharpe ratio is above unity", but "formal Sharpe-ratio comparisons against the passive benchmark do not reject after bootstrap adjustment"; on features (H3, §5.3): "technical indicators improve performance in selected long-only configurations… EGARCH-derived features do not deliver a uniformly robust incremental gain"; "the results point to **execution design as the main driver of economic performance**."
- **Fact for the stretch decision:** the paper provides *no* walk-forward evidence for on-chain features at any cadence; it also demonstrates (on our exact market/granularity) that at 1h the action is in execution discipline and turnover, with feature enrichment only conditionally helpful — i.e., an on-chain stretch starts from an evidence gap.

### 2.3 arXiv 2407.18334 — *A Comprehensive Analysis of Machine Learning Models for Algorithmic Trading of Bitcoin* (Jabbar & Jalil)

URL: https://arxiv.org/abs/2407.18334. Full text fetched on 2026-11-09.

- **§III-A Data** (verbatim): "our study leverages a detailed **dataset of Bitcoin prices**, publicly available since the inception of Bitcoin trading in 2013"; train Jan 2013–Jan 2023, backtest Feb–Jul 2023, forward test Aug–Oct 2023; features = raw prices + "a range of technical indicators" (Accumulation/Distribution, Parabolic SAR, etc.) over rolling windows of 1/7/14/21/28 days.
- 41 models (21 classifiers, 20 regressors); "Random Forest and Stochastic Gradient Descent, outperform others in terms of profit and risk management."
- **Fact:** price + technical indicators only; **no on-chain features**; literature-review section mentions Twitter-sentiment studies ([15]) but no on-chain metric studies.

### 2.4 Metric-by-metric mapping (facts, incl. native cadence)

| Metric | Where it exists today | Native cadence | Standing in the three assigned papers |
|---|---|---|---|
| **Centralized-exchange netflows** | Coin Metrics **Community (free)**: `FlowInExNtv/USD`, `FlowOutExNtv/USD` (verified). CryptoQuant: on-chain API from **Professional $99/mo** (daily res). Glassnode: `FlowInEx` family, Pro tier | **Daily** | **Untested** in all three; survey §10.4 lists Coin Metrics only as a bubble/crash dataset source |
| **Active addresses** | CM Community `AdrActCnt` (free, verified); Glassnode T1 Basic (free @24h web); CryptoQuant daily on Basic | **Daily** | Untested in all three |
| **MVRV** | CM Community `CapMVRVCur` (free, verified); Glassnode (flagship metric; paid tiers for API); CryptoQuant "Advanced Indicator" | **Daily** (on-chain realized-cap math) | Untested; Santiment markets an MVRV tutorial (marketing, not evidence) |
| **SOPR** | Glassnode, CryptoQuant (paid tiers) | **Daily** | Untested — term does not appear in any of the three papers |
| **Funding rate / perp basis** | **Derivatives-market data, not on-chain** (classification note). From **Bybit's own API** directly (v5 funding endpoints) — free and native to our venue. Also on Glassnode/CryptoQuant as off-chain indicators | **5m–1h (exchange-native)** | Outside 2606.00060's scope (spot-only); not classified "on-chain" in any source reviewed |
| **Hash rate** | CM Community `HashRate` (free, verified); blockchain.com charts (free, daily); Glassnode "Health" category | **Daily** | Untested in all three |
| **Whale transfers / wallet clusters** | Glassnode **entity-adjusted / per-exchange** metrics (Advanced/Professional); CryptoQuant per-exchange breakdowns; "whale-transfer" standalone products (Whale Alert etc.) `[pricing Unverified this session]` | Daily–sub-daily (vendor) | Untested; nothing quotable in the reviewed papers |
| **Supply / realized-cap variables** | CM Community `Sply*`, `Cap*` (verified in CSV header) | **Daily** | Survey mentions circulating/max supply features only via Yao et al. [186] (market-cap/supply from listings) |

---

## 3. Effort vs evidence — neutral fact summary

1. **Free aggregated on-chain metrics at 1h cadence: none found, verified.** Every free option is daily-native: Glassnode Free (24h, no API), CryptoQuant Basic (daily, 3-yr), Coin Metrics Community (daily), blockchain.com charts (daily), DefiLlama (daily, DeFi-only), Dune free (view-only, cannot execute), Etherscan (raw-only, EVM chains, no BTC).
2. **Paid hourly on-chain is expensive, verified.** Glassnode 1h→10-min on-chain resolution + full API starts at **Professional (from $584/mo annual)** *plus* credit costs (1 credit/BTC call). CryptoQuant's on-chain **API** is daily-resolution even on Professional ($99/mo); hourly-resolution on-chain CSV is **Premium ($799/mo)**. A "1h on-chain signal" therefore costs **$584–799+/mo** from either vendor, before any usage-based add-on.
3. **Self-assembled hourly on-chain (Dune / Etherscan route):** possible in principle; Dune's free tier no longer executes queries or API calls (view-only) → Analyst at $75/mo with metered credits; Etherscan is EVM-only (and so leaves BTC uncovered). Dune's raw-Bitcoin coverage itself is unverified today.
4. **Daily-native feeds are usable against 1h candles only as step-function features** (24 identical bars per on-chain value, with alignment/forward-fill choices), and all carry **vendor-revision leakage risk**: Coin Metrics flags recent values as `flash` until finalized (verified in the free API today); Glassnode documents "Data Mutations, Reprocessing… Finalization" and sells immutable **Point-in-Time** metrics on the Professional tier for exactly this backtest-integrity reason.
5. **The literature offers no 1h on-chain evidence base**: none of the three assigned papers uses on-chain features; the survey's feature taxonomy has no on-chain bucket; the walk-forward paper closest to our setup (2606.00060) is OHLCV+TA+EGARCH-only and finds execution discipline (cost-aware filter) the main driver, feature enrichment only conditionally supported. By contrast, **funding/basis (derivatives, not on-chain)** is venue-native (Bybit API) and sub-hourly — but that classification is a definitional choice, out of scope here.

---

## Design implications for v0.2 (neutral — decisions deliberately not made here)

- **Granularity vs 1h-candle reality, stated plainly:** as of 2026-11-09 there is **no verified free feed providing aggregated BTC on-chain metrics at 1h cadence**. If on-chain enters v0.2 without a $584–799/mo subscription, it enters as **daily-native data resampled onto 1h candles** (a 24-bar step function). That is a different modeling assumption from "hourly on-chain signal," and under walk-forward discipline it implies (a) explicit lag/alignment rules (e.g., use yesterday's finalized daily value only from its publication timestamp onward), (b) a decision to treat on-chain features as slow/low-frequency relatives of the 1h price process, and (c) a point-in-time data policy for vendor revisions.
- **Point-in-time discipline is obtainable at the free tier** from Coin Metrics Community (`*-status: flash` fields + CSV `*EODCompletionTime` columns), which is relevant to constructing a leakage-safe daily on-chain panel.
- The only two "hourly-ish" non-vendor paths are: **Dune** (custom SQL → hourly aggregates; costs credits, free tier blocked; BTC coverage unverified) and **Etherscan-style raw assembly** (EVM-only, not BTC). Neither is a BTC network-metrics feed today.
- **On-chain is not the literature's evidence base for 1h decisions.** The assigned sources tie short-horizon predictability to sentiment/search data (survey §7.2.4) and, empirically, to execution design (2606.00060); on-chain metrics are absent from all three. Any stretch case must therefore be built from fresh walk-forward evidence on our own data, per the project's stated discipline.
- **Contradictions to resolve before buying anything:** Glassnode's docs-FAQ (Advanced = "up to 1 hour resolution") vs its current pricing page (Advanced = 24h; 10-min on Professional) — § below. The practical reading of today's pricing page: hourly on-chain = Professional.

---

## Contradictions & caveats (flagged)

1. **Glassnode — Advanced resolution:** docs FAQ (fetched today): "The Advanced subscription will have access to all Basic and Essential metrics at **up to a 1 hour resolution**." Current pricing page (fetched today): Advanced = "**Resolution 24h**," 300+ metrics; "**up to 10 minutes**" and "1,500+ metrics" only on Professional. Directly contradictory claims from the same vendor on the same day; the pricing page (product surface) is treated as current reality, the docs FAQ as stale — flagged, not adjudicated.
2. **Glassnode — metrics/asset counts:** docs FAQ says "over **800** different metrics… over **500** ERC-20 assets"; marketing/pricing pages today say "**1,700+ metrics**" / "**1,500+ assets** / 15+ years." Consistent with an old FAQ, not a conflict of substance, but cited numbers should always carry their source date.
3. **Glassnode — Advanced API access:** pricing-table row shows "API Light: 14d history / 1d resolution / 50 calls per day" under Advanced, consistent with docs ("Light API is the API available to Advanced subscribers"), yet the same pricing page's FAQ answers "API access is **not included** in the Advanced plan." Read together: the **full Professional API** is the paid add-on; **Light API** ships with Advanced. Both sources quoted above; flagged for anyone building against Glassnode.
4. **CryptoQuant — "hourly" is tiered by medium:** hourly/block *chart viewing* is available on Advanced ($39/mo), but the on-chain **API** only exists from Professional ($99/mo) and is **daily-resolution** there; hourly-res on-chain **CSV** only on Premium ($799/mo). Naive readings of the plan ladder ("Advanced = Hourly, Block-level") overstate what an API-only integration would get.
5. **Dune — free tier changed:** older community knowledge ("2,500 free credits *per month*, API included") is now wrong; today's docs say free is **view-only** and the 2,500 credits are a one-time **trial** allowance. Any older analysis of Dune feasibility is stale.
6. **CryptoCompare pricing unverifiable** this session (JS-only rebranded portal) — treat all CryptoCompare plan facts as unverified as of 2026-11-09.
7. **Dune Bitcoin coverage unverified** from today's docs index (EVM-network catalog pages enumerated; no Bitcoin tree visible in the index fetched). Must be confirmed in the Data Explorer before any Dune-based BTC design decision.

---

## Session-verified probes (raw evidence, 2026-11-09)

- Coin Metrics community API: `GET community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=AdrActCnt,CapMrktCurUSD,FlowInExNtv&page_size=3` → daily rows, BTC up to previous day, `flash` statuses.
- Coin Metrics community CSV: `GET raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv` (HEAD: 200 OK, 2,482,497 bytes; header + sample rows read).
- Blockchain.com: `GET api.blockchain.info/charts/n-transactions?timespan=5days&format=json` → 200, `period: "day"`.
- DefiLlama: `GET api.llama.fi/v2/historicalChainTvl` → 3,331 points, daily; `GET stablecoins.llama.fi/stablecoincharts/all` → last 20 points spaced +24h.
- Vendor pages fetched: glassnode.com/pricing; studio.glassnode.com/pricing; docs.glassnode.com/basic-api/api.md + /further-information/faq.md; cryptoquant.com/pricing; dune.com/pricing + two docs.dune.com markdown pages; api-docs.defillama.com (llms.txt); etherscan.io/apis; santiment.net/pricing/; developers.cryptocompare.com/landing/pricing (JS-only shell recovered).
- Papers fetched: ar5iv HTML of 2003.11352, 2606.00060, 2407.18334; grep/read used for the verbatim quotes above.
