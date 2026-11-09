"""v0.1 trigger baseline for the data-agent: EMA 12/26 crossover.

Golden-cross entry, death-cross exit, long-only spot, 1h closed-candle
signals. Carries the decided risk rails in-file (spec: .scratch/agent-v01-spec/spec.md;
decisions: .scratch/agent-v01-spec/map.md).
"""
import talib.abstract as ta
from freqtrade.strategy import IStrategy
from pandas import DataFrame
from technical.qtpylib import crossed_above, crossed_below


class EmaCrossBaseline(IStrategy):
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

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (crossed_above(dataframe["ema_fast"], dataframe["ema_slow"]) & (dataframe["volume"] > 0)),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (crossed_below(dataframe["ema_fast"], dataframe["ema_slow"]) & (dataframe["volume"] > 0)),
            "exit_long",
        ] = 1
        return dataframe
