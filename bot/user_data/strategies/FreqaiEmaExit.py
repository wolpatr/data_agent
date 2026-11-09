"""v0.2 Decide: FreqAI classifier entries + v0.1 exits and rails (spec §5, §7).

Entries gate on the classifier's probability of the fee-aware 'up' class;
exits stay the v0.1 EMA death-cross; rails are identical to EmaCrossBaseline
so behavior stays comparable across the gate boundary. News features come
from the self-archive (the source of truth for backtests and live alike).
"""
import datetime as dt
import json
import os
from pathlib import Path

import pandas as pd
import talib.abstract as ta
from featurelab import fee_aware_label_classes, market_features
from freqtrade.strategy import IStrategy
from newsfeed import merge_article_features
from newsstore import (
    load_archive_features_dir,
    should_fetch,
    time_from_literal,
)
from pandas import DataFrame
from technical.qtpylib import crossed_below


class FreqaiEmaExit(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = False

    minimal_roi = {}
    stoploss = -0.05

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    startup_candle_count = 100

    entry_proba = 0.55

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 2,
                "stop_duration_candles": 4,
                "required_profit": 0.0,
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "calculation_mode": "equity",
                "lookback_period_candles": 168,
                "trade_limit": 5,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.2,
            },
        ]

    def _news_dir(self) -> Path:
        return Path(self.config.get("user_data_dir", "bot/user_data")) / "news" / "av"

    def _whitelist_coins(self) -> set[str]:
        return {p.split("/")[0] for p in self.config["exchange"]["pair_whitelist"]}

    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int,
                                       metadata: dict, **kwargs) -> DataFrame:
        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, metadata: dict,
                                         **kwargs) -> DataFrame:
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        groups = self.config.get("v02_feature_groups", {})
        if groups.get("market", True):
            features = market_features(dataframe)
            for col in ("f_ret_1", "f_ret_6", "f_ret_24", "f_rsi14", "f_atr_close",
                        "f_vol_zscore", "f_ema12_26_dist"):
                dataframe[f"%-{col}"] = features[col]

        if groups.get("news", True):
            news_dir = self._news_dir()
            if news_dir.exists():
                features = load_archive_features_dir(news_dir, self._whitelist_coins())
                if not features.empty:
                    merged = merge_article_features(dataframe, features, metadata["pair"],
                                                    self.timeframe)
                    dataframe["%-news_sentiment_mean"] = merged["news_sentiment_mean"].to_numpy()
                    dataframe["%-news_count"] = merged["news_count"].to_numpy()

        if groups.get("macro", False):
            macro_dir = Path(self.config.get("user_data_dir", "bot/user_data")) / "macro"
            if macro_dir.exists():
                for csv in macro_dir.glob("*.csv"):
                    series = pd.read_csv(csv, index_col=0, parse_dates=True)[0]
                    key = csv.stem
                    dataframe[f"%-macro_{key}"] = series.reindex(
                        dataframe["date"], method="ffill"
                    ).to_numpy()
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        horizon = self.config["freqai"]["feature_parameters"]["label_period_candles"]
        classes = fee_aware_label_classes(dataframe, horizon=horizon, threshold=0.003)
        dataframe["&-up_flat"] = classes
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = self.freqai.start(dataframe, metadata, self)
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe["enter_tag"] = None
        conditions = [
            dataframe["do_predict"] == 1,
            dataframe["&-up_flat"] == "up",
            dataframe["volume"] > 0,
        ]
        if "up" in dataframe.columns:
            conditions.append(dataframe["up"] > self.entry_proba)
            mask = conditions[0]
            for condition in conditions[1:]:
                mask = mask & condition
            dataframe.loc[mask, ["enter_long", "enter_tag"]] = (1, "freqai_up")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
             & (dataframe["volume"] > 0)),
            ["exit_long", "exit_tag"],
        ] = (1, "ema_exit")
        return dataframe

    def bot_loop_start(self, current_time: dt.datetime, **kwargs) -> None:
        """Refresh the news self-archive within the AV daily budget (best effort)."""
        api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
        if not api_key:
            return
        import urllib.request

        news_dir = self._news_dir()
        log_path = news_dir / "fetch_log.json"
        history = []
        if log_path.exists():
            history = json.loads(log_path.read_text(encoding="utf-8"))
        stamps = [
            dt.datetime.fromisoformat(s) if dt.datetime.fromisoformat(s).tzinfo else
            dt.datetime.fromisoformat(s).replace(tzinfo=dt.UTC)
            for s in history
        ]
        if news_dir.exists() and not should_fetch(
            current_time, stamps, max_per_day=25, min_interval_hours=1
        ):
            return
        coins = sorted(self._whitelist_coins())
        tickers = ",".join(f"CRYPTO:{c}" for c in coins)
        url = (
            "https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
            f"&tickers={tickers}&limit=50"
            f"&time_from={time_from_literal(min(stamps) if stamps else current_time - dt.timedelta(days=3))}"
            f"&apikey={api_key}"
        )
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError):
            return
        news_dir.mkdir(parents=True, exist_ok=True)
        stamp = current_time.strftime("%Y-%m-%d")
        day_file = news_dir / f"{stamp}.jsonl"
        with day_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"fetch_ts": current_time.isoformat(), "payload": payload},
                                separators=(",", ":")) + "\n")
        history.append(current_time.isoformat())
        log_path.write_text(json.dumps(history[-100:]), encoding="utf-8")
