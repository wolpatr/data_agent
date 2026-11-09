# Venue selection: crypto exchange for a paper-first autonomous spot-trading agent (TypeScript / CCXT), Ireland-based user

**Research date:** 2026-11-09 · **Status:** findings file (research-only, no production code) · **Method:** primary-source verification (official exchange docs/help/blog pages, regulator pages, library source) over a live-fetch session; each fact carries its dated source below.

---

## TL;DR — Recommendation

**Primary recommendation: Bybit, used via Bybit EU (the MiCA-authorised Bybit EU GmbH platform, bybit.eu), with paper trading in Phase 1 against Bybit's official API demo/testnet environments.**

- Paper-first path (non-negotiable criterion): the agent runs **unattended against Bybit's official demo/testnet APIs** from day one:
  - **Option A (zero-config, CCXT-native):** CCXT `bybit` + `exchange.set_sandbox_mode(true)` → routes to the official testnet `api-testnet.bybit.com` (verified in ccxt 4.5.92 source, `bybit.js:162-168`).
  - **Option B (most production-like, official demo service):** Bybit v5 **Demo Trading Service** at `https://api-demo.bybit.com` — demo account + demo funds provisioned via API (`POST /v5/account/demo-apply-money`), public market data identical to mainnet, orders retained 7 days (official docs: bybit-exchange.github.io/docs/v5/demo).
- Irish retail availability: Bybit EU GmbH is **FMA (Austria) CASP-authorised under MiCA** (decision dated 2025-05-28; published by the regulator 2025-05-30), services include exchange of crypto-for-funds and crypto-for-crypto — passported across the EEA, which includes Ireland. Bybit EU operates a live EU platform (bybit.eu) and markets itself as a "MiCAR-authorised provider" to European users.
- Runner-up: **OKX** (Malta MFSA MiCA licence, Jan 2025; demo trading via the production API with the `x-simulated-trading` header, CCXT-supported). Choose OKX instead if its demo environment fits the unattended-run tooling better — it is near-equivalent on every criterion.
- **Disqualified: Binance** — blocked from operating in the EU as of May 2026 (no MiCA licence; Greek application expected rejected; MiCA transition for legacy CASPs ended 1 July 2026). Its Spot Test Network is excellent but criterion (a) fails for an Irish user. **Coinbase** fails criterion (b): its Advanced Trade "sandbox" is a static mock (no live fills, no candles). **Kraken** passes (a) best of all (licensed *in Ireland*) but has **no REST/API-key spot sandbox** — paper trading exists only through the official Kraken CLI, which a CCXT-based agent cannot use directly.

---

## Comparison table

| Criterion (priority order) | Binance (binance.com) | Coinbase (Advanced Trade) | Kraken | Bybit (Bybit EU) | OKX (OKX Europe) |
|---|---|---|---|---|---|
| (a) Legally available to Irish retail for spot | **FAIL** — blocked from EU operations May 2026; no MiCA licence | PASS — MiCA (Luxembourg CSSF); Ireland migrated to MiCA entity 2025-10-23 | PASS (strongest) — licensed *by* the Central Bank of Ireland; Irish entities CBI-regulated | PASS — FMA (Austria) CASP under MiCA, 2025-05-28; EEA passporting; EU platform live (Ireland listing: verify at signup) | PASS — MiCA licence via Malta (announced 2025-01-27); EEA serving (Ireland listing: verify at signup) |
| (b) REAL paper/testnet API for unattended agent | PASS (technically) — official Spot Test Network (testnet.binance.vision), but venue is EU-blocked so unusable end-state | **WEAK** — Advanced Trade sandbox is static mocks via `api-sandbox.coinbase.com` (no auth, accounts/orders only, no candles, pre-2023 canned data) | **WEAK** — no REST/API sandbox; paper trading only via official Kraken CLI (`kraken paper`, live prices, no account) — not usable from CCXT | **PASS (strong)** — official demo trading at `api-demo.bybit.com` (demo funds via API, market data = mainnet, 7-day orders) + full testnet (`api-testnet.bybit.com`); CCXT testnet wiring in-box | **PASS (strong)** — demo trading on the production API via `x-simulated-trading: 1` header (CCXT `setSandboxMode` support verified in source); real prices |
| (c) Spot API fit: OHLCV + market orders + balances + error semantics | Excellent (not usable in EU) | Good — `/brokerage` candles/orders/accounts (CCXT `coinbase` class); mock sandbox lacks candles | Excellent | Excellent — full v5 REST/WS, market/limit, balances, error catalogue, demo/testnet parity | Excellent — full v5 REST/WS, header-gated demo |
| (d) Liquid BTC/quote pairs | Largest (N/A in EU) | High (BTC/EUR etc.); no standalone BTC/USDT | High (deep EUR book, first BTC/EUR pair 2013) | Very high BTC/USDT + BTC/EUR on EU platform | Very high BTC/USDT + BTC/EUR |
| (e) Fees for small real-money use | ~0.1% base (N/A in EU) | Higher retail tier (~0.6% taker; unverified this session) | ~0.25–0.40% Pro tiers (unverified this session) | ~0.1% base spot (unverified this session — confirm on Bybit EU fee page) | ~0.08–0.1% base spot (unverified this session) |
| CCXT (v4.5.92) confirmatory support | `setSandboxMode` → testnet.binance.vision (binance.js:210-212) | `coinbase` = Advanced Trade; **no sandbox wiring**; legacy `coinbaseexchange` sandbox only (coinbaseexchange.js:147-150) | **No sandbox wiring at all** (kraken.js) | `setSandboxMode` → `api-testnet.bybit.com` (bybit.js:162-168) | `setSandboxMode` toggles `x-simulated-trading` header (okx.js:8453-8460) |

---

## Verified facts, each with dated source

### 1. Binance — EU availability (criterion a) — VERIFIED, fails for this use case

- **Binance was blocked from operating in the European Union in May 2026.** Wikipedia's Binance article (retrieved 2026-11-09; last edited 2026-11-05) states: "In May 2026, Binance was blocked from operating in the European Union," citing Angus Berwick, *"Christine Lagarde Helped Block Binance's Foothold in Europe," The Wall Street Journal, 18 September 2026, https://www.wsj.com/finance/currencies/christine-lagarde-helped-block-binances-foothold-in-europe-d905c86d* (retrieved 19 September 2026).
- **No MiCA authorisation; legacy-transition expiry.** Same article, EU section: under MiCA, pre-existing CASPs could operate on the transitional regime only "until 1 July 2026"; "In June 2026 Reuters reported that Binance's application for a MiCA licence in Greece was expected to be rejected," which "could prevent Binance from continuing to offer crypto services across the EU after the MiCA transition period expires" (Reuters, June 2026; Binance denied and said it had received no formal indication of rejection).
- **No Austrian CASP authorisation found.** The Austrian FMA site-search for "Binance" returns **0 results** (fetched 2026-11-09: https://www.fma.gv.at/en/?s=Binance) — FMA publishes MiCA licence grants on its site (as it did for Bybit), so this is negative evidence.
- **Binance Spot Test Network capabilities (for the record).** Official site https://testnet.binance.vision (fetched 2026-11-09, page copyright © 2026 Binance.com): official Spot Test Network — login via GitHub to generate API keys (HMAC/RSA/Ed25519), REST+WS+FIX mirrors of the Spot API at `https://testnet.binance.vision/api`, `/api` endpoints only (no `/sapi`), virtual funds auto-provisioned, klines available (klines/uiKlines identical), same rate-limit/filters as production, **monthly full resets without notice**. Relevant only if Binance re-enters the EU.

### 2. Coinbase — MiCA licence + Ireland + sandbox reality (criteria a, b)

- **MiCA licence from Luxembourg CSSF; Coinbase Luxembourg S.A. is the authorised entity.** Official Coinbase help article "MiCA authorization and changes to Coinbase service" (fetched 2026-11-09: https://help.coinbase.com/en/coinbase/other-topics/other/mica-cblu).
- **Ireland is served under the MiCA entity — effective 23 October 2025.** Same help article, rollout table: "Croatia, Cyprus, Estonia, Germany, **Ireland**, Latvia, Slovenia — 23 October 2025." (Coinbase Ireland Limited remains CBI-regulated for e-money services.)
- **Licence announcement dated 20 June 2025.** Official Coinbase blog, Daniel Seifert, "Coinbase Secures MiCA Licence," **Jun 20, 2025** (fetched 2026-11-09: https://www.coinbase.com/blog/coinbase-secures-mica-licence-a-milestone-in-europes-crypto-evolution) — also notes Coinbase pre-existing national licences incl. Ireland, Germany, France, Italy, Netherlands, Spain.
- **Advanced Trade API "sandbox" = static mock, not a paper engine.** Official docs "Advanced Trade API Sandbox" (fetched 2026-11-09: https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/sandbox.md): endpoint `https://api-sandbox.coinbase.com/api/v3/brokerage/...`; "All responses are static and pre-defined"; no authentication needed; **only Accounts and Orders endpoints**; error variants via `X-Sandbox:` headers. Live check (2026-11-09): `GET /api/v3/brokerage/accounts` returned the canned account fixtures (USDC/ETH/USD/BTC, data dated 2023). **No candles, no order lifecycle, no liquidity** — fails paper-first for an hourly-candle agent. The older Coinbase Exchange sandbox (`api-public.sandbox.exchange.coinbase.com`) belongs to the legacy Exchange API (CCXT `coinbaseexchange`), not Advanced Trade.

### 3. Kraken — MiCA licence in Ireland + paper-trading reality (criteria a, b)

- **MiCA licence granted by the Central Bank of Ireland — announced 25 June 2025.** Official Kraken blog: "Kraken cements European leadership with MiCA license from Central Bank of Ireland," **June 25, 2025** (fetched via DuckDuckGo listing and fetched 2026-11-09: https://blog.kraken.com/news/mica-license-central-bank-of-ireland); corporate wire release of same date: BusinessWire, "Kraken Secures MiCA License from Central Bank of Ireland…" (2025-06-25: https://www.businesswire.com/news/home/20250625529871/en/Kraken-Secures-MiCA-License-from-Central-Bank-of-Ireland-Cementing-Leadership-in-European-Crypto-Markets). Irish Times covered it 2025-06-26.
- **Irish regulated entities, stated on Kraken's own site (fetched 2026-11-09).** kraken.com/legal/micar and kraken.com footer: "Payward Europe Solutions Limited, trading as Kraken, is regulated by the Central Bank of Ireland. Payward Global Solutions Limited, trading as Kraken, is regulated by the Central Bank of Ireland. Registered office: 70 Sir John Rogerson's Quay, Dublin, D02 R296, Ireland." Plus MiCAR policy/disclosure hub at /legal/micar.
- **Paper trading = official Kraken CLI only; no REST/API sandbox.** Kraken developer portal (fetched 2026-11-09: https://docs.kraken.com/api/): "Kraken CLI — Trade, stream and stake from the command line — with **paper trading against live market data**." Kraken CLI README (github.com/krakenfx/kraken-cli, fetched 2026-11-09): "paper trading runs on live prices with no account"; spot paper engine (`kraken workspace create <name> --mode paper`, `kraken paper buy/sell`, market+limit, configurable fee/slippage; fills at live prices) and a futures paper engine; MCP server for agent use. **This is a separate Rust CLI, not a REST test endpoint; CCXT's `kraken` class has no sandbox wiring** (verified: no `test` URLs in ccxt 4.5.92 `kraken.js`). A CCXT-based TypeScript agent cannot point `set_sandbox_mode` at Kraken.
- Prior VASP registrations incl. Ireland, Belgium, France, Italy, Netherlands, Poland, Spain (same Kraken blog post).

### 4. Bybit — MiCA authorisation in Austria + demo/testnet quality (criteria a, b)

- **Regulator-verified: Bybit EU GmbH is a MiCA CASP (decision dated 2025-05-28).** FMA Austria, "Granting of Authorisation Bybit EU GmbH," **Release Date: 30 May 2025** (fetched 2026-11-09: https://www.fma.gv.at/en/granting-of-authorisation-bybit-eu-gmbh/): authorisation pursuant to Article 63 of Regulation (EU) 2023/1114 (MiCAR) by administrative decision dated 28.05.2025; authorised services include **exchange of crypto-assets for funds, exchange of crypto-assets for other crypto-assets (**i.e., spot trading), custody, placing, transfer services**.
- **EMI Licence Aug 2026:** FMA granted Bybit Payments GmbH an electronic-money institution licence (dated 2026-08-04; https://www.fma.gv.at/konzessionserteilung-bybit-payments-gmbh/ — via FMA site, referenced in Wikipedia "Bybit", retrieved 2026-11-09).
- **EU platform live and marketed as MiCAR-authorised provider.** Bybit EU press directory (bybit.eu/sitemap/press/en-EU.html, fetched 2026-11-09) includes e.g. "Bybit EU Partners with MEXC to Support Dutch Users Transitioning to a MiCAR Authorised Provider" and Bybit EU "Recognized Across Europe" — the entity actively operates across EEA venues (Austria HQ ties, Benelux, Nordics, CEE).
- **Demo Trading Service is official, API-first, agent-suitable.** Bybit v5 API docs "Demo Trading Service" (fetched 2026-11-09: https://bybit-exchange.github.io/docs/v5/demo): demo trading account created from mainnet; REST `https://api-demo.bybit.com`, private WS `wss://stream-demo.bybit.com` (public data identical to mainnet `wss://stream.bybit.com`); **demo funds via API** `POST /v5/account/demo-apply-money` (BTC/ETH/USDT/USDC); demo orders retained **7 days**; same basic trading rules; rate limit not upgradable; supports orders, execution history, wallet balance. Also a separate standalone testnet at testnet.bybit.com (`api-testnet.bybit.com`), wired into CCXT (see §5).
- **(Confirmation, Wikipedia "Bybit" retrieved 2026-11-09, ref list)** — May 2025 FMA authorisation and 2026 EMI licence corroborated; Nov 2025: European subsidiary suspended Russian nationals, i.e., Bybit EU actively onboarding EEA users.

### 5. OKX — MiCA licence (Malta) + demo trading (criteria a, b)

- **MiCA licence via Malta.** OKX official post "Our MiCA License and Scaling OKX in Europe" dated **2025-01-27** (okx.com; surfaced via Google News RSS query, items dated 2025-01-27 sourcing https://www.okx.com — direct page fetch returned 404, see gaps); corroborated by Times of Malta, **2025-02-06**: "Two Malta-based crypto companies receive licences to operate across EU" (timesofmalta.com). OKX's own 2025-11-04 post markets "9/10 MiCA services — one of Europe's broadest MiCA licenses."
- **Post-Binance-exit EEA operations confirmed.** Finance Magnates/TradingView, **2026-08-17**: "Inflows from Binance Customers Grew More Than 8 Times: OKX Europe CEO on Post-MiCA Scene" (Google News RSS, sourced to financemagnates.com / okx.com) — OKX Europe operating under MiCA across the EEA and absorbing former Binance EU users.
- **Demo trading via production API + header.** Mechanism `x-simulated-trading: 1` verified at library level: CCXT 4.5.92 `okx.js:8453-8460` — `setSandboxMode(enable)` toggles the `x-simulated-trading` request header (`okx.js:8457`). The OKX v5 docs page (www.okx.com/docs-v5/en/) could not be fetched directly (>5 MB response) — see gaps.
- Ireland-specific country list not verified this session — see gaps.

### 6. CCXT coverage (confirmatory only; version 4.5.92 installed locally, `rg` over `js/src`)

- `binance.js:210-212` — sandbox URLs `https://testnet.binance.vision/api/v3`; `pro/binance.js:85-90` — testnet WS streams; explicit `setSandboxMode` + `sandboxMode` plumbing (`binance.js:2829-2831`).
- `bybit.js:162-168` — `test` URLs → `https://api-testnet.bybit.com` (spot+futures+v2 paths). Note: CCXT routes `bybit` sandbox to **testnet**, not to the newer `api-demo.bybit.com` demo service; use Option B by overriding the base URL per official Bybit docs if demo-accounts are needed.
- `okx.js:8457` — `this.headers['x-simulated-trading'] = '1'` when sandbox mode enabled; removed when disabled (`okx.js:8459-8460`).
- `kraken.js` — **no sandbox support** (no `test` URLs; only the literal coin name "SAND" and `'sandbox': false` metadata) — consistent with Kraken's API-level lack of a sandbox.
- `coinbase.js` — the `coinbase` class targets Advanced Trade (`https://api.coinbase.com`, `/brokerage/...` incl. `brokerage/market/products/{product_id}/candles` at line 274); **no `test` URLs** → `set_sandbox_mode` unsupported; the sandbox lives only in the legacy `coinbaseexchange` class (`coinbaseexchange.js:147-150`).

---

## Recommendation recap (mapping to criteria)

**Venue: Bybit EU (FMA/MiCA-authorised Bybit EU GmbH).**
1. **(a) Ireland legality:** MiCA CASP authorisation granted by Austria's FMA (decision 2025-05-28, published 2025-05-30) with spot exchange services in scope → passportable into Ireland; Bybit EU operates the EEA platform (bybit.eu). Confirm the Ireland country list in the signup flow.
2. **(b) Paper-first (non-negotiable):** run Phase 1 unattended on **CCXT `bybit` with `set_sandbox_mode(true)`** (official testnet) — or, for the closest-to-production experience, point the client at **`https://api-demo.bybit.com`** (official demo trading; demo funds via API; public market data = mainnet; 7-day order retention). Both are documented for programmatic/unattended use.
3. **(c) API depth:** full v5 REST/WS for OHLCV (1h candles), market orders, balances, execution history, with an explicit error-code catalogue; CCXT covers everything used here.
4. **(d) Liquidity:** BTC/USDT among the world's deepest; EU platform additionally offers EUR-quoted pairs. For the real-money phase under MiCA, validate the compliant quote assets (EUR and/or an authorised e-money token) on the EEA platform — see gaps.
5. **(e) Fees:** base spot fee ~0.1% (widely published; **not verified this session** — confirm on bybit.eu fee schedule before the real-money phase).

**Fallback ranking:** OKX Europe (Malta MiCA; demo trading header; CCXT-supported) → Kraken (best Irish regulatory footprint; usable only if the paper phase can run via the official Kraken CLI rather than CCXT) → Coinbase (legally superb in Ireland; paper story inadequate).

---

## Gaps and uncertainties to record on the map

1. **Bybit EU country list for Ireland not individually verified** (EEA passporting + active EU operations strongly imply availability; verify the Ireland option exists in the bybit.eu signup/KYC flow before committing).
2. **OKX Irish availability not individually verified**; and OKX's MiCA licence page + v5 demo docs could not be fetched directly (404 / >5 MB) — licence verified via Google News RSS metadata, OKX's own RSS item (2025-01-27), and Times of Malta (2025-02-06); demo mechanism verified via CCXT source. Re-verify on mfsa.mt register and okx.com docs before relying on it.
3. **Binance EU-block facts rest on dated secondary reporting** (WSJ 2026-09-18; Reuters June 2026 — both paywalled, read via Wikipedia citations dated 2026-11-05) plus negative evidence on fma.gv.at. If Binance secures MiCA authorisation and re-enters the EU later, the decision should be revisited — its Spot Test Network remains the most mature sandbox in the industry.
4. **Regulator-register cross-check pending:** ESMA's central MiCA CASP register and national registers (CBI registers.centralbank.ie, MFSA, CSSF, FMA company database) were not machine-verifiable this session (404/JS-heavy pages). Before the real-money phase, re-check every licence on the registers themselves.
5. **MiCA stablecoin/compliant-quote-asset status unverified:** whether the agent's eventual real-money pair on an EEA platform can be BTC/USDT is unconfirmed (USDT's EMT/ART authorisation status was not researched this session); plan for BTC/EUR or an authorised stablecoin pair.
6. **Fee schedules not verified from official pages this session** (fee pages are JS-rendered); treat fee numbers in the table as approximate until confirmed.
7. **Bybit demo orders expire after 7 days** (official docs) — acceptable for hourly-candle paper runs but schedule periodic re-top-up of demo funds and expect demo-account resets during long unattended sessions; testnet does not have this exact constraint but resets state periodically too (Binance testnet documents monthly resets as an analogue — verify Bybit testnet reset policy empirically).

---

## Note

This document is an **infrastructure/venue-selection analysis for a software agent**, not investment advice; nothing here recommends any crypto asset, trade, or position, and licensing facts above describe platform legality of services, not the merits of trading.
