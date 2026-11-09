"""Feature and label engineering for the v0.2 Decide (spec: .scratch/agent-v02-model/spec.md).

Pure, testable building blocks consumed by the FreqAI-enabled strategy:
market features (three decided groups live in the strategy; this module holds
the reusable numerics) and the fee-aware binary label. No lookahead: labels
read only strictly-future candles and go NaN once the future is unavailable.
"""
import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

LABEL_COLUMN = "&label"


def market_features(dataframe: DataFrame) -> DataFrame:
    df = dataframe.copy()
    close = df["close"].astype("float64")

    df["f_ret_1"] = close.pct_change(1)
    df["f_ret_6"] = close.pct_change(6)
    df["f_ret_24"] = close.pct_change(24)
    df["f_rsi14"] = ta.RSI(close, timeperiod=14)
    atr = ta.ATR(df, timeperiod=14)
    df["f_atr_close"] = atr / close
    vol_mean = df["volume"].rolling(24).mean()
    vol_std = df["volume"].rolling(24).std(ddof=0)
    df["f_vol_zscore"] = (df["volume"] - vol_mean) / vol_std.replace(0, np.nan)
    ema_fast = ta.EMA(close, timeperiod=12)
    ema_slow = ta.EMA(close, timeperiod=26)
    df["f_ema12_26_dist"] = (ema_fast - ema_slow) / close
    return df


def fee_aware_labels(dataframe: DataFrame, horizon: int = 6, threshold: float = 0.003) -> DataFrame:
    df = dataframe.copy()
    close = df["close"].astype("float64")
    future_return = close.shift(-horizon) / close - 1
    df[LABEL_COLUMN] = (future_return > threshold).astype("float64")
    df.loc[future_return.isna(), LABEL_COLUMN] = np.nan
    return df


def fee_aware_label_classes(dataframe: DataFrame, horizon: int = 6,
                            threshold: float = 0.003) -> pd.Series:
    """String-class view of the fee-aware label for FreqAI classifiers."""
    df = fee_aware_labels(dataframe, horizon=horizon, threshold=threshold)
    classes = df[LABEL_COLUMN].map(
        lambda v: pd.NA if pd.isna(v) else ("up" if v == 1.0 else "flat")
    )
    return classes
