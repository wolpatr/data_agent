import pandas as pd
import pytest


def test_bucket_hourly_relevance_weights_sentiment_and_counts_articles():
    articles = [
        {"pair": "BTC/USDT", "ts": "2026-11-09T09:10:00Z", "sentiment": 0.6, "relevance": 1.0},
        {"pair": "BTC/USDT", "ts": "2026-11-09T09:50:00Z", "sentiment": -0.2, "relevance": 0.5},
        {"pair": "ETH/USDT", "ts": "2026-11-09T09:20:00Z", "sentiment": 0.4, "relevance": 1.0},
        {"pair": "BTC/USDT", "ts": "2026-11-09T10:15:00Z", "sentiment": 0.0, "relevance": 0.2},
    ]

    from newsfeed import bucket_hourly

    result = bucket_hourly(articles, freq="1h")

    assert set(result.index.get_level_values("pair")) == {"BTC/USDT", "ETH/USDT"}
    btc_rows = result.loc["BTC/USDT"]
    hour9 = btc_rows.loc[pd.Timestamp("2026-11-09T09:00:00Z")]
    hour10 = btc_rows.loc[pd.Timestamp("2026-11-09T10:00:00Z")]
    assert hour9["news_sentiment_mean"] == pytest.approx((0.6 * 1.0 + -0.2 * 0.5) / 1.5)
    assert hour9["news_count"] == 2
    assert hour10["news_sentiment_mean"] == pytest.approx(0.0)
    assert hour10["news_count"] == 1
    eth_hour9 = result.loc["ETH/USDT"].loc[pd.Timestamp("2026-11-09T09:00:00Z")]
    assert eth_hour9["news_count"] == 1


def make_candles(opens):
    dates = pd.date_range(
        start=pd.Timestamp("2026-11-09T08:00:00Z"), periods=len(opens), freq="1h"
    )
    return pd.DataFrame({"date": dates, "close": opens})


def test_merge_is_lookahead_safe_and_exact_at_bucket_end():
    articles = [
        {"pair": "BTC/USDT", "ts": "2026-11-09T09:50:00Z", "sentiment": -1.0, "relevance": 1.0},
        {"pair": "BTC/USDT", "ts": "2026-11-09T10:15:00Z", "sentiment": 0.5, "relevance": 1.0},
    ]
    from newsfeed import bucket_hourly, merge_article_features

    features = bucket_hourly(articles)
    candles = make_candles([100.0, 101.0, 102.0, 103.0, 104.0])

    merged = merge_article_features(candles, features, "BTC/USDT")

    candle08 = merged.loc[merged["date"] == pd.Timestamp("2026-11-09T08:00:00Z")].iloc[0]
    candle09 = merged.loc[merged["date"] == pd.Timestamp("2026-11-09T09:00:00Z")].iloc[0]
    candle10 = merged.loc[merged["date"] == pd.Timestamp("2026-11-09T10:00:00Z")].iloc[0]
    candle11 = merged.loc[merged["date"] == pd.Timestamp("2026-11-09T11:00:00Z")].iloc[0]
    assert pd.isna(candle08["news_count"])
    assert candle09["news_count"] == 1
    assert candle09["news_sentiment_mean"] == -1.0
    assert candle10["news_count"] == 1
    assert candle10["news_sentiment_mean"] == 0.5
    assert candle11["news_count"] == 1
    assert candle11["news_sentiment_mean"] == 0.5
