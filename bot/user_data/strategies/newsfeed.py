"""News feed pipeline for the v0.2 Decide input (spec: .scratch/agent-v02-model/spec.md).

Pure, testable pieces: normalize upstream article payloads into the internal
article shape, then bucket into per-pair hourly features for the lookahead-safe
candle join. Upstream adapters (Alpha Vantage, CryptoPanic self-archive) pin
their field mappings separately.
"""
import pandas as pd
from pandas import DataFrame


def bucket_hourly(articles, freq="1h") -> DataFrame:
    if not articles:
        return DataFrame(columns=["news_sentiment_mean", "news_count"])
    rows = DataFrame(
        [
            {
                "pair": a["pair"],
                "hour": pd.to_datetime(a["ts"], utc=True),
                "sentiment": float(a["sentiment"]),
                "relevance": float(a["relevance"]),
            }
            for a in articles
        ]
    ).astype({"sentiment": "float64", "relevance": "float64"})
    rows["hour"] = rows["hour"].dt.floor(freq)
    grouped = rows.groupby(["pair", "hour"])
    features = grouped.apply(
        lambda g: pd.Series(
            {
                "news_sentiment_mean": (
                    (g["sentiment"] * g["relevance"]).sum() / g["relevance"].sum()
                    if g["relevance"].sum() > 0
                    else g["sentiment"].mean()
                ),
                "news_count": len(g),
            }
        ),
        include_groups=False,
    )
    features.index = features.index.set_names(["pair", "hour"])
    return features


def merge_article_features(candles: DataFrame, features: DataFrame, pair: str, freq="1h") -> DataFrame:
    """Join hourly news features onto candles, lookahead-safe.

    A bucket covering [hour, hour+freq) is fully known only at hour+freq, so a
    candle whose decision time is its close (date + freq) may use buckets with
    bucket_end <= close. Earlier candles get NaN (caller may fill).
    """
    candles = candles.copy()
    if features.empty:
        candles["news_sentiment_mean"] = pd.NA
        candles["news_count"] = pd.NA
        return candles

    pair_features = features.loc[[pair]] if pair in features.index.get_level_values("pair") else features.iloc[:0]
    available = DataFrame(
        {
            "available_at": pair_features.index.get_level_values("hour") + pd.Timedelta(freq),
            "news_sentiment_mean": pair_features["news_sentiment_mean"].to_numpy(),
            "news_count": pair_features["news_count"].to_numpy(),
        }
    ).sort_values("available_at")

    candles = candles.sort_values("date")
    candles["_close_time"] = candles["date"] + pd.Timedelta(freq)
    merged = pd.merge_asof(
        candles, available, left_on="_close_time", right_on="available_at", direction="backward"
    ).drop(columns=["_close_time", "available_at"])
    return merged
