# Open historical BTC 1h data sources + freqtrade import path — fact-finding (v0.3 splits)

Primary-source-verified 2026-11-10 (live probes ~20:43–20:48 UTC against real endpoints, freqtrade 2026.10 installed in this repo's venv, CCXT 4.5.92). Research-only.

Use for: choosing the historical feed for the pinned 12m-train/3m-val/3m-test walk-forward protocol (arXiv 2606.00060-style), the import commands, and the venue-mismatch risks documented below.

## TL;DR

- **Deepest key-free source = Binance public data dumps** (`data.binance.vision`): spot BTC/USDT 1h back to **2017-08-17 04:00 UTC**; USDT-M futures 1h back to **2020-01-01**. Verified with S3 listings + real zip downloads; no account, no geo block (this machine's network at least).
- **freqtrade natively downloads from these dumps**: `freqtrade download-data --exchange binance` (2026.10 ships `binance_public_data.py` which fetches `data.binance.vision` daily zips and stores feather). **Verified end-to-end key-free in this repo's venv**: 1h data from 2017-09 downloaded into a temp datadir and listed back.
- **Bybit's exchange-side floor (verified empirically)**: spot BTCUSDT 1h klines start **2021-07-05 12:00 UTC**; USDT-perp (linear BTCUSDT) starts **2020-03-25 10:00 UTC**. Bybit REST therefore covers any 2024-01-01→today extension without venue mixing, but cannot go to 2018.
- CryptoCompare min-api is **no longer key-free** (401 "API key required"). OKX public history does not serve 2020/2015 1H probes. Coinbase serves BTC-**USD** (not USDT) from ≤2016-01, key-free but quote-mismatched.

## Sources table (verified 2026-11-10)

| Source | Pair/quote | Verified earliest 1h candle | Freshness | Key-free? | Format / notes |
|---|---|---|---|---|---|
| Binance data dumps, spot (`https://data.binance.vision/data/spot/monthly+klines/…`) | BTCUSDT USDT | **2017-08-17 04:00 UTC** (first 1h file covers from here; monthly zips 2017-08…2026-10 exist; freqtrade BTC/USDT 1m docs sample also starts 2017-08-17 04:00) | Monthly zip for 2026-10 published 2026-11-02; daily zips through yesterday (HEAD `BTCUSDT-1h-2026-11-09.zip` → HTTP 200) | Yes (HTTP GET, no auth; S3 listing API works) | CSV inside zip: headerless, 12 cols: `open_time,open,high,low,close,volume,close_time,quote_vol,count,taker_buy_vol,taker_buy_quote_vol,ignore` (ms epochs; sample 2017-08 verified) |
| Binance data dumps, USDT-M futures (`data/futures/um/monthly+klines/…`) | BTCUSDT perp | **2020-01-01** (monthly list starts 2020-01; 404 for 2019-09-08 daily) | same | Yes | Same CSV schema; freqtrade explicitly advises splitting futures downloads at 20200101 for BTC/USDT:USDT |
| freqtrade native dumps downloader (`--exchange binance`) | BTC/USDT spot | 2017-09-01 (this probe's `--timerange 20170901-20171001` run stored 999 1h candles 2017-09-01→2017-10-12, feather) | pulls daily zips, caps at now−2 days; 404 → falls back to REST | Yes | Writes freqtrade feather directly (schema below) |
| Bybit v5 REST `/v5/market/kline` (what `download-data` uses for bybit) | spot BTCUSDT | **2021-07-05 12:00 UTC** (descended 47 pages to empty; explicit probes: data at 12:00, empty at 11:00 and everything older) | current hour (2026-11-10 20:00 candle present) | Yes | ccxt `fetch_ohlcv`/raw pagination; 1000/call |
| Bybit v5 REST, linear (USDT perp) `BTCUSDT` | BTCUSDT:USDT | **2020-03-25 10:00 UTC** | same | Yes | relevant if futures venue ever used |
| OKX REST `market/history-candles` BTC-USDT 1H | BTC-USDT | **does not serve 2020 or 2015** (probes returned the *latest* candles instead of requested old range) | current | Yes | docs warn 100 candles/call; shallow in practice |
| CryptoCompare `min-api.cryptocompare.com/data/v2/histohour` | BTC/USDT | n/a — **HTTP 401 "API key required"** on all probes (CoinDesk-gated now) | — | No | needs key; excluded |
| Coinbase Exchange `/products/BTC-USD/candles` | BTC-**USD** | ≤2016-01 (data returned for 2016-01-01 probe; 2015-01-01 probe empty) | current | Yes | seconds epochs, column order `[time,low,high,open,close,volume]`, newest-first; wrong quote currency — cross-check use only |
| Kraken | BTC/EUR|USD|USDT | not probed; freqtrade docs: public OHLC = **720 candles only**; deep history via Kraken's trades-zip files → `convert-trade-data --format-from kraken_csv` | — | Yes (manual download) | high effort, only if a second venue needed |

Licensing: none of the probed feeds carries an explicit OSI-style license. Binance dumps ship unlicensed data with CHECKSUM sidecars; freqtrade/freqtrade-public-data treat them as exchange-provided public archives. Treat all as "research use, verify terms before redistribution".

## freqtrade import path (verified commands)

### Preferred: native download from the dumps (key-free, EU-safe)

```bash
# Full history, 1h BTC/USDT, feather (default format). Uses data.binance.vision under the hood.
uv run freqtrade download-data --exchange binance -p BTC/USDT -t 1h --timerange 20170817-

# Verify what landed
uv run freqtrade list-data --exchange binance --show-timerange
```

Verified end-to-end today (no config, no keys, temp dirs):

```bash
uv run freqtrade download-data --exchange binance -p BTC/USDT -t 1h --timerange 20170901-20171001 --datadir <dir> --userdir <dir>
# log: "Downloaded data for BTC/USDT, 1h, spot with length 999"
uv run freqtrade list-data --datadir <dir> --show-timerange
# BTC/USDT | 1h | spot | 2017-09-01 00:00 | 2017-10-12 20:00 | 999
```

Mechanism (source: `.venv/Lib/site-packages/freqtrade/exchange/binance_public_data.py`): fetches **daily** zip archives per day from `https://data.binance.vision/data/{spot|futures/um}/daily/klines/BTCUSDT/1h/…`, caps end at **now−2 days** (daily-archive delay), and on 404 falls back to the slower REST API; for futures BTC/USDT:USDT it explicitly suggests splitting ranges at 20200101. Config knob `exchange.only_from_ccxt` (default `false`) disables the dumps path. Note the probe over-fetched past the requested end (999 candles to 2017-10-12 for a range ending 2017-10-01) — always verify with `list-data --show-timerange`; freqtrade trims to `--timerange` at load time.

### `convert-data` (format conversion only — not a CSV importer)

```
uv run freqtrade convert-data --format-from json --format-to feather --datadir user_data/data/binance -t 1h
```

Verified present in 2026.10 (`--exchange` valid only config-less). It converts between freqtrade's own storage formats (json/jsongz/feather/parquet); it cannot import raw Binance CSV dumps. There is no built-in kline-CSV importer — either use the native dumps downloader above, or convert CSVs manually per the recipe below.

### Manual CSV → feather recipe (only if bypassing the native downloader)

File must satisfy the schema that `FeatherDataHandler`/`ArrowDataHandler` write and read (source: `freqtrade/candle_columns.py`, `data/history/datahandlers/arrowdatahandler.py`, `featherdatahandler.py`):

- filename: `user_data/data/binance/BTC_USDT-1h.feather` (pair `/` → `_`; futures candle types go into a `futures/` subdir with `-futures` suffix, e.g. `BTC_USDT-1h-futures.feather`)
- columns, exact order: `date, open, high, low, close, volume` (`OHLCV_COLUMNS`)
- dtypes: value columns float64; `date` tz-aware UTC datetime (stored as `datetime64[us, UTC]`; loader normalizes with `.dt.as_unit("ms")`)
- stored without index (`reset_index(drop=True)`), `to_feather(..., compression="lz4", compression_level=9)`
- loader tolerates a 6-column positional layout, but named columns are the canonical form

```python
import pandas as pd
df = pd.read_csv("BTCUSDT-1h-2017-08.csv", header=None,
                 usecols=[0,1,2,3,4,5], names=["date","open","high","low","close","volume"])
df["date"] = pd.to_datetime(df["date"], unit="ms", utc=True).dt.as_unit("us")
df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
df.reset_index(drop=True).loc[:, ["date","open","high","low","close","volume"]] \
  .to_feather("user_data/data/binance/BTC_USDT-1h.feather", compression="lz4", compression_level=9)
```

Schema of the file freqtrade itself produced (probe): `date datetime64[us, UTC]`, five float64 columns, RangeIndex, 2017-09-01 00:00 UTC → …, ms-epoch open times.

### Backtesting on imported (offline) data

- `freqtrade backtesting` has **no `--exchange` flag** — the pair files live under `user_data/data/<exchange>/` and the exchange comes from the config. Options:
  - a separate backtest config with `"exchange": {"name": "binance", ...}` (empty `api_key`/`secret` are fine — configuration docs: "`exchange.api_key` … **Only required when you are in production mode**"), keeping the live/dry-run config on bybit; or
  - `--datadir user_data/data/binance-20180101` style override (documented example on the Backtesting page) with any exchange resolved in config.
- Fees: backtesting "will use the exchange's default fees" unless `--fee 0.001` is passed (applied twice: entry+exit). For paper comparability (c = 0.001, §4.1 of arXiv 2606.00060), pass `--fee 0.001` explicitly.
- Key-free offline backtesting is also implied by dry-run behaviour and the configuration table; the repo already runs key-less public-endpoint work.

### Bybit-side incremental/prepend (venue-native, no mixing)

- The existing 2025-01→ archive is Bybit. To prepend 2024 for the v0.3 protocol start: `uv run freqtrade download-data -c config.json --prepend --timerange 20240101-20250101` (docs: `--prepend` + `--timerange` with end date). Bybit REST covers this fully (floor 2021-07-05).

## Merge / venue-mismatch caveats (factual points)

1. **Spot vs futures feed in the reference paper.** arXiv 2606.00060 §3.1: "hourly OHLCV data for the **BTC/USDT USD-margined futures** contract collected from **Binance** through its public REST API… raw sample runs from **1 December 2017**". Contradiction: Binance USD-M futures listed **2019-09** and the public archive starts **2020-01** (verified: monthly list begins 2020-01, 2019-09 daily 404). A Dec-2017 Binance-futures sample is not obtainable from Binance; the paper is likely (undocumented) spot data or pre-2019 splice. RESOURCES.md's "Binance-futures hourly BTC/USDT 2018→2026" inherits this. Everything else from §3/§4 is reproducible: 70,872 hourly obs, Dec-2017 burn-in, 12m train/3m val/3m test, 3m step, 27 folds, c = 0.001.
2. **Price basis across venues.** Pre-2021-07 the *only* USDT deep series with verified depth is Binance spot (Bybit spot didn't exist; Bybit floors: spot 2021-07-05, perp 2020-03-25). Any Bybit→older-history merge has a venue seam at 2021-07-05 12:00 UTC (spot) or 2020-03-25 (perp). Hourly BTC closes across major venues typically track within basis points, but the seam lands inside the training/test grid unless splits are chosen at month boundaries.
3. **Cost model mismatch.** Backtesting fees come from the *config'd* exchange's market info: Binance-data-under-binance-config prices with Binance spot fees, while live is planned on **Bybit spot** (0.1%). The paper sidesteps this with a flat c = 0.001 all-in cost — replicate with `--fee 0.001` so both venues and the paper share one cost model; don't let the fee silently follow the data's venue.
4. **Volume semantics.** Binance spot `volume` = base-asset BTC volume (12-col CSV, verified sample); Binance UM futures volume = contracts (BTC for linear). Same unit, different scale — never merge spot and futures columns into one series; keep volume-feature comparisons within one venue series.
5. **Funding/mark candles.** The paper excludes funding-rate variables. If any futures backtests are ever run, bybit funding history is not served (freqtrade exchanges doc: dry-run calculation is used) while OI history is full on bybit (data-download doc note) — spot-only data avoids this entirely.
6. **Data quality.** Binance has outage gaps (notably 2021-05); the paper fills missing hours forward with previous close + zero volume (§3.2). freqtrade's loader default `fill_missing=True` does zero-volume gap fill too — decide consciously whether to replicate the paper's fill or to keep genuine gaps and use `fill_missing=False` for the splits.
7. **EU-block caveat rechecked.** api.binance.com REST returned HTTP 200 from this network today, and data.binance.vision (CloudFront/S3, key-free) works outright; freqtrade docs list geo-blocks (CA/NL/US…) only for API access, and RESOURCES.md's "account-blocked for EU since May 2026, public archives unaffected" is consistent with what was probed: archives are unaffected, REST klines also respond from this network today.

## Design implications for v0.3 (neutral bullets)

- **Immediate protocol start needs no foreign venue**: the pinned protocol (12m/3m/3m, ≥18 months) starting at 2024-01-01 can be extended entirely on Bybit (floor 2021-07-05 → covers it) with the venue already used live: `--prepend --timerange 20240101-` style download. Zero venue mixing for splits starting 2024+.
- **Max depth (≥2018) only exists on Binance**: 2018→2021-07 must come from Binance spot dumps (2017-08-17 start verified). Prefer running deep-history walk-forwards as a *single-venue Binance series* rather than splicing bybit onto binance mid-run; if splicing is kept, put the seam at a month-boundary fold edge (protocol steps by 3-month months).
- **Paper-exact replication** (same folds ± same data semantics) would use Binance UM futures from 2020-01-01 (verified earliest achievable), not the paper's claimed Dec-2017 futures start, or Binance spot to reach 2018 — document whichever comparison is claimed.
- **Import**: the native `freqtrade download-data --exchange binance` route is documented-adjacent (`only_from_ccxt` + `binance_public_data.py`) and verified working key-free; manual feather writing per the recipe above is unnecessary unless custom cleaning is wanted. `convert-data` handles format conversion, not CSV import.
- **Cost comparability with the paper** is achievable via `--fee 0.001` under either venue config; keep the cost model explicit in the results store (λ, c) rather than inheriting the backtest config's exchange fee.
- **Freshness at the right edge**: dump dailies lag ~2 days (freqtrade caps at now−2d); the final few candles per snapshot should come from the existing bybit REST incremental download or be accepted at T−2.
- **Missing-hour policy** must be pinned before building splits: paper-style forward-fill (freqtrade default `fill_missing=True`) vs genuine gaps (`fill_missing=False`). Binance 2021-05 outage sits inside the deep-history span.

## Contradictions / open items

1. Paper's Dec-2017 Binance-futures start is impossible (futures listed 2019-09; archive 2020-01) — unresolved in the paper; affects any " replicate exactly" claim.
2. RESOURCES.md gap listed "Bybit OHLCV via CCXT" as a candidate deep source — empirically it is shallow for max depth (floor 2021-07-05) but sufficient for the pinned 2024+ protocol; update the gap note.
3. 2026-11 monthly dump not yet published (probe 20:47 UTC): latest spot monthly = 2026-10; use daily zips (verified for 2026-11-09) or bybit REST for the current month tail.
4. Binance daily kline archives for the launch week (2017-08-17/18) were not individually probed (monthly 2017-08 verified instead); freqtrade's downloader uses daily files and warns/falls back to REST on missing first days — expect it to handle the oldest range transparently.
5. CryptoCompare was listed in some earlier notes as key-free — now 401-gated; only usable with a key.
