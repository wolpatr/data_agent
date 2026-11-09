# News & sentiment sources — fact-finding (v0.2 Decide inputs)

**Date:** 2026-11-09
**Scope:** financial news/sentiment sources a Python bot can consume for 1h-candle crypto decisions (freqtrade harness v0.1 dry-run, BTC/USDT Bybit spot; v0.2 = ML-classifier Decide with news features). RESEARCH ONLY — no project code.
**Method:** every claim below was checked against the vendor's own docs/pricing page, official source code, or the cited arXiv paper. `✅ Verified — <URL>` = read this session against the primary page (or its live-API response). `⚠️ Unverified` = plausible/secondhand or the page could not be rendered this session; do not build on it without confirming. JS-heavy vendor sites were read via Wayback snapshots or a headless-render of the official page; those are noted.

---

## 1. Comparison table (free-tier reality, per official pages)

| Source | Cost (verified) | Free-tier limits | Rate limits | Latency/freshness | Crypto coverage | Historical news w/ timestamps | Terms / attribution constraints |
|---|---|---|---|---|---|---|---|
| **CryptoPanic** API | Growth $50/week or $199/mo; Enterprise from $899/mo ⚠️ | Free token exists ("developer" plan) but limits published only behind login ⚠️ | Per-IP 5 or 10 req/s + monthly cap ("e.g. 1,000/mo … 300,000/mo" examples) ✅ | Live feed, near-real-time; server-side cache ≈ 30 s ✅ | **Crypto-native** (crowd votes, panic score, coin filters) ⚠️ history plan-bound | **No date-range API param** (`page` max 50, `last_pull` Enterprise-only) ✅ docs show none | No use of name/logo/branding; access revocable "at any time for any reason" ✅ |
| **Finnhub** | All-In-One **$3,500/mo** ✅ | Free: 60 API calls/min, **Company News 1 year + real-time** ✅ | 60 req/min ✅ | Real-time ✅ | Category endpoint incl. crypto per docs ⚠️ (docs SPA unrenderable this session) | `/company-news?from&to` date-ranged ✅; `/news` general feed is **not** date-ranged (`minId` only) ✅ (SDK) | Personal Use license ✅; no attribution scheme found in pricing page |
| **Alpha Vantage** NEWS_SENTIMENT | Premium $49.99/mo (75 req/min) ✅ | 25 req/day free "covering the majority of our datasets" ✅ — NEWS_SENTIMENT explicitly on free tier **ambiguous** | 25 req/day; paid 75–1200 req/min ✅ | Live; articles `time_published` to the second ✅ | Yes — ticker syntax `CRYPTO:BTC`, topic `blockchain` ✅ | `time_from`/`time_to` historical query params; docs example dated 2022-04 (archive *depth* ⚠️) | Terms of Service on site; open-source/education exemption for rate limits ✅ |
| **NewsAPI.org** | $449/mo Business ✅ | Developer $0: **dev/testing only, 24 h article delay, 1-month search window, 100 req/day** ✅ | 100 req/day ✅ | 24 h delayed (free) / real-time (paid) ✅ | General outlet list; specific crypto outlets not verified ⚠️ | 1 month (free) / 5 years (Business $449/mo) ✅ | Dev plan forbidden in staging/production ✅; no full text, URLs only ✅ |
| **GDELT** | **Free, no key** | Entire database "100% free and open" ✅ | DOC API: no documented key/limit (best practice: modest pacing) ⚠️ | DOC API rolling 3-month window; 15-min update cadence ✅ | Global news incl. crypto only via search keys / themes (no crypto-specific entity API) ⚠️ | **Full raw archive downloadable**: 2.0 events+GKG files every 15 min (live slot verified 2026-11-09); 1.0 events back to 1979 ✅ | Terms of use published on about page (attribution expectations ⚠️ unverified detail) |
| **Marketaux** | Basic $29 → Pro 50K $199/mo (snapshot 2025-04) ✅ | 100 req/day but **only 3 articles/request** ⚠️ snapshot | Daily quota ✅ | "Instant news access" ✅ | Entity-level sentiment + market cap across 5,000+ sources; 80+ markets ✅ | Date filtering exists per docs ⚠️ (not rendered this session) | TOS on site; attribution scheme ⚠️ |
| **GNews API** (what CryptoTrade actually used) | Essential €49.99/mo | **Free €0: non-commercial only, 100 req/day, 12-h delay, 30-day history** ✅ | Daily quota ✅ | 12 h delayed (free) / real-time (paid) ✅ | Google News coverage per keyword/topic (crypto via queries) ✅ | Paid: "historical data since 2020" ✅; free: last 30 days ✅ | Free plan forbids commercial use explicitly ✅ |
| **RSS: CoinDesk** | Free | No documented limit ✅ (feed `ttl: 5`) | — | Hourly update-period; items timestamped `pubDate` ✅ | Crypto-native ✅ | **Live-only** (no archive endpoint documented) ✅-by-absence | copyright "© CoinDesk, Inc."; republication terms apply ⚠️ |
| **RSS: Cointelegraph** | Free | Same ✅ | — | Hourly; `pubDate`/`atom:updated` ✅ | Crypto-native ✅ | **Live-only** ✅-by-absence | utm-tagged links; standard RSS courtesy expected ⚠️ |
| **RSS: Reuters** | — | **Public RSS feeds dead** (feeds.reuters.com transport error this session) ✅-by-attempt | — | — | — | — | Reuters content is licensed wire content; no public API ⚠️ |
| **X / Twitter API** | **Pay-per-usage credits, no subscriptions** ✅ (2026) | — | Post read **$0.005/post**, cap 3 M reads/month ✅ | Real-time ✅ | Crypto discourse strong but unfiltered | No historical window on cheap tiers; full-archive search ⚠️ (was Pro-gated before 2025 pricing change) | Search/timelines ToS; scraping forbidden ✅ (docs) |
| Bloomberg / Reuters wire / Dow Jones Newswires | Enterprise contracts only (LSEG/CBRS/Decipher equivalents are six-figure) ⚠️ | — | — | — | Yes, but priced out | — | **Out of reach — treat as unavailable for v0.2** |

**Killer-limitation one-liners**

- **CryptoPanic** — the richest crypto-native crowd-signal, but on today's public docs there is **no historical date-range query**, and history depth + sane rate limits sit behind $199/mo (with the plans page contradicting itself on how much).
- **Alpha Vantage NEWS_SENTIMENT** — the only cheap API returning **per-article, per-ticker, machine-scored sentiment with second timestamps you can re-query over time ranges**; cost/risk is the 25 req/day free ceiling being *ambiguous* for this endpoint.
- **GDELT** — the only **fully free** source whose full history is directly downloadable, but it is *global-press aggregate* data (tone, volume, themes), not per-coin entity sentiment, and its search API only reaches back **3 months**.
- **NewsAPI.org** — free tier is dev-only, 24 h delayed, 1 month window: unusable for live and shallow for backtest; the useful tier is $449/mo.
- **Finnhub** — free tier gives 1 year of *company* news with date ranges, but the general/crypto news feed is not date-ranged, so walk-forward backfill of the *general* crypto feed isn't documented.
- **GDELT/X/RSS** — no cost barrier live, but no (or expensive/no) historical replay without self-archiving.

---

## 2. Source inventory — details, verified against each vendor's own pages

### 2.1 CryptoPanic
- Current official API docs (rendered copy of https://cryptopanic.com/developers/api/ since the page is SPA): base `https://cryptopanic.com/api/<plan>/v2`, plans `developer | growth | enterprise`; endpoints `GET /posts/` and `GET /portfolio/` (Growth+). Params: `public=true`, `currencies=BTC,ETH`, `regions=en`, `filter in {rising, hot, bullish, bearish, important, saved, lol}`, `kind in {news, media, all}`, `page` (max 50), and **Enterprise-only**: `last_pull`, `panic_period (1h/6h/24h)`, `panic_sort`, `size (1–50)`, `with_content`, `search`. ✅ Verified — https://cryptopanic.com/developers/api/ (headless-render of official page)
- Item schema includes: `id, slug, title, description, published_at (ISO 8601), created_at, kind (news|media|blog|twitter|reddit), source{title,region,domain,type}, instruments[], votes{positive, negative, important, liked, disliked, lol, toxic, saved, comments}, panic_score (0–100), author, content{original|clean}`. ✅ same URL. The sentiment signal is **vote-based** (filters `bullish`/`bearish`) rather than a model score ✅.
- Rate limits & terms (official overview page, headless-render): "rate limited per IP at 5 req/sec, or 10 req/sec depending on your API plan"; "server-side caching, so there is no point of making requests more than once every 30 seconds"; "All API requests are logged"; "rights to revoke API access at any time for any reason"; no use of CryptoPanic name/logo/branding without approval. ✅ Verified — https://cryptopanic.com/developers/api/about/
- Plans & pricing (official page): Growth weekly **$50/week** (history 1 month), Growth **$199/mo** ($179 annual) (history "**1 years**"), Enterprise **custom from $899/mo** (history 1 year, PUSH API + SEARCH QUERY, unlimited rate limit); "News Delay: Real-time (except Free plan)"; monthly requests 600 (weekly plan) / 3,000 (Growth) / custom. ✅ Verified — https://cryptopanic.com/developers/api/plans/
- **Contradiction (recorded):** the Overview says Growth **$199/mo → History 1 month** and only Enterprise gets "1 years"; the Plans table says Growth $199 → **1 year**. Also Overview wrote the weekly plan's 600 request cap as "**req/month**" while Plans says "**req/week**". ⚠️ Both pages official, self-inconsistent — confirm in-dashboard before relying on Growth history.
- The public docs expose **no historical date-range query param** on `/posts/` (`page` is capped at 50; `size`/`last_pull` are Enterprise). ✅ Verified — https://cryptopanic.com/developers/api/
- A consumer **PLUS** plan ($49/year, Panic Score display, X content curation, 5 bots) exists and explicitly "**PLUS is not an API plan and does not provide access to the CryptoPanic API**". ✅ Verified — https://cryptopanic.com/plus/
- RSS: `/news/rss/` and API-with-`format=rss` exist; RSS returns **only 20 items regardless of plan**. ✅ same docs URL.
- Free "developer" plan specifics (calls/month, page size, delay): ⚠️ Unverified — dashboards are login-walled; older third-party write-ups (free v1 API ≈ 1 req/s, `before_ts`/`after_ts` window on the retired v3 "Pro" API) are secondhand and do not match today's v2 docs. Do not build the v0.2 spec on them.

### 2.2 Finnhub
- Pricing (rendered official pricing page, snapshot Sep 2025): **Free $0/mo — Personal Use — 60 API calls/minute — "Company News: 1 year and real-time updates"**; All-In-One **$3,500/mo** (annually) — "Company News: 20 years", 900 calls/min. ✅ Verified — https://finnhub.io/pricing
- Endpoints verified directly in the **official SDK client source** (`finnhub-python`, Finnhub-Stock-API): `general_news(category, min_id)` → `GET /news` (param `category`, `minId` — **no date range param**); `company_news(symbol, from, to)` → `GET /company-news` (**date-ranged**); `news_sentiment(symbol)` → `GET /news-sentiment` (company-level aggregate, **not** per-article scores); plus `press_releases(symbol, from, to)`, `stock_social_sentiment(symbol, from, to)`. ✅ Verified — https://raw.githubusercontent.com/Finnhub-Stock-API/finnhub-python/master/finnhub/client.py
- Crypto news access is documented as `GET /news?category=crypto` ⚠️ Unverified — the docs pages (`finnhub.io/docs/api/news`, `/company-news`) are a React SPA that rendered empty this session even via headless render; the exact category enum and news-article-depth policies still need one-time verification from a real account.
- No crypto-specific news endpoints (crypto endpoints are market-data: `crypto_candles`, `crypto_symbols`, …). ✅ Verified — same SDK source.

### 2.3 Alpha Vantage — Market News & Sentiment (`NEWS_SENTIMENT`)
- Response schema verified by a **live API call with the public demo key** (2026-11-09): `feed[]` items with `time_published` (`YYYYMMDDTHHMMSS`), `summary`, `source` / `source_domain`, `topics[]{topic, relevance_score}`, `overall_sentiment_score` + `overall_sentiment_label`, and per-ticker `ticker_sentiment[]{ticker, relevance_score, ticker_sentiment_score, ticker_sentiment_label}`; plus top-level `sentiment_score_definition`: **"x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat-Bullish; x >= 0.35: Bullish"** and `relevance_score_definition` "0 < x <= 1". Sources observed in-feed: CoinDesk, Benzinga, TradingView, Investing.com, Stocktwits, Yahoo Finance — i.e. real pre-c-scored model output, not crowd votes. ✅ Verified — https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo (live response) + https://www.alphavantage.co/documentation/
- Params (official docs): `tickers` with crypto syntax **`CRYPTO:BTC`** ("articles that simultaneously mention Coinbase (COIN), Bitcoin (CRYPTO:BTC)…"), `topics` including **`blockchain`**, `time_from`/`time_to` in `YYYYMMDDTHHMM`, `sort` = LATEST|EARLIEST|RELEVANCE, `limit` 50 default / 1000 max. ✅ Verified — https://www.alphavantage.co/documentation/ (NEWS_SENTIMENT section)
- **Historical**: `time_from` accepts past ranges — the official docs' worked example queries `time_from=20220410T0130` for `COIN,CRYPTO:BTC,FOREX:USD`. ✅ Verified — same docs URL. Archive *depth* (how far back crypto articles survive) ⚠️ Unverified; the demo key refuses non-whitelisted examples, and no published depth statement was found.
- Cost: docs badge + tip "this is a premium API function" ✅; but the official FAQ says free keys get "25 API requests per day … covering the majority of our datasets" and unlimited requests for "verified open-source or educational projects", and the demo key does return this endpoint's whitelisted example. ⚠️ Ambiguity: whether NEWS_SENTIMENT draws from the 25/day free allotment or strictly needs a paid key. Premium = $49.99/mo for 75 req/min ("No daily limits"). ✅ Verified — https://www.alphavantage.co/support/ and https://www.alphavantage.co/premium/
- Terms: Alpha Vantage Terms of Service apply at signup (acknowledged at key claim). Attribution per ToS ⚠️ (full ToS not parsed this session).

### 2.4 NewsAPI.org
- Pricing (official): **Developer $0** — "articles have a 24 hour delay", "Search articles up to a month old", "100 requests per day", "For development and testing … cannot be used in a staging or production environment (including internally)"; **Business $449/mo** — real-time, 5-year search, 250k req/mo; **Advanced $1749/mo** — 2M req/mo, 99.95% SLA; "**Is the full article content available with any plan?** No… you are able to use the URL included with each result to scrape this yourself if required." ✅ Verified — https://newsapi.org/pricing
- `/sources` page today lists top-headline outlets by country only (not an outlet table this session); specific crypto outlets therefore ⚠️ Unverified.
- Consequence: the free tier is unusable for a live 1h decision loop (24 h delay) **and** shallow for backtest (1 month).

### 2.5 GDELT
- "The entire GDELT database is 100% free and open and you can download the raw datafiles … or analyze it at limitless scale with Google BigQuery." Raw files: "over 2.5TB for last year alone". GDELT 2.0 events + GKG "update every 15 minutes". ✅ Verified — https://www.gdeltproject.org/data.html
- File cadence proven live: `https://data.gdeltproject.org/gdeltv2/lastupdate.txt` returned three zips for slot `20261109223000` (export / mentions / **gkg** CSV zips; GKG slot ≈ 6.4 MB). ✅ Verified — live response 2026-11-09.
- DOC 2.0 full-text search API (official blog post): searches "**a rolling window of the last 3 months**"; `STARTDATETIME/ENDDATETIME` in `YYYYMMDDHHMMSS`; timeline modes use **15-minute resolution for spans < 72 h, hourly 72 h–1 week, daily beyond a week**; articles as % of all monitored coverage (or raw in `timelinevolraw`); **Tone** filter/score (−100 … +100; `tone>5`, `tone<-5`); `mode=artlist` max 250 records; output CSV/JSON/RSS; CORS `*`; 65 machine-translated languages; `domain:`, `theme:`, `sourcelang:`, `near:`, `repeat:` operators. ✅ Verified — https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- **Historical**: downloadable archive is the real backtest path — GDELT 1.0 events since 1979, 1.0 GKG from 2013-04-01, 2.0 events + 2.0 GKG as 15-minute files (2.0 launched Feb 2015 per blog; data directories enumerated at `data.gdeltproject.org/gdeltv2/`). ✅ Verified — https://www.gdeltproject.org/data.html (+ links: `data.gdeltproject.org/events/index.html`, `/gkg/index.html`, and the 2.0 download blog page linked from data.html). The DOC **API** itself only reaches 3 months back ✅ (same blog post).
- No crypto ticker mapping — you query by keywords/themes/domains yourself; GKG contains tone/sentiment fields per its codebook ⚠️ (codebook PDF linked from data.html; not parsed this session).
- Terms of Use exist (about.html#termsofuse) ⚠️ detail unverified; GDELT datasets are routinely redistributed with attribution in academic work, but read the ToU before shipping anything.

### 2.6 Marketaux
- Plans (official pricing page via Wayback snapshot 2025-04-26; live fetch timed out twice this session): **Free $0 — 100 requests/day, 3 articles/request**; Basic $29/mo — 2,500/day, 20 articles; Standard $49 — 10,000/day, 50; Pro $99 — 25,000/day, 100; Pro 50K $199 — 50,000/day; 200,000+ entities, 5,000+ news sources, 80+ markets, 30+ languages; entity-level sentiment + market cap (entities per stat request: 0/0/20/100/100). ✅ Verified — https://web.archive.org/web/20250426201929/https://www.marketaux.com/pricing (marked snapshot, not live)
- Historical date filtering & per-entity historical sentiment ⚠️ Unverified this session (their docs page also failed to render). The 3-articles-per-request free cap is the headline constraint.

### 2.7 GNews API — the source CryptoTrade actually used
- Pricing verified from the vendor: **Free €0: non-commercial only, 100 req/day, up to 10 articles/request, 12-hour delay, last 30 days of historical data, content cut to 250 characters**; **Essential €49.99/mo: 1,000 req/day, real-time, "Historical data since 2020", full article content**; Business €99.99 (5,000/day); Enterprise €249.99 (25,000/day). "Can I use the Free plan for a commercial project? No." ✅ Verified — https://gnews.io/pricing
- It is a curated front on Google News (same mechanism the CryptoTrade paper used via the `gnews` Python package). ✅ Verified — paper §2.1 + Appendix B (below).

### 2.8 Free RSS feeds
- **CoinDesk**: live RSS at `https://www.coindesk.com/arc/outboundfeeds/rss/` — RSS 2.0, `pubDate` per item to the second, title/link/description/categories, `ttl: 5`, `sy:updatePeriod: hourly`, copyright "© 2026 CoinDesk, Inc.". Full text not in feed (`content:encoded` empty). ✅ Verified — live fetch 2026-11-09.
- **Cointelegraph**: live RSS at `https://cointelegraph.com/rss` — RSS 2.0, hourly update period, `pubDate` + `atom:updated`, HTML summary in `description`, article links utm-tagged. ✅ Verified — live fetch 2026-11-09.
- **Reuters**: public RSS retired — `feeds.reuters.com` transport error this session; Reuters removed its public RSS feeds around 2020 ⚠️ (secondary knowledge; the dead endpoint is verified). Wire content is enterprise-licensed. Reuters itself appears in third-party feeds (e.g., it showed up only as an Alpha Vantage source name in the demo feed), not as a free feed.
- CryptoPanic also offers RSS via its API with `format=rss` (20 items max regardless of plan) ✅ (§2.1).
- RSS = **live-only, self-archiving** (no historical endpoints); perfect for the dry-run accumulation track, useless alone for backtest.

### 2.9 X / Twitter API — cost reality
- Official docs (2026): X API v2 is now **pay-per-usage with credits, "No subscriptions"**; **Post read = $0.005/post** (deduplicated within 24 h), user read $0.010; capped at **3 M post reads per monthly cycle** on pay-per-usage; writes $0.015/request; auto-recharge + spending limits documented; xAI credit rebates 10–20% at $200–$1000+ spend. ✅ Verified — https://docs.x.com/x-api/getting-started/about-x-api and https://docs.x.com/x-api/getting-started/pricing.md
- Worked cost: an hourly poll reading ~15 crypto-analyst posts/hour ≈ 360 reads/day ≈ **$1.35/mo** at $0.005/read — live cost is trivially cheap now.
- Historical/backtest reality: the cheap tiers never included full-archive search (pre-2026 plans: archive search on Pro $5k/mo +); under the new credit model the archive-search entitlement is not clearly published ⚠️ Unverified. Treat X features as **live-only / collect-forward** for v0.2.

### 2.10 General financial wires (Bloomberg, Reuters, Dow Jones)
- No self-serve API: Bloomberg Terminal / Enterprise Access Point, LSEG (Reuters) Newswires, Dow Jones Newswires are negotiated enterprise contracts ⚠️ (general knowledge; not formally verified this session). **Out of reach for v0.2** — and note Alpha Vantage/Stocktwits/TradingView *resell or re-expose* some wire-adjacent content, which is the cheap lawful path to wire-ish coverage.

---

## 3. Historical availability — can the feature actually be backtested?

**Verdict: Yes, but only through a short list of paths. A live-only feed cannot backtest its feature — anything else in this table is collect-forward only.**

| Path | History depth | How | Status |
|---|---|---|---|
| **GDELT raw 2.0 files (GKG)** | 15-min granular files **since Feb 2015** (1.0 GKG from 2013; events to 1979) | Download `gkg.csv.zip` from `data.gdeltproject.org/gdeltv2/` per 15-min slot; aggregate tone/volume/themes yourself | ✅ Verified free & open (data.html; lastupdate.txt live) |
| **GDELT DOC API** | **3 months only** | `STARTDATETIME`/`TIMESPAN` | ✅ Verified (blog) — good for *dry-run validation*, not walk-forward |
| **Alpha Vantage NEWS_SENTIMENT** | Unknown depth; docs example re-queries **2022-04** | `time_from`/`time_to` + `sort=EARLIEST`, limit 1000 | ✅ parameter verified; depth ⚠️ |
| **Finnhub `/company-news`** | **1 year on free tier**, 20 yrs paid | `from`/`to` per symbol | ✅ pricing page; but symbol-centred (stocks), crypto-general feed has **no** range ✅ (SDK) |
| **GNews paid** | **"Historical data since 2020"** | API `topic`/`query` + date params | ✅ pricing page; free tier only 30 days |
| **NewsAPI Business** | 5 years | `from`/`to` | ✅ pricing page; $449/mo |
| **CryptoPanic** | Plan-dependent "History 1 month / 1 year" (self-contradicted) | Pagination only; **no date-range param on public docs** | ⚠️ contradiction recorded (§2.1) |
| **Marketaux** | Date filters per docs | — | ⚠️ unrendered this session |
| **RSS feeds (all)** | None | Must self-archive from day 1 | ✅-by-absence |
| **X API** | Effectively none at cheap tiers | Archive-search entitlement unclear post-pricing-change | ⚠️ |

Backtestable-anywhere summary: **GDELT (free, deep, aggregate-granularity), Alpha Vantage (cheap, per-article pre-scored, depth unverified), GNews Essential (€49.99/mo, since 2020, full text), Finnhub company-news (free, 1 year, stock-symbol framing), NewsAPI Business ($449/mo, 5 yrs).** Everything else = live-only or collect-forward.

---

## 4. Sentiment pipelines without "LLM vibes"

### 4.1 Pre-scored sources (zero local NLP)
- **Alpha Vantage NEWS_SENTIMENT**: per-article `overall_sentiment_score` (−1…1 with published band thresholds) + per-ticker scores/relevance — a ready-made feature: filter `tickers=CRYPTO:BTC`, aggregate mean score & article count per 1 h bucket. ✅ (§2.3)
- **CryptoPanic crowd votes**: `votes.positive / votes.negative` + `filter=bullish|bearish` + enterprise `panic_score (0–100)` and per-period (1h/6h/24h) panic scores — crowd-labelled, not model-labelled; historical API access is the bottleneck (§2.1). ✅ schema / ⚠️ plan limits
- **GDELT tone**: article tone filter (`tone<n>`/`tone>n`) and timeline tone modes; GKG carries per-document tone fields ⚠️ (codebook unread this session). Aggregate, global-press scale. ✅ API semantics (§2.5)
- **Marketaux**: entity-level sentiment_score + per-entity market cap in one response (Standard+ plans). ⚠️ unrendered docs
- Pre-scored is the cheapest to make **deterministic** (reproducible in backtest); vote-based labels are not reproducible at article-publication time from an archived page — beware look-ahead of crowd votes when replaying (votes accumulate after publication; backtesting vote features needs vote-count-by-timestamp data, which the CryptoPanic API doesn't provide ⚠️).

### 4.2 Lexicons / classical models (if scoring locally)
- **VADER** (Hutto & Gilbert 2014): social-media-tuned parsimonious rule-based lexicon; the survey records its crypto use — Smuts ran VADER on Telegram sentiment feeding an LSTM with "76% accuracy … predicting hourly prices" in H1-2018 (§7.2.4). Repo: https://github.com/cjhutto/vaderSentiment (MIT) ⚠️ (license from repo standard knowledge; not re-checked this session).
- **FinBERT (ProsusAI)**: BERT-base fine-tuned on Financial PhraseBank (Malo 2014) + Reuters TRC2; softmax labels `positive/negative/neutral`; **license CC BY-NC-SA 4.0 — non-commercial only** (fine for a private bot, flagged for anything commercial). ✅ Verified — https://huggingface.co/ProsusAI/finbert (model card, license line, label set)
- **TextBlob**: recorded by the survey (Li et al. used it inside an XGBoost pipeline, Pearson 0.806 hourly index vs price, §7.2.4).
- CryptoTrade's LLM summarization (below) is the *later* layer, not v0.2's classifier feature.

### 4.3 What the CryptoTrade paper (arXiv 2407.09546) actually does with news — where the LLM layer would sit *later*
- Data collection (§2.1): off-chain news pulled **daily** per coin via the **Gnews API** (pypi `gnews` — a Google News front), filtered for "reputable financial and cryptocurrency-specific outlets such as Bloomberg, Yahoo Finance, and crypto.news"; Gnews ToS constraint (non-commercial, no mirroring) is acknowledged in Appendix B.
- Pipeline (§2.2): news is **summarized with GPT-3.5-turbo**, then a dedicated **News Analyst agent** ("extract [and analyze] critical information from the latest news to assess the potential market impact") reports to a **Trading agent** producing daily buy/sell/hold actions (§2.3) — trading frequency is **day-level, not hour-level**; a **Reflection agent** re-analyzes "the previous week's prompts, decisions, and returns" to feed the next decisions (§2.4).
- Evidential weight of news in their ablation (§3.3, Table 5, ETH bull, GPT-4o): Full prompt 28.47% return / 0.23 Sharpe; **"w/o News" 19.69% / 0.06** — removing news cost ~8.8 pp return and most of the Sharpe. ("w/o TxnStats" hurt most by their own account.)
- Limitations the authors themselves flag (§6): "relatively limited dataset", day-to-day cadence ("aim … to hour-to-hour or minute-to-minute"), and zero-shot (no fine-tuning) LLMs underperforming traditional signals in places — i.e., **the paper is a design precedent for a later LLM Evaluate/News-analyst layer, not evidence that an LLM beats a classifier at hourly frequency**.
- Licensing note: their dataset is CC BY-NC-SA (Appendix A) — inspiration-only, consistent with the repo's earlier "inspiration-only" verdict.

### 4.4 What the survey (arXiv 2003.11352) records about news/sentiment signal usefulness
- ML feature framing (§3.3.2, "Machine Learning Technology"): inputs groups — "Economic indicators …, **Social indicators (Google Trends, Twitter, etc.)**, Technical indicators (price, volume, etc.) and … Seasonal indicators"; sentiment data "typically has to be **combined with Machine Learning for the generation of trading signals**" (§7.2.4) — i.e., survey precedent for news-as-feature-into-classifier, exactly the v0.2 shape.
- Quotable finding (§7.2.4 Sentiment Analysis, verbatim): "Sentiment analysis, a popular research topic in the age of social media, has also been adopted to improve predictions for cryptocurrency trading. This data source typically **has to be combined with Machine Learning for the generation of trading signals**."
- Recorded results (§7.2.4): Lamon et al. — news+social headline classifier on price-direction labels, Logistic Regression best, "43.9% of price increases correctly predicted and 61.9% of price decreases" (daily); Smuts — VADER on Telegram + Google Trends, LSTM, "backtesting reached 76% accuracy … predicting hourly prices" (H1-2018); Li et al. — TextBlob + gradient boosting, "Pearson correlation of 0.806" hourly (ZClassic); Bouri & Gupta — "The predictive power of **Internet-based** economic uncertainty-related query indices is **statistically stronger than that of newspapers** in predicting Bitcoin returns" (a caution that *news text alone* was weaker than search/social metrics); Flori — "news and media attention seem to contribute to influence the demand for Bitcoin" (§7.2.4).
- Data-quality caution (§10.4, citing Alexander et al.): "less than half the cryptocurrency papers published since January 2017 employ correct data" — argues for timestamp-integrity discipline (same-timezone alignment, no-lookahead) when merging news into 1 h candles.
- Opportunity framing (§11, verbatim): "**Sentiment-based research.** … there is a substantial body of work, which uses natural language processing technology, for sentiment analysis with the ultimate goal of **using news and media contents to improve the performance of cryptocurrency trading strategies**." — the survey's own open-direction endorsement of news-as-input.

---

## 5. Integration shape — news features per 1 h candle in a freqtrade informative context

Facts below are from the official freqtrade stable docs (doc source verified at `freqtrade/freqtrade` repo, `docs/` markdown; the site is docsify-rendered from these files):

- **`informative_pairs()`**: define extra `("pair", "timeframe")` tuples; freqtrade downloads them "as part of the regular whitelist refresh process and [they are] available via `DataProvider` just as other pairs"; "These pairs will **not** be traded"; "it's best to keep this list short"; optional 3rd tuple element for candle type. ✅ Verified — https://www.freqtrade.io/en/stable/strategy-customization/ (`Informative Pairs` section; note freqtrade's DataProvider is **ohlcv-shaped** — it fetches *candles*, not news).
- **`@informative` decorator**: merges an informative dataframe into `populate_indicators()` with `ffill`, column formats, and **`cache: bool = True`** — and the docs explicitly say: "Use `cache=False` on methods that use **non-OHLCV data**, have side effects, or otherwise need to run for every base pair." The reserved column `date_merge` must not be returned. ✅ Verified — same page (`Informative pairs decorator`).
- **`merge_informative_pair()`**: the documented lookahead-safe merge: informative dates shifted by `timeframe_to_minutes(inf_tf)` into a `date_merge` column, `pd.merge(left_on='date', right_on='date_merge', how='left')` then `ffill`; docs also show the custom manual implementation. ✅ Verified — same page (`merge_informative_pair()`).
- **DataProvider** (`self.dp`): `get_pair_dataframe(pair, timeframe)` (historical in backtest inside `populate_*` returns the *full timerange*; in callbacks up to the simulated candle), `historic_ohlcv`, plus live-only `orderbook`/`ticker`/`check_delisting` — each with an explicit docs warning that using them in backtest "will not work correctly." Hyperopt: "The DataProvider is available during hyperopt, however it can only be used in `populate_indicators()` … not available in `populate_entry_trend()` and `populate_exit_trend()`." ✅ Verified — same page (`Additional data (DataProvider)`).
- **External-data seams (the factual precedent for news)**: `bot_loop_start()` is documented as "called once at the start of every bot throttling iteration in dry/live mode (roughly every 5 seconds …) **or once per candle in backtest/hyperopt mode**" and its job description literally includes "**loading of external data, etc.**" — the official docs even show `requests.get("https://some_remote_source.example.com")` guarded by `runmode` checks. ✅ Verified — https://www.freqtrade.io/en/stable/strategy-callbacks/ (`Bot loop start`). Caveat in same docs: heavy/network work in `confirm_trade_entry`/`confirm_trade_exit` is discouraged ("Timing … is critical, so avoid doing heavy computations or network requests").
- **Determinism rules that bind a news feature**: "during backtesting the full time range is passed to the `populate_*()` methods at once … avoid index referencing (`df.iloc[-1]`)" and the "Warning: Using future data" — news timestamps must be merged strictly `date_merge` ≤ candle-close with `ffill`, never reversed. Freqtrade ships `lookahead-analysis` and `recursive-analysis` commands to check this before dry/live. ✅ Verified — strategy-customization (`Strategies and Backtesting`, `Lookahead and recursive analysis` boxes).
- **No first-class news connector exists in the strategy docs** (no news plugin, no non-OHLCV loader in the DataProvider surface) — the sanctioned seams are exactly: `informative_pairs` (candles), `@informative`/`merge_informative_pair` (any dataframe, incl. a locally-computed news-feature frame), `bot_loop_start` (external fetch), and offline pre-computation into a local file the strategy merges by date. Community strategies that consume external data follow these seams; the docs themselves do not prescribe more. (Stated strictly from docs scope this session; a separate `dp.add_custom_data`-style API is ⚠️ not documented in stable.)

---

## 6. Design implications for v0.2 (neutral — no decision made here)

- **Backtestability is the binding constraint, not richness.** Only GDELT raw files (free, 2015→), Alpha Vantage NEWS_SENTIMENT (`time_from` ranges; depth unverified), GNews paid (since 2020, €49.99/mo), Finnhub company-news (free 1 yr, stock-symbol framing) and NewsAPI Business ($449/mo) are verified historical paths. RSS, X, and live-only CryptoPanic pages are collect-forward.
- **A "collect-forward now, backtest later" bridge exists regardless of source choice**: start archiving RSS/FinVANTAGE-style raw items with UTC timestamps during v0.1 dry-run (CoinDesk + Cointelegraph verified live with per-second `pubDate`), because every non-historical source becomes the next GDELT-quality archive in ~6 months.
- **Pre-scored vs local-scoring tradeoff:** AV gives per-article per-ticker sentiment with second timestamps (deterministic replay); GDELT gives free aggregate tone/volume history (no per-coin entity layer); CryptoPanic's votes are crowd signals that cannot be replayed with publication-time vote counts — a vote-feature backtest would embed look-ahead unless the API exposes vote-state-by-timestamp (not documented ⚠️).
- **Hourly alignment is mechanical, not exotic**: freqtrade's own `merge_informative_pair` semantics (date-merge ≤ candle date + `ffill`) define the correct news-candle join; aggregation windows (e.g., 1 h/24 h article counts, mean sentiment delta) would be computed *outside* the join.
- **Survey evidence supports news-as-feature-into-ML** ("has to be combined with Machine Learning" §7.2.4) but also shows internet-search/social-sentiment metrics outperforming newspaper metrics in one recorded comparison (§7.2.4) — v0.2 spec may want to weigh search-volume/social features alongside news text.
- **The LLM layer's reserved seat (per CryptoTrade)**: news → summarization → dedicated news-analyst + reflection loop, at *daily* cadence in their paper; keeping v0.2 deterministic (classifier features) leaves that slot for a later phase without architectural rework.
- **Compliance landmines noted**: NewsAPI free = dev-only/24 h-delay; GNews free = non-commercial; FinBERT weights = CC BY-NC-SA (non-commercial); CryptoPanic = branding prohibition + revocation right + request logging; Alpha Vantage = free-tier ambiguity on this endpoint worth one email/one test-key.
- **Cost ladders are modest**: fully-free walk-forward path exists (GDELT archive + self-archived RSS + AV @ 25/day if the endpoint draws on it); a pragmatic paid step is ~$50/mo (AV premium or GNews Essential — the same tier CryptoTrade used) before CryptoPanic's $199 or NewsAPI's $449.
- **Open verification items before the v0.2 spec freezes**: (1) AV NEWS_SENTIMENT free-tier eligibility + crypto archive depth (one free key answers both), (2) Finnhub `/news?category=crypto` depth from a real token, (3) CryptoPanic free-plan limits + Growth history (dashboard), (4) Marketaux current live pricing/date-filter docs, (5) GDELT terms-of-use attribution language.

---

## Sources used (exact URLs)

**CryptoPanic** — API docs: https://cryptopanic.com/developers/api/ (headless render needed) · Overview/terms: https://cryptopanic.com/developers/api/about/ · Plans: https://cryptopanic.com/developers/api/plans/ · PLUS page (non-API plan): https://cryptopanic.com/plus/
**Finnhub** — pricing: https://finnhub.io/pricing · official SDK client source: https://raw.githubusercontent.com/Finnhub-Stock-API/finnhub-python/master/finnhub/client.py · docs pages (unrenderable this session): https://finnhub.io/docs/api/news
**Alpha Vantage** — NEWS_SENTIMENT docs: https://www.alphavantage.co/documentation/ · live demo response: https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo · free-tier FAQ: https://www.alphavantage.co/support/ · premium: https://www.alphavantage.co/premium/
**NewsAPI.org** — pricing/plan rules: https://newsapi.org/pricing · sources index: https://newsapi.org/sources
**GDELT** — data overview: https://www.gdeltproject.org/data.html · DOC 2.0 API: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ · live file index: https://data.gdeltproject.org/gdeltv2/lastupdate.txt
**Marketaux** — pricing (Wayback snapshot 2025-04-26): https://web.archive.org/web/20250426201929/https://www.marketaux.com/pricing
**GNews** — pricing/FAQ: https://gnews.io/pricing
**X API** — overview/tiers: https://docs.x.com/x-api/getting-started/about-x-api · pay-per-usage pricing: https://docs.x.com/x-api/getting-started/pricing.md
**RSS** — CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/ (live) · Cointelegraph: https://cointelegraph.com/rss (live) · Reuters `feeds.reuters.com` (dead endpoint, verified by attempt)
**Freqtrade** — https://www.freqtrade.io/en/stable/strategy-customization/ and https://www.freqtrade.io/en/stable/strategy-callbacks/ (doc source verified at https://github.com/freqtrade/freqtrade/tree/stable/docs)
**Papers** — CryptoTrade: https://arxiv.org/abs/2407.09546 (§2.1, §2.2, §2.3, §2.4, §3.3 Table 5, §6, App. A–B) · Survey: https://arxiv.org/abs/2003.11352 (§3.3.2, §7.2.4, §10.4, §11)
**Sentiment models** — FinBERT model card: https://huggingface.co/ProsusAI/finbert · VADER: https://github.com/cjhutto/vaderSentiment (license ⚠️ from standard knowledge)
