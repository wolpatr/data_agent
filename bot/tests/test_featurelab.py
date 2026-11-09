import pandas as pd
import pytest


def make_frame(n, closes, volumes=None):
    dates = pd.date_range(start="2026-01-01", periods=n, freq="1h", tz="UTC")
    volumes = volumes if volumes is not None else [100.0] * n
    return pd.DataFrame(
        {"date": dates, "open": closes, "high": closes, "low": closes, "close": closes, "volume": volumes}
    )


def test_market_features_add_the_decided_columns():
    closes = [100.0] * 30 + [100 + i for i in range(1, 11)]
    df = make_frame(len(closes), closes)

    from featurelab import market_features

    result = market_features(df)

    for col in (
        "f_ret_1",
        "f_ret_6",
        "f_ret_24",
        "f_rsi14",
        "f_atr_close",
        "f_vol_zscore",
        "f_ema12_26_dist",
    ):
        assert col in result.columns
    row = result.iloc[39]
    assert row["f_ret_1"] == pytest.approx(closes[39] / closes[38] - 1)
    assert row["f_ret_6"] == pytest.approx(closes[39] / closes[33] - 1)
    assert row["f_ret_24"] == pytest.approx(closes[39] / closes[15] - 1)


def test_market_features_rsi_matches_wilder_definition_bounds_and_direction():
    rising = make_frame(40, [100 + i for i in range(40)])
    falling = make_frame(40, [100 - i for i in range(40)])

    from featurelab import market_features

    rising_feats = market_features(rising)
    falling_feats = market_features(falling)

    def wilder_rsi(closes):
        s = pd.Series(closes, dtype="float64")
        delta = s.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        rs = gain / loss
        return 100 - 100 / (1 + rs)

    last = rising_feats["f_rsi14"].iloc[-1]
    assert last == pytest.approx(wilder_rsi(rising["close"]).iloc[-1].item())
    assert last > 70
    assert falling_feats["f_rsi14"].iloc[-1] < 30


def test_ema_distance_matches_pandas_ewm_reference():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 21)]
    df = make_frame(len(closes), closes)

    from featurelab import market_features

    result = market_features(df)

    fast = df["close"].ewm(span=12, adjust=False).mean()
    slow = df["close"].ewm(span=26, adjust=False).mean()
    expected = (fast - slow) / df["close"]
    pd.testing.assert_series_equal(
        result["f_ema12_26_dist"].iloc[25:], expected.iloc[25:], check_names=False
    )


def test_fee_aware_label_is_future_only_and_threshold_exact():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 41)]
    df = make_frame(len(closes), closes)

    from featurelab import fee_aware_labels

    labeled = fee_aware_labels(df, horizon=6, threshold=0.003)

    label = labeled["&label"]
    assert label.iloc[-6:].isna().all()
    assert (label.iloc[:34] == 0).all()
    assert label.iloc[34] == 1
    assert (closes[40] / closes[34]) - 1 == pytest.approx(0.02)
    assert label.iloc[33] == 0
    assert (closes[39] / closes[33]) - 1 == 0