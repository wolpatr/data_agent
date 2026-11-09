# Trigger strategy fact-finding — freqtrade strategy anatomy + cited baseline (v0.1)

**Date:** 2026-11-09
**Scope:** Freqtrade stable docs (https://www.freqtrade.io/en/stable/), freqtrade `stable` branch source (template + `strategy_resolver.py` + `interface.py`), the freqtrade-strategies GitHub repo, TA-Lib docs, and three papers: Fang et al. (arXiv 2003.11352), Bysik & Ślepaczuk (arXiv 2606.00060), Jabbar & Jalil (arXiv 2407.18334). Research only — no decisions made here. Target: v0.1 paper/dry-run trigger baseline, BTC/USDT Bybit spot, 1h candles, long-only, fixed stake.

**Verification key:** `[V]` verified against the cited primary source during this scan (2026-11-09, docs as served that day). `[U]` unverified / community-only claim, kept only to flag what still needs a source.

Cross-references a sibling scan already in this folder: `research/freqtrade-risk-rails.md` (protections + stoploss mechanics vs freqtrade develop source).

---

## 1. Freqtrade strategy anatomy (stable, 2026-current)

- Strategy anatomy page states the strategy file contains: candle data handling, indicators, entry logic + signals, exit logic + signals, Minimal ROI, stoploss (fixed/trailing/callbacks), pricing, position adjustment, plus callbacks.
  - `[V]` https://www.freqtrade.io/en/stable/strategy-customization/ ("Anatomy of a strategy")
- `INTERFACE_VERSION` defines the strategy interface version; "The current version is 3 — which is also the default when it's not set explicitly in the strategy." In source: `INTERFACE_VERSION: int = 3` on `IStrategy`.
  - `[V]` https://www.freqtrade.io/en/stable/strategy-customization/ + https://raw.githubusercontent.com/freqtrade/freqtrade/stable/freqtrade/strategy/interface.py
- Required methods (v2/v3 signature, all take `(dataframe: DataFrame, metadata: dict)`): `populate_indicators`, `populate_entry_trend`, `populate_exit_trend`. Resolver validation rejects a strategy missing entry/exit trend overrides ("`populate_entry_trend` or `populate_buy_trend` must be implemented", "`populate_exit_trend` or `populate_sell_trend` must be implemented"). `populate_indicators` is `@abstractmethod` on the interface.
  - `[V]` interface.py + https://raw.githubusercontent.com/freqtrade/freqtrade/stable/freqtrade/resolvers/strategy_resolver.py
- Signal convention (long-only spot): entry — dataframe column `enter_long` set to `1` for entries, `0` for no action ("enter_long is a mandatory column"); exit — column `exit_long` = `1`. Optional tags: `enter_tag`, `exit_tag`. A trade opens "on the next open candle" after the signal appears on the last closed candle.
  - `[V]` https://www.freqtrade.io/en/stable/strategy-customization/ ("Entry signal rules", "Exit signal rules")
- Signal collision: "When conflicting signals collide (e.g. both 'enter_long' and 'exit_long' are set to 1), freqtrade will do nothing and ignore the entry signal."
  - `[V]` strategy-customization ("Colliding signals")
- Vectorised assignment style (used by all official examples):
  `dataframe.loc[(guards) & (dataframe['volume'] > 0), 'enter_long'] = 1`; `volume > 0` is the docs' own guard ("Buying requires sellers to buy from. Therefore volume needs to be > 0").
  - `[V]` strategy-customization (Dataframe, Entry signal rules, Note before Exit signal rules)
- Attribute defaults (strategy-class attributes, current stable):
  - `IStrategy` source: `can_short: bool = False` — "Can this strategy go short?"; resolver: `can_short` + spot trading mode raises `ImportError("Short strategies cannot run in spot markets ...")`. Docs: "If you have 1 values in the enter_short column ..., setting can_short = False (which is the default) will mean that these short signals are ignored." For our spot bot, `can_short = False` is correct and `enter_short` signals are meaningless.
    - `[V]` interface.py; strategy_resolver.py (`_strategy_sanity_validations`); strategy-customization ("Can short")
  - `use_exit_signal`, `exit_profit_only`, `ignore_roi_if_entry_signal` are annotated (untyped defaults in `interface.py`) and defaulted in the resolver attribute list: `use_exit_signal: True`, `exit_profit_only: False`, `ignore_roi_if_entry_signal: False` (also `exit_profit_offset: 0.0`). The official template sets exactly these values with the comment "These values can be overridden in the config."
    - `[V]` interface.py + strategy_resolver.py + https://raw.githubusercontent.com/freqtrade/freqtrade/stable/freqtrade/templates/sample_strategy.py
  - `process_only_new_candles: bool = True` in `interface.py` (class default True; the template sets it explicitly). Meaning per source: run `populate_indicators` only for new candle.
    - `[V]` interface.py + sample_strategy.py
  - `use_exit_signal` disables the exit-signal side but "will not influence signal collision rules"; `exit_profit_only` (False) would only exit on profit; `ignore_roi_if_entry_signal` (False) lets an entry signal suppress a simultaneous ROI exit — defaults are the ones we want for the baseline (no exotic exit-side tricks).
    - `[V]` strategy-customization (Exit signal rules) + resolver defaults
- `startup_candle_count`: "This should be set to the maximum number of candles that the strategy requires to calculate stable indicators." Warning in docs: must be below `ohlcv_candle_limit * 5` "(which is 500 * 5 for most exchanges)". Docs' worked rule of thumb: `ema100` needs ~400 candles. For a slow EMA of 26 on 1h, ~100 is the analogous scale (check with `freqtrade recursive-analysis`).
  - `[V]` strategy-customization ("Strategy startup period") — the 100-for-EMA26 inference itself is my extrapolation of the docs' example ratio, not a docs-stated number.
- Strategy class must declare `timeframe`: `strategy-customization` "Timeframe" section — "This is the periodicity of candles the bot should use in the strategy. Common values are '1m', '5m', '15m', '1h'". `"1h"` is a supported standard value; it is accessible in methods as `self.timeframe`.
  - `[V]` strategy-customization ("Timeframe")
- Pair whitelist lives in the **config**, not the strategy: `exchange.pair_whitelist` — "List of pairs to use by the bot for trading and to check for potential trades during backtesting."
  - `[V]` https://www.freqtrade.io/en/stable/configuration/ (parameters table, `exchange.pair_whitelist` row)
- `minimal_roi`: dict of minutes-since-open → ROI fraction; exits independent of signals, "The calculation does include fees."
  - `[V]` strategy-customization ("Minimal ROI")
- **Disabling minimal ROI** — two candidate conventions:
  - Documented current method: "To disable ROI completely, set it to an empty dictionary: `minimal_roi = {}`". `[V]` https://www.freqtrade.io/en/stable/strategy-customization/ ("Disabling minimal ROI")
  - Legacy community convention `minimal_roi = {"0": 100}` ("insanely high number") — I did **not** find that phrasing in the current stable docs during this scan; `[U]` in current docs (older docs/older community strategy files carried it).
  - Source-level anchor that a huge constant = effectively disabled: the resolver's fallback default for `minimal_roi` is `{"0": 10.0}` (10 = 1000% profit, unreachable). `[V]` strategy_resolver.py (attribute list)
  - Interaction with exit signals: ROI exits happen independently of signals; `ignore_roi_if_entry_signal=False` (default) means an entry signal does **not** block an ROI exit on the same check. With ROI disabled, exits come only from exit signals, stoploss, trailing, or custom hooks. `[V]` strategy-customization ("Minimal ROI", "Exit signal rules") + resolver defaults

## 2. freqtrade-strategies repo — simplest maintained MA-crossover example

Repo: https://github.com/freqtrade/freqtrade-strategies (GPL-3.0, default branch `main`; 5.6k stars). README framing:

> "They also mostly should serve as a starting point for your own strategies, not as 'ready to use' strategies." (README, "Free trading strategies")

- `[V]` README: https://raw.githubusercontent.com/freqtrade/freqtrade-strategies/main/README.md (branch `develop` does not exist → 404; `main` serves it)
- README FAQ also confirms: "All strategies of the repo are into `user_data/strategies`" and uses `freqtrade trade --strategy Strategy001` as its install/test example.
- **`Strategy001.py`** is the simplest root-level maintained moving-average cross strategy in the repo:
  - URL: https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/Strategy001.py (raw: https://raw.githubusercontent.com/freqtrade/freqtrade-strategies/main/user_data/strategies/Strategy001.py)
  - File: class `Strategy001(IStrategy)`; `INTERFACE_VERSION: int = 3`; `timeframe = '5m'`; `process_only_new_candles = True`; `minimal_roi = {"60": 0.01, "30": 0.03, "20": 0.04, "0": 0.05}`; `stoploss = -0.10`; `use_exit_signal = True`; `exit_profit_only = True` (note: not the default); `ignore_roi_if_entry_signal = False`.
  - Fast/slow periods: **EMA 20 / EMA 50** for the entry — `qtpylib.crossed_above(dataframe['ema20'], dataframe['em50'])` … actually exactly `crossed_above(ema20, ema50)` (golden cross), plus two Heikin-Ashi guards (green bar, HA close above ema20).
  - Exit rule: `qtpylib.crossed_above(dataframe['ema50'], dataframe['ema100'])` **plus** red HA bar and HA-close below `ema20` — i.e. an **asymmetric** exit: EMA50 crossing *above* EMA100 is the trigger (with the red-bar/below-ema20 filters disambiguating direction), *not* a symmetric EMA20/EMA50 death cross.
  - `[V]` all of the above read directly from the raw file on `main` (2026-11-09).
- Other repo candidates checked and ruled out for "simplest MA cross": `MultiMa.py` and `mabStra.py` are hyperoptable ratio-of-MAs systems (TEMA/SMA families with parameter spaces, `IntParameter`/`DecimalParameter`), not plain crossovers; `UniversalMACD.py` is MACD-based; `hlhb.py` is a high/low breakout. `[V]` raw files on `main`.
- The repo also ships the **official sample/template strategy** (what `freqtrade new-strategy` starts from and what the docs quote from): https://raw.githubusercontent.com/freqtrade/freqtrade/stable/freqtrade/templates/sample_strategy.py — RSI/TEMA/Bollinger example (`[V]` file itself), useful as the canonical skeleton rather than as an MA-cross example.

## 3. Literature citation for the baseline

### Fang et al., *Cryptocurrency Trading: A Comprehensive Survey* (arXiv 2003.11352, v5 2022)
https://arxiv.org/abs/2003.11352 (full text read via https://ar5iv.labs.arxiv.org/html/2003.11352)

- Categorization quote (Section 3, "Cryptocurrency Trading Strategy"): "There are many trading strategies, which can be broadly divided into two main categories: technical and fundamental." And: "From a survey on stock prediction, we in fact know that 66% of the relevant research work was based on technical analysis; while 23% and 11% were based on fundamental analysis and general analysis, respectively." — with "Cryptocurrency trading can draw on the experience of stock market trading in most scenarios." → technical rules are the majority research base for this domain. `[V]` survey §3 (read 2026-11-09)
- Quotable finding (Section 3.2, "Systematic Trading"): "Technical analysis in cryptocurrency trading is the act of using historical patterns of transaction data to assist a trader in assessing current and projecting future market conditions for the purpose of making profitable trades." followed by **"Some experiments showed that the use of specific technical trading rules allows generating excess returns, which is useful to cryptocurrency traders and investors in making optimal trading and investment decisions"** `[60]`. `[V]` survey §3.2
- MA-family specifics gathered under §6.1 Technical Analysis (Systematic Trading review schema, Table 5):
  - "Hudson et al. applied almost 15,000 technical trading rules (classified into **MA rules**, filter rules, support resistance rules, oscillator rules and channel breakout rules). This comprehensive study found that technical trading rules provide investors with significant predictive power and profitability." `[V]` §6.1
  - "Corbet et al. analysed various technical trading rules in the form of the **moving average-oscillator** and trading range break-out strategies ... the backtest showed **variable-length moving average (VMA) rule performs best** considering it generates the most useful signals in high frequency trading." `[V]` §6.1
  - "Grovys et al. examined a **simple moving average trading strategy** using daily price data for the 11 most traded cryptocurrencies over the period 2016-2018. The results showed that, excluding Bitcoin, technical trading rules produced an annualised excess return of 8.76% ..." `[V]` §6.1 — note the "excluding Bitcoin" hedge: evidence for crypto broadly, not specifically BTC.
  - Trend-following with EMAs in crypto (§5.3 Turtle trading in crypto): "Extended Turtle Trading system is improved ... and introduces a new rule by using **exponential moving average (EMA). Three EMA values are used to trigger the 'buy' signal: 30EMA (Fast), 60EMA (Slow), 100EMA (Long)**" with backtest improvement over the original system. `[V]` §5.3
- Section numbering per the review schema in the survey (Table 5: "6.1 Technical Analysis" under Systematic Trading; "5.3 Turtle trading system in Cryptocurrency market"). `[V]`

### Bysik & Ślepaczuk, *Machine Learning-Based Bitcoin Trading Under Transaction Costs: Evidence From Walk-Forward Forecasting* (arXiv 2606.00060, v1 2026-05-19)
https://arxiv.org/abs/2606.00060 (full text read via https://arxiv.org/html/2606.00060v1)

- What it is: hourly BTC/USDT (Binance futures feed), ~70,000 observations 2018–2026, XGBoost vs LSTM vs iTransformer, 27-fold walk-forward, long-only sign rule (`pos=1` if forecast > 0 else cash) plus a cost-aware execution filter (λ·c threshold, c = 10 bp). Contribution list (§1): evaluate ML forecasts by realized trading performance; the cost-aware execution rule; controlled comparison of the three architectures. Abstract: "The strongest long-only XGBoost strategy produces annualised returns above 65% with a Sharpe ratio above one"; naive sign-based strategies "fail once transaction costs of ten basis points are imposed." `[V]` abstract + §1 + §4.1
- (a) **MA-crossover baselines: none tested.** The comparators are the ML strategies themselves and buy-and-hold (formal comparison "against the passive benchmark"). Technical analysis appears only as *features* — Table 3's candidate families include `DIST_SMA` (distance to simple moving average) and normalized `MACD`/`MACD_HIST` over windows {3…336}h — not as a trading-rule baseline. Prior technical-rule strategies (RSI/MACD/Keltner) appear only in the positioning table (Cohen 2023) as literature context. `[V]` §1, §4.3 Table 3, Table 1
- (b) Contribution-location confirmation: the model/execution phase is where the paper's novelty lives ("The contribution is therefore not only a comparison of forecasting models, but an assessment of whether their predictions remain economically useful once the cost of acting on them is built into the trading decision itself", §2.4). Supports framing "v0.1 = simple infra-priming baseline; v0.2 = research-cited classifier". `[V]` §2.4
- `[U]` peer-review status: arXiv preprint ("Journal: arXiv" on its own header), University of Warsaw Quantitative Finance Research Group — treat as working paper.

### Jabbar & Jalil, *A Comprehensive Analysis of Machine Learning Models for Algorithmic Trading of Bitcoin* (arXiv 2407.18334, v1 2024-07-09)
https://arxiv.org/abs/2407.18334 (full text read via https://arxiv.org/html/2407.18334v1)

- What it is: 41 ML models (21 classifiers, 20 regressors) predicting Bitcoin prices/classifying long/short; ML + trading metrics (PNL %, Sharpe); backtest (Feb–Jul 2023), forward test (Aug–Oct 2023), plus "real-world" runs. Abstract: "certain models, such as Random Forest and Stochastic Gradient Descent, outperform others in terms of profit and risk management." `[V]` abstract + §III
- (a) **Own MA-crossover baseline: none.** But the literature review explicitly records an MA baseline being beaten by ML: "[9] compared the effectiveness of **Simple Moving Average (SMA)** and Radial Basis Function Neural Network (RBFNN) methods. The study demonstrated that **RBFNN significantly outperforms SMA**, providing a more accurate tool for forecasting Bitcoin prices." `[V]` §II Literature Review
- (b) Contribution-location confirmation: the contribution is the 41-model comparison and evaluation framework ("Our research contributes to the existing literature by providing a comprehensive analysis of various machine learning models in the context of Bitcoin trading", §I), not the trading plumbing — supports the same v0.1/v0.2 framing. `[V]` §I
- `[U]` peer-review status beyond arXiv; CC BY 4.0.

**Framing support (both 2024/2026 papers):** model/classifier phase is where their contributions live; neither benchmarks its contribution against a hand-built MA-crossover *trading-rule* baseline in backtest, and the survey treats technical/MA rules as a well-established (older) layer of the field. That is consistent with shipping v0.1 as a deliberately simple, research-cited MA-cross baseline whose job is exercising the infrastructure.

## 4. EMA conventions on BTC/hourly — grounded candidates

| Pair (fast/slow) | Where it is grounded | Status |
|---|---|---|
| **12/26** (+9 signal) | TA-Lib `MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)` defaults; "MACDFIX - Moving Average Convergence/Divergence Fix 12/26" exists as its own function (`[V]` https://ta-lib.github.io/ta-lib-python/func_groups/momentum_indicators.html). MACD-style TA features (normalized MACD over hour windows) used by Bysik & Ślepaczuk (§4.3 Table 3 `[V]`); Cohen (2023) trades explicit RSI/MACD rules in the 2026 paper's positioning table `[V]` Table 1 | `[V]` as a documented cross convention — note the pair itself is the MACD fast/slow periods, not an EMA-cross trading default per se |
| **20/50** (+ 50-vs-100 exit) | freqtrade-strategies `Strategy001.py` (see §2) `[V]` | `[V]` as a freqtrade-repo example |
| **21 / 50 / 100** | Official template's commented-out EMA list: `ema3, ema5, ema10, ema21, ema50, ema100` (`[V]` sample_strategy.py) | `[V]` as the official template's example set |
| **30/60/100** | Extended Turtle EMA buy triplet in Fang et al. survey §5.3 `[V]` | `[V]` survey-recorded crypto application |
| 9/21 | Common community EMA pair — **no primary source found in this scan** | `[U]` |
| 50/200 ("golden cross") | Common convention — **no primary source found in this scan** | `[U]` |

- EMA vs SMA distinction is cheap to source: TA-Lib exposes `ta.EMA` and `ta.SMA` as separate functions, and the official template lists both side-by-side with comments `# EMA - Exponential Moving Average` / `# SMA - Simple Moving Average` — freqtrade strategies use either via talib. `[V]` sample_strategy.py + TA-Lib docs. Note: MA rules in the survey literature cover both (Hudson/Corbet/Grovys entries use MA/VMA/SMA language). `[V]` survey §6.1

## 5. Protections + stoploss in the strategy class

- **Coexistence confirmed.** `stoploss` is a bare class attribute on `IStrategy` (`stoploss: float`, no default → mandatory) and `protections` is a class attribute with default `protections: list = []`; the docs' protection examples define protections as a strategy `@property def protections(self):` returning a list of dicts. Both live in the same strategy class at the same time.
  - `[V]` https://raw.githubusercontent.com/freqtrade/freqtrade/stable/freqtrade/strategy/interface.py + https://www.freqtrade.io/en/stable/plugins/ ( StoplossGuard / MaxDrawdown / LowProfitPairs / CooldownPeriod examples all shown as `@property` on the strategy)
- **Config overrides strategy** (stoploss): stoploss page Info box: "All stoploss properties mentioned in this file can be set in the Strategy, or in the configuration. **Configuration values will override the strategy values.**"
  - `[V]` https://www.freqtrade.io/en/stable/stoploss/
- **Config overrides strategy** (general + timeframe): configuration docs, "Parameters in the strategy": "The following parameters can be set in the configuration file or strategy. **Values set in the configuration file always overwrite values set in the strategy.**" The list includes `timeframe`, `minimal_roi`, `stoploss`, `process_only_new_candles`, `use_exit_signal`, `exit_profit_only`, `ignore_roi_if_entry_signal` (i.e. `timeframe` in config wins over `strategy.timeframe`; source resolver implements exactly this precedence "Configuration → Strategy → default").
  - `[V]` https://www.freqtrade.io/en/stable/configuration/ + strategy_resolver.py (`_override_attribute_helper` docstring: "Prevalence: Configuration, Strategy, default")
- Protections cannot move to config: config-level `"protections"` was removed in 2024.10 (deprecation-turned-error) — strategy file is the only protection carrier. Already fully established in `research/freqtrade-risk-rails.md` §3 `[V]`.
- Decided rails expressed as candles (docs-recommended style, "all below examples will use the 'candle' definition"):
  - CooldownPeriod: `{"method": "CooldownPeriod", "stop_duration_candles": 2}` `[V]` plugins/ ("Cooldown Period" example is exactly 2 candles)
  - StoplossGuard: `"lookback_period_candles": 24, "trade_limit": 2, "stop_duration_candles": 4` (docs' own example shape: 24c / trade_limit 4 / stop 4c; our decided rail swaps trade_limit to 2) `[V]` plugins/ ("Stoploss Guard")
  - MaxDrawdown: `"lookback_period_candles": 168, "trade_limit": 5, "stop_duration_candles": 24, "max_allowed_drawdown": 0.2` (docs' example shape: 48c/20/12c/0.2; our decided rail swaps the numbers). `calculation_mode`: `"equity"` is docs-recommended for new setups; `"ratios"` is the current default. `[V]` plugins/ ("MaxDrawdown")

## 6. Dry-run config essentials the strategy assumes

The strategy file assumes the config supplies: `"dry_run": true` (required key, "Defaults to true"; default dry-run DB `sqlite:///tradesv3.dryrun.sqlite`, simulated `dry_run_wallet` default 1000), an exchange block for Bybit with `"pair_whitelist": ["BTC/USDT"]` (`exchange.pair_whitelist` = "List of pairs to use by the bot for trading and to check for potential trades during backtesting"; `"pairlists"` defaults to `StaticPairList`, so no pairlist config is needed for a static single pair), and `"timeframe": "1h"` — a config-overridable strategy parameter ("Parameters in the strategy" list), so setting it in config pins it over the strategy's own `timeframe = "1h"`; the two must agree for the bot to act on 1h candles. The loop is candle-aligned: freqtrade dataframe rows are candles sorted by date with "the latest complete candle always being the last in the dataframe", "all actions will be based of the last row" (closed candle), and an entry signal on that row triggers a trade "on the next open candle"; protections' locks are rounded up to the next candle, so every decision unit is a completed 1h candle. Cited config docs keys only (whitelist/timeframe/dry_run): https://www.freqtrade.io/en/stable/configuration/ ; candle-loop semantics from https://www.freqtrade.io/en/stable/strategy-customization/ and plugins/. `[V]`

## 7. Minimal complete v0.1 trigger strategy (EMA 12/26 cross, decided rails)

Long-only spot, 1h, golden-cross entry / death-cross exit, `minimal_roi` disabled, fixed rail values from the decided risk rails (see `research/freqtrade-risk-rails.md`). Claim markers per line are below the snippet.

```python
# v0.1 trigger baseline — EMA 12/26 cross, Bybit spot BTC/USDT, long-only, 1h.
# Rails: stoploss -0.05; CooldownPeriod 2c; StoplossGuard lookback 24c / trade_limit 2 / stop 4c;
#        MaxDrawdown lookback 168c / trade_limit 5 / max_allowed_drawdown 0.2 / stop 24c.
import talib.abstract as ta
from pandas import DataFrame

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import IStrategy


class TriggerEMACross(IStrategy):
    INTERFACE_VERSION = 3          # current/default interface version

    timeframe = "1h"               # must match config; config value would win anyway
    can_short = False              # spot: shorts impossible (default False, explicit)

    minimal_roi = {}               # documented ROI disable; exits = signals/stoploss only
    stoploss = -0.05               # mandatory rail; config could override

    process_only_new_candles = True          # default True; explicit
    use_exit_signal = True                   # default True; explicit
    exit_profit_only = False                 # default False; explicit
    ignore_roi_if_entry_signal = False       # default False; explicit

    # ~4x the slow EMA period, mirroring the docs' ema100 -> 400 rule of thumb
    startup_candle_count = 100

    @property
    def protections(self):
        return [
            {"method": "CooldownPeriod",
             "stop_duration_candles": 2},
            {"method": "StoplossGuard",
             "lookback_period_candles": 24,
             "trade_limit": 2,
             "stop_duration_candles": 4,
             "required_profit": 0.0,         # default: only losing stoplosses count
             "only_per_pair": False},
            {"method": "MaxDrawdown",
             "calculation_mode": "equity",   # docs-recommended for new setups (default is "ratios")
             "lookback_period_candles": 168,
             "trade_limit": 5,
             "stop_duration_candles": 24,
             "max_allowed_drawdown": 0.2},
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"])  # golden cross
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])  # death cross
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
```

Claim map:
- `INTERFACE_VERSION = 3` `[V]` strategy-customization + interface.py; `timeframe = "1h"` `[V]` strategy-customization Timeframe; `can_short = False` spot semantics `[V]` interface.py + resolver + Can short (docs).
- `minimal_roi = {}` `[V]` Disabling minimal ROI (docs). `stoploss = -0.05` mandatory ratio attr `[V]` stoploss page + interface.py + config docs (mandatory, config override).
- Defaults triplet `[V]` resolver + template. `process_only_new_candles` `[V]` interface.py + template.
- `protections` as `@property` in strategy `[V]` plugins/; config-level protections removed in 2024.10 `[V]` via research/freqtrade-risk-rails.md (develop source).
- Protection parameter shapes `[V]` plugins/ examples; decided values (2 / 24-2-4 / 168-5-0.2-24) are the project's own rails, not docs defaults.
- `crossed_above`/`crossed_below` vectorised signal style `[V]` docs sample + Strategy001; `enter_long`/`exit_long` = 1 convention `[V]` Entry/Exit signal rules; `volume > 0` guard `[V]` docs note.
- `startup_candle_count = 100` — method `[V]` (docs startup-period section + recursive-analysis), the 100 number is my extrapolation of the docs' ema100→400 ratio → treat as a parameter to confirm with `freqtrade recursive-analysis`, not a docs-stated value.
- Order types omitted: `IStrategy` defaults apply (entry/exit/stoploss = limit, `stoploss_on_exchange = False`). `[V]` interface.py. Note Bybit spot has no exchange-side stoploss; dry-run is fully bot-simulated. `[V]` research/freqtrade-risk-rails.md §1.

## 8. Design implications for v0.1 (neutral — no decision made)

- The minimal strategy is genuinely minimal: 6–8 class attributes + 3 populate methods; everything else (order types, stake, whitelist, timeframe override) lives in config or IStrategy defaults.
- `minimal_roi = {}` (documented) vs the older `{"0": 100}` convention (not in current docs this scan) — pick the documented `{}` unless historical parity matters; both leave exit-signal + stoploss + protections as the only exit paths.
- Choosing 12/26 gives ground in the TA-Lib MACD convention + 2026 paper's TA-feature usage; 20/50 gives ground in the freqtrade-strategies example itself (Strategy001). 9/21 and 50/200 remain ungrounded community lore in this scan.
- Strategy001's exit asymmetry (50-vs-100 cross + HA filters rather than a 20/50 death cross) is a reminder that "entry pair, exit death cross" is a deliberate, defensible symmetry choice for v0.1, not simply what the reference strategies do.
- Crossed-signal semantics: signals computed on the closed 1h candle, trade executes next candle open; simultaneous enter+exit on the same candle = entry ignored (colliding-signal rule).
- Protections (decided rails) + mandatory stoploss coexist in one strategy `@property` + class attribute; config can override stoploss but not protections (config-level removed 2024.10).
- Every protection value is candle-denominated (`*_candles`), so changing candle TF would silently re-scale the rails — fine for 1h v0.1, worth a comment in the config/strategy docs.
- The v0.2 classifier can replace the two `populate_*_trend` method bodies (or, more surgically, the signal columns) without touching the rails skeleton: same `enter_long`/`exit_long` contract, same protections/stoploss, same config — that is exactly the seam the 2024/2026 papers support ("model phase is where contributions live").
- Startup candles: EMA26 needs ~100 1h candles of warm-up under the docs' ratio; run `freqtrade recursive-analysis` before dry-run to confirm 0% variance.
- Bybit spot: no exchange-side stop; dry-run stoploss is bot-managed — already established; nothing extra needed in the strategy file.

## Docs-version notes / contradictions found

- **ROI disable convention drift:** current stable docs say "To disable ROI completely, set it to an empty dictionary: `minimal_roi = {}`." The `{"0": 100}` "insanely high number" phrasing and convention did **not** appear in the current stable pages this scan (`[U]` legacy); source anchor for "big constant ≈ disabled": resolver fallback `{"0": 10.0}`. `[V]` per-item
- **`exit_profit_only` in examples ≠ default:** Strategy001 sets `exit_profit_only = True`; the interface/resolver/default docs value is `False`. Not a contradiction, but anyone eyeballing Strategy001 as a template should not copy that flag.
- **`INTERFACE_VERSION` stale comment in source:** `interface.py` carries a comment "Default to version 2" above `INTERFACE_VERSION: int = 3` (and the docs say default 3). Comments lag; attribute + docs agree on 3. `[V]`
- **`process_only_new_candles` default ambiguity risk:** interface.py has it as class default `True`; docs pages this scan do not state the default in prose — treat source as authoritative. `[V]`
- **MaxDrawdown modes:** stable docs now document `calculation_mode` (`"ratios"` default, `"equity"` recommended); older docs/older write-ups have no mode at all. Consistent with `research/freqtrade-risk-rails.md`. `[V]`
- Branch note: freqtrade-strategies default branch is `main` (a `develop` raw URL 404s). `[V]`
