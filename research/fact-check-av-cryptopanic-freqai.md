# Fact-check — Alpha Vantage schema, CryptoPanic auth, FreqAI config keys (v0.2 spec inputs)

**Date:** 2026-11-09
**Scope:** exact API facts needed by the v0.2 build: (1) Alpha Vantage `NEWS_SENTIMENT` surface, (2) CryptoPanic API v2 auth/shape/limits, (3) Freqtrade FreqAI config keys (spot `include_corr_pairlist`, minimal `freqai` block, model selection), (4) Bybit spot taker fee for dry-run. RESEARCH ONLY — this file is the only write.
**Method:** every checked item cites the primary page or live primary response read **this session** (2026-11-09). `✅ Verified` = read against the cited primary source this session (or its JSON response). `⚠️ Unverified` = secondhand / could not render this session — do not build on it. JS-only pages that returned no content to our fetcher are annotated with how the fact was actually sighted.

---

## 1. Alpha Vantage — `NEWS_SENTIMENT`

Docs: https://www.alphavantage.co/documentation/ → section **"Market News & Sentiment"** (under "Alpha Intelligence™"). Endpoint base for every AV function: `https://www.alphavantage.co/query`.

### 1.1 Query surface — ✅ Verified (docs text quoted verbatim)

- **Required:** `function=NEWS_SENTIMENT`, `apikey`.
- **Optional `tickers`:** *"The stock/crypto/forex symbols of your choice. For example: `tickers=IBM` will filter for articles that mention the IBM ticker; `tickers=COIN,CRYPTO:BTC,FOREX:USD` will filter for articles that **simultaneously** mention Coinbase (COIN), Bitcoin (CRYPTO:BTC), and US Dollar (FOREX:USD) in their content."*
  → **"CRYPTO:BTC" is a real, documented ticker value: VERIFIED.**
- **Optional `topics`:** *"The news topics of your choice. For example: `topics=technology` will filter for articles that write about the technology sector; `topics=technology,ipo` will filter for articles that **simultaneously** cover technology **and** IPO in their content. Below is the full list of supported topics:"*
  Full list (verbatim): **Blockchain: `blockchain`**, Earnings: `earnings`, IPO: `ipo`, Mergers & Acquisitions: `mergers_and_acquisitions`, Financial Markets: `financial_markets`, Economy - Fiscal Policy: `economy_fiscal`, Economy - Monetary Policy: `economy_monetary`, Economy - Macro/Overall: `economy_macro`, Energy & Transportation: `energy_transportation`, Finance: `finance`, Life Sciences: `life_sciences`, Manufacturing: `manufacturing`, Real Estate & Construction: `real_estate`, Retail & Wholesale: `retail_wholesale`, Technology: `technology`.
  → **`blockchain` is valid: VERIFIED. `cryptocurrency`/`CRYPTOCURRENCY` is NOT in the supported topic list: VERIFIED (absent).**
- **Optional `time_from` / `time_to`:** *"The time range of the news articles you are targeting, in YYYYMMDDTHHMM format. For example: `time_from=20220410T0130`. If time_from is specified but time_to is missing, the API will return articles published between the time_from value and the current time."*
  → **`YYYYMMDDTHHMM` (UTC, minute precision): VERIFIED.** Docs worked example: `...function=NEWS_SENTIMENT&tickers=COIN,CRYPTO:BTC,FOREX:USD&time_from=20220410T0130&limit=1000&apikey=demo` (queries the 2022-04-10 past range → historical `time_from` is supported, archive depth ⚠️ Unverified).
- **Optional `sort`:** *"By default, `sort=LATEST` and the API will return the latest articles first. You can also set `sort=EARLIEST` or `sort=RELEVANCE` based on your use case."*
- **Optional `limit`:** *"By default, `limit=50` and the API will return up to 50 matching results. You can also set `limit=1000` to output up to 1000 results."*

### 1.2 Response schema — ✅ Verified (live call)

Call made this session: `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo` (the docs' own example link; returns HTTP 200 JSON).

Top-level keys (verbatim): `items` (string, `"50"`), `sentiment_score_definition`, `relevance_score_definition`, `feed` (array). Definitions verbatim:
- `sentiment_score_definition`: `"x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat_Bullish; x >= 0.35: Bullish"`
- `relevance_score_definition`: `"0 < x <= 1, with a higher score indicating higher relevance."`

Per-article object, one sample **verbatim from the live response**:

```json
{
    "title": "Apple Reclaims $5 Trillion Crown: What's Going On?",
    "url": "https://www.benzinga.com/trading-ideas/movers/26/11/63054391/apple-reclaims-5-trillion-crown-whats-going-on",
    "time_published": "20261109T174800",
    "authors": ["Anusuya Lahiri"],
    "summary": "Apple Inc. has reportedly reclaimed a $5 trillion market capitalization, surpassing NVIDIA Corp., driven by its lower reliance on extensive AI infrastructure spending, robust demand for its bonds, and expanding AI rollout in China. ...",
    "banner_image": "https://cdn.benzinga.com/cdn-cgi/image/...",
    "source": "Benzinga",
    "category_within_source": "General",
    "source_domain": "Benzinga",
    "topics": [
        { "topic": "financial_markets", "relevance_score": "0.940501" },
        { "topic": "technology", "relevance_score": "0.833786" },
        { "topic": "finance", "relevance_score": "0.639149" }
    ],
    "overall_sentiment_score": 0.148969,
    "overall_sentiment_label": "Neutral",
    "ticker_sentiment": [
        { "ticker": "AAPL", "relevance_score": "1.000000", "ticker_sentiment_score": "0.631752", "ticker_sentiment_label": "Bullish" },
        { "ticker": "NVDA", "relevance_score": "0.829871", "ticker_sentiment_score": "-0.437159", "ticker_sentiment_label": "Bearish" }
    ]
}
```

Schema facts that matter to the parser:
- `time_published` format is **`YYYYMMDDTHHMMSS`** (note: **seconds**, 6 digits — one granular level finer than the request-side `time_from`): live values `"20261109T174800"`, `"20261109T212404"` etc. ✅
- `overall_sentiment_score` is a **bare JSON number**; `overall_sentiment_label` a string. ✅
- `ticker_sentiment[]` entries carry `relevance_score`, `ticker_sentiment_score`, `ticker_sentiment_label` as **strings** (quote-and-float in the parser); `ticker` is the symbol. ✅
- `topics[]` entries are `{topic, relevance_score}` with lowercase topic slugs matching the filter list (`blockchain`, `financial_markets`, …). ✅

### 1.3 Rate limits / free access

- Free standard limit: **25 API requests/day** — premium page: *"For use cases that exceed our **standard API usage limit (25 API requests per day)** or require certain premium API functions, we offer a premium plan to scale your use cases."* ✅ Verified — https://www.alphavantage.co/premium/
- Paid: 75–1200 req/min, no daily limits ($49.99+/mo). ✅ same page.
- **Caveat:** the docs section carries the badge *"Trending Premium"* and the tip *"💡 Tip: this is a premium API function. Subscribe to a premium membership plan to instantly unlock all premium APIs."* yet the docs' own demo link (`apikey=demo`) returns 200 with data for this endpoint. ✅ Verified — https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo
  ⚠️ **Whether a personal free key draws from the 25/day allotment vs. is premium-blocked is not stated** on the public docs (demo key ≠ personal key). One-time test with the project's real free key required before spec freeze. (Same finding as research/news-sentiment-sources.md §2.3.)

---

## 2. CryptoPanic — free API v2 auth + shape

Official docs: https://cryptopanic.com/developers/api/ — a Vue SPA; **content renders client-side only** and returned nothing to plain fetch this session. Facts below combine: (a) today's search-index snippets of the official docs pages, (b) the **repo's own same-day headless-render verification** recorded in `research/news-sentiment-sources.md` §2.1–2.3 (read against the official docs/about/plans pages), (c) mirrors quoting the official docs, (d) a live 404 probe.

### 2.1 Auth — ✅ VERIFIED: `auth_token` is required

- Official docs (search-index snippet of https://cryptopanic.com/developers/api/, sighted 2026-11-09): *"API Reference — Welcome to the CryptoPanic API reference. This section documents all available endpoints, parameters, responses, and error codes. Authentication ⚠️ You must include your auth_token in all requests to authenticate."*
- Base URL pattern (official / docs mirrors): **`https://cryptopanic.com/api/<api_plan>/v2`** — the plan segment is in the URL now (e.g. `developer`, `growth`, `enterprise` in today's docs render; mirrors say "API_PLAN"). `API access requires an account;` token is personal and regenerated at the developer dashboard (login-walled).
- Live probe this session: `GET https://cryptopanic.com/api/v2/posts/?currencies=BTC` and `?auth_token=empty` → **HTTP 404 both times** (no plan-qualified base URL / invalid token ⇒ no data). Consistent with the plan-qualified URL; exact error contract ⚠️ Unverified (401-on-invalid-token is asserted by third-party SDK error classes, not by a quotable official doc).

### 2.2 `/posts/` parameters and response

- Params (official docs render, same-day, `research/news-sentiment-sources.md` §2.1): `public=true`, **`currencies=BTC,ETH`** (comma codes — BTC filter valid ✅), `regions=en`, **`filter` ∈ {`rising`, `hot`, `bullish`, `bearish`, `important`, `saved`, `lol`}`**, `kind` ∈ {`news`, `media`, `all`}, `page` (1–50). **`hot` and `rising` filter values exist: VERIFIED.** Enterprise-only: `last_pull`, `panic_period` (1h/6h/24h), `panic_sort`, `size`, `with_content`, `search`.
- Corroborated by official-docs mirrors: https://www.anygen.io/showcase/cryptopanic/index.html (filter table: currencies/regions/filter/kind + votes fields, "checked in September 2026") and the PyPI SDK `cryptopanic==0.1.0` (https://pypi.org/project/cryptopanic/, released 2026-01-08 — `get_posts(currencies=["BTC", "ETH"], filter="rising")`, "hot" listed, pagination `next`/`previous`).
- Per-post shape (SDK + AnyGen mirror + repo's official-docs render; model-scored fields vs crowd votes both absent/limited):
  - `Post`: `id: int`, `slug: str`, `title: str`, `description: str`, **`published_at: datetime`** (ISO 8601), `created_at: datetime`, `kind: str # "news", "media", "blog", "twitter", "reddit"`, `source: {title, region, domain, type}`, `original_url: str`, `url: str`, `image: str | None`, **`instruments: [{code: "BTC", title, slug, url, market_cap_usd, price_in_usd, ...}]`**, **`votes: {negative, positive, important, liked, disliked, lol, toxic, saved, comments}`** (all ints), `panic_score: int | None # 0–100`, `panic_score_1h`, `author`, `content`. ✅ Verified as the SDK's declared model + AnyGen's docs-mirror table (votes list: *"negative, positive, important, liked, disliked, lol, toxic, saved, comments"*).
  - **Sentiment is crowd-vote-based, not a model score**: there is **no per-post model `sentiment` score field** in the documented v2 response; bullish/bearish views are the `filter=` values driven by community votes. ✅ (official-docs render + SDK model + AnyGen all agree; no field named `sentiment` appears in any of the three.)
  - `published_at` exists with minute-or-finer precision (datetime in ISO 8601) — **suitable for hourly self-archiving**, but the exact sub-minute format is ⚠️ Unverified (no official doc text rendered this session confirms "%H:%M[:SS][+tz]"); dedupe by `id`, bucket by `published_at` floor. 
- Metadata gating (official `/developers/api/legacy` search-index snippet, sighted 2026-11-09): *"Extra metadata in API responses increases traffic and costs, therefore following fields are available only to PLUS users: description, image. Add &metadata=true to get extra metadata fields."* — i.e. `metadata=true` is a plan-gated extra-fields switch; core post fields are returned without it. (Same finding recorded in repo §2.1.)

### 2.3 Rate limits and the free tier

- Official overview (repo's same-day render, §2.2 of news-sentiment-sources.md): *"rate limited per IP at 5 req/sec, or 10 req/sec depending on your API plan"*; *"server-side caching, so there is no point of making requests more than once every 30 seconds"*; *"All API requests are logged"*; *"rights to revoke API access at any time for any reason"*. ✅ — https://cryptopanic.com/developers/api/about/
- Plans (official `/developers/api/plans/` render, same day): **Growth weekly $50/week** (10 req/s, 600 requests/week, 1-month history), **Growth $199/mo** (3,000 requests/month, 1-year history), **Enterprise from $899/mo**; *"News Delay: Real-time (except Free plan)"* — implying a free plan exists. ✅
- ⚠️ **Contradiction to resolve before spec freeze:** the third-party dltHub connector page (updated 2026-08-26, https://dlthub.com/context/source/cryptopanic) states: *"Note: API access requires an active paid plan, as the free Developer plan was discontinued in early 2026."* — this conflicts with the official docs render (same-day, lists `developer|growth|enterprise` and "Free plan") and with AnyGen ("CryptoPanic offers free and paid API access"). Official docs outrank dltHub, but the free token's real quota/page-size limits are login-walled either way; **verify free-plan token creation + limits in the dashboard once before relying on CryptoPanic in v0.2**.
- RSS: `format=rss` (or `/news/rss/`) returns **max 20 items** regardless of plan. ✅

---

## 3. Freqtrade / FreqAI config facts (v2026.10, spot)

Sources checked this session: docs https://www.freqtrade.io/en/stable/freqai-configuration/ and /en/stable/freqai-parameter-table/, machine config schema https://schema.freqtrade.io/schema.json (what `$schema`/validation consumes), and the shipped example config https://raw.githubusercontent.com/freqtrade/freqtrade/stable/config_examples/config_freqai.example.json. Note: `config_examples/config_full.example.json` (stable) contains **no `freqai` section** — the FreqAI home is `config_examples/config_freqai.example.json`. ✅ (both example configs fetched this session)

### 3.1 `include_corr_pairlist` for a SPOT BTC/USDT pair — ✅ VERIFIED: `"BTC/USDT"` (no `:USDT` suffix)

- The shipped example config uses `"include_corr_pairlist": ["BTC/USDT:USDT", "ETH/USDT:USDT"]` **only because that whole file is `"trading_mode": "futures"`** (its `pair_whitelist` is `1INCH/USDT:USDT`…). ✅ — config_freqai.example.json.
- The docs' own minimal-config example uses flat/spot-style values: `"include_corr_pairlist": ["ETH/USD", "LINK/USD", "BNB/USD"]`. ✅ — freqai-configuration.md.
- The docs state the `:USDT` suffix is added **if and only if** using futures pairs: *"...`%%-rsi-period_10_ETH/USDT:USDT_1h` for the `rsi` feature with `period=10`, `timeframe=1h`, and `pair=ETH/USDT:USDT` (**the `:USDT` is added if you are using futures pairs**)."* ✅ — freqai-configuration.md.
- → **For spot BTC/USDT: `include_corr_pairlist: ["BTC/USDT"]` is correct; `BTC/USDT:USDT` is futures notation and wrong for spot.**

### 3.2 Minimal required `freqai` block — ✅ VERIFIED (docs, verbatim)

From https://www.freqtrade.io/en/stable/freqai-configuration/ ("Setting up the configuration file") — *"a FreqAI config must at minimum include the following parameters"*:

```json
"freqai": {
    "enabled": true,
    "purge_old_models": 2,
    "train_period_days": 30,
    "backtest_period_days": 7,
    "identifier": "unique-id",
    "feature_parameters": {
        "include_timeframes": ["5m","15m","4h"],
        "include_corr_pairlist": ["ETH/USD", "LINK/USD", "BNB/USD"],
        "label_period_candles": 24,
        "include_shifted_candles": 2,
        "indicator_periods_candles": [10, 20]
    },
    "data_split_parameters": {
        "test_size": 0.25
    }
}
```

Schema cross-check (`schema.freqtrade.io/schema.json`, `definitions.freqai`): top-level keys include `enabled`, `identifier`, `write_metrics_to_disk`, `purge_old_models`, `conv_width`, `train_period_days`, `backtest_period_days`, `live_retrain_hours`, `expiration_hours`, `save_backtest_models`, `fit_live_predictions_candles`, `data_kitchen_thread_count`, `activate_tensorboard`, `wait_for_training_iteration_on_reload`, `continual_learning`, `keras`, `override_exchange_check`, `feature_parameters` (**required sub-keys: `include_timeframes`, `include_corr_pairlist`** — so `include_corr_pairlist` is not optional even if empty), `data_split_parameters`, and **`model_training_parameters`** ("Flexible dictionary that includes all parameters available by the selected model library.", type object). The user-guessed key `"features"` does **not** exist — the real key is **`feature_parameters`**. ✅

### 3.3 Selecting a classifier model — ✅ VERIFIED: top-level `"freqaimodel"` (or CLI `--freqaimodel`)

- The model is chosen **by class name only**: docs *"...via the flag `--freqaimodel LightGBMClassifier`"*; classifiers section: *"FreqAI includes a variety of classifiers, such as the `LightGBMClassifier` via the flag `--freqaimodel LightGBMClassifier`"*. ✅ — freqai-configuration.md. In a config file the same name is the **top-level** key (not inside `freqai`): schema property `"freqaimodel": {"description": "FreqAI model class name (must be available in the user directory under freqaimodels). Additional search paths can be added via freqaimodel_path.", "type": ["string","null"]}` — sibling keys `freqaimodel_path` and `freqai` ($ref to the freqai block above). ✅ — schema.freqtrade.io/schema.json.
- Classifier targets must be **strings/discrete** (docs: `df['&s-up_or_down'] = np.where(df["close"].shift(-100) > df["close"], 'up', 'down')` as the classifier example; multiple targets must all go in one label column). ✅
- **`freqai.classifier_activation` (or any `classifier*` key) does NOT exist**: a grep of the full fetched `schema.freqtrade.io/schema.json` for `classifier`/`classif*` returns **zero properties**; the freqai-configuration and freqai-parameter-table doc pages list no such key either. The only class-related mechanism anywhere in the docs is `self.freqai.class_names = ["down", "up"]` set inside the strategy's `set_freqai_targets()` — **a PyTorch-classifier-only attribute**, not a config key. → Do **not** write `classifier_activation` or similar into the config; report the real schema as above. ✅

---

## 4. Bybit spot fee (dry-run assumption) — ✅ Verified: taker 0.1% (0.001)

- **Bybit's own fee page**: https://www.bybit.com/en/fee/spot — page is JS-only to our fetcher; its published description (sighted 2026-11-09 via search index of that page) states: *"Bybit charges maker and taker fees starting at 0.1% for Spot trading."* A third-party schedule verified against that page agrees: *"At the base tier (VIP 0), Bybit charges 0.1% maker and 0.1% taker on spot"* (checked 2026-09-23, https://coinfutures.info/exchanges/bybit/fees).
- **CCXT source (what freqtrade actually consumes), verbatim** — https://raw.githubusercontent.com/ccxt/ccxt/master/python/ccxt/bybit.py, spot-market parser (~line 2017):
  ```python
  takerFee = self.parse_number('0.001')   # = 0.1%
  makerFee = self.parse_number('0.001')   # = 0.1%
  ... 'taker': takerFee, 'maker': makerFee, ...  # on spot markets (contract: False)
  ```
  → in freqtrade dry-run, the per-market fee freqtrade falls back to (CCXT spot market fee for `bybit`) is **0.1% taker / 0.1% maker**: ✅ Verified.
- **Freqtrade hook for the assumption**, config docs row `fee` (raw source: https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docs/configuration.md, verified this session): *"`fee` — Fee used during backtesting / dry-runs. Should normally not be configured, which has freqtrade fall back to the exchange default fee. Set as ratio (e.g. 0.001 = 0.1%). Fee is applied twice for each trade, once when buying, once when selling."* Schema: `"fee": {"description": "Trading fee percentage. Can help to simulate slippage in backtesting", "type": "number", "minimum": 0, "maximum": 0.1}`. → dry-run fee of 0.1% is the default-by-exchange behavior for bybit spot; optionally pin it with `"fee": 0.001`.

---

## Spec inputs (facts only)

- **AV endpoint:** `GET https://www.alphavantage.co/query` with `function=NEWS_SENTIMENT&apikey=...`. ✅
- **AV ticker syntax:** `tickers=` CSV of symbols — `"CRYPTO:BTC"` is a real documented value (e.g. `tickers=COIN,CRYPTO:BTC,FOREX:USD`; crypto-only: `tickers=CRYPTO:BTC`); multiple values are AND-filtered. ✅
- **AV topics:** `topics=blockchain` is valid; `topics=technology,ipo`-style CSV is AND-filtered. **No `cryptocurrency` topic exists.** Full valid list: blockchain, earnings, ipo, mergers_and_acquisitions, financial_markets, economy_fiscal, economy_monetary, economy_macro, energy_transportation, finance, life_sciences, manufacturing, real_estate, retail_wholesale, technology. ✅
- **AV time window:** `time_from`/`time_to` in `YYYYMMDDTHHMM` (UTC, minute); `time_from` alone = from-range to now; historical ranges supported (docs example `time_from=20220410T0130`). ✅
- **AV sort/limit:** `sort=LATEST|EARLIEST|RELEVANCE` (default LATEST); `limit` default 50, max 1000. ✅
- **AV per-article fields:** `title`, `url`, `time_published` (**`YYYYMMDDTHHMMSS`**, seconds), `authors[]`, `summary`, `banner_image`, `source`, `category_within_source`, `source_domain`, `topics[]{topic, relevance_score}`, `overall_sentiment_score` (number), `overall_sentiment_label`, `ticker_sentiment[]{ticker, relevance_score(string), ticker_sentiment_score(string), ticker_sentiment_label}`. Top-level: `items`, `sentiment_score_definition`, `relevance_score_definition`, `feed[]`. Bucket boundaries: ≤ -0.35 Bearish; ≤ -0.15 Somewhat-Bearish; (-0.15, 0.15) Neutral; ≤ 0.35 (note docs write `<=` from 0.15) Somewhat-Bullish; else Bullish. ✅
- **AV rate:** free key standard limit **25 requests/day**; paid 75–1200 req/min. NEWS_SENTIMENT's premium-status on free personal keys is unresolved → one-time key test before freeze. ✅/⚠️
- **CryptoPanic:** `auth_token` **required** on all API requests; base URL is plan-qualified `https://cryptopanic.com/api/<api_plan>/v2/`; plain `/api/v2/...` 404s. ✅
- **CryptoPanic `/posts/`:** `currencies=BTC[,ETH]`, `regions`, `filter` ∈ {rising, **hot**, bullish, bearish, important, saved, lol}, `kind` ∈ {news, media, all}, `page` (1–50, `next`/`previous` URLs). ✅
- **CryptoPanic per-post:** `id`, `title`, `published_at` (ISO 8601 datetime, minute-or-finer — precision ⚠️), `kind`, `source{title,region,domain}`, `url`, `instruments[{code: "BTC", ...}]`, `votes{positive, negative, important, liked, disliked, lol, toxic, saved, comments}`, `panic_score` (0–100, plan-gated param). **No model-scored per-post `sentiment` field — sentiment is crowd-vote based; bullish/bearish are `filter=` values.** ✅ (schema fields ⚠️ for anything beyond votes/verified params)
- **CryptoPanic plans/pricing (as of same-day render):** free/"developer" plan exists per official plans page but with unpublished limits (login-walled) — ⚠️ contradicted by dltHub's "free Developer plan was discontinued in early 2026"; Growth $199/mo = 3,000 requests/month (≈100/day), Enterprise from $899/mo; per-IP 5–10 req/s, ~30 s server-side cache, all requests logged; RSS capped at 20 items. For hourly BTC self-archiving: ≤ 25 pages/day is comfortably inside even Growth, but free-tier feasibility must be dashboard-verified. ⚠️
- **FreqAI spot correlation pairs:** `feature_parameters.include_corr_pairlist: ["BTC/USDT"]` — spot notation only; `BTC/USDT:USDT` is futures notation (the `:USDT` suffix is added "if you are using futures pairs"). `include_corr_pairlist`+`include_timeframes` are schema-required sub-keys of `feature_parameters`. ✅
- **FreqAI minimal block:** `"freqai": {"enabled": true, "purge_old_models": 2, "train_period_days": 30, "backtest_period_days": 7, "identifier": "...", "feature_parameters": {"include_timeframes": [...], "include_corr_pairlist": [...], "label_period_candles": N, "include_shifted_candles": 2, "indicator_periods_candles": [...]}, "data_split_parameters": {"test_size": 0.25}}`; optional extras: `model_training_parameters`, `live_retrain_hours`, `save_backtest_models`, `fit_live_predictions_candles`, `keras`. The key is `feature_parameters` — no `features` key. ✅
- **FreqAI model switch:** `"freqaimodel": "LightGBMClassifier"` — **top-level** config key (or CLI `--freqaimodel`); model selected by class name only; classifier labels are set as string classes (`'up'/'down'` etc.) inside `set_freqai_targets()`. `"freqai.classifier_activation"` and any `classifier*` config key **do not exist** in schema.json or docs; the only class-name mechanism is the PyTorch-classifier-only `self.freqai.class_names` in-strategy attribute. ✅
- **Bybit spot fee:** taker (and maker) **0.1%** = 0.001 at base tier; CCXT hardcodes spot taker/maker `0.001` for bybit, which is what freqtrade's dry-run/backtest fee falls back to; freqtrade optional override: `"fee": 0.001` (applied twice per round-trip). ✅

---

### Primary URLs used this session

- https://www.alphavantage.co/documentation/ (NEWS_SENTIMENT section; page text + full-parameter quotes)
- https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo (live schema/sample; demo key)
- https://www.alphavantage.co/premium/ (25/day free standard limit; plans)
- https://cryptopanic.com/developers/api/ (+ /legacy; SPA — content sighted via official-pages search index today + repo session-prior headless render in research/news-sentiment-sources.md §2.1–2.3)
- https://www.anygen.io/showcase/cryptopanic/index.html (mirror of official docs: filters, votes, plan table)
- https://pypi.org/project/cryptopanic/ (SDK 0.1.0 mirroring official API: Post/Instrument/Source/Votes models, params, 401/403/429 error classes)
- https://dlthub.com/context/source/cryptopanic (contradicting free-plan claim — flagged)
- https://www.freqtrade.io/en/stable/freqai-configuration/, /en/stable/freqai-parameter-table/, /en/stable/exchanges/
- https://schema.freqtrade.io/schema.json (machine config schema; `freqaimodel`, `fee`, freqai defs; zero `classifier*` keys)
- https://raw.githubusercontent.com/freqtrade/freqtrade/stable/config_examples/config_freqai.example.json (freqai example; futures notation)
- https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docs/configuration.md (`fee` row)
- https://raw.githubusercontent.com/ccxt/ccxt/master/python/ccxt/bybit.py (spot taker/maker 0.001)
- https://www.bybit.com/en/fee/spot (fee page; content sighted via its indexed description)
