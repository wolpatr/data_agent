import pandas as pd
from EmaCrossBaseline import EmaCrossBaseline

CONFIG = {"strategy": "EmaCrossBaseline", "stake_currency": "USDT", "dry_run": True}


def build_candles(closes, volumes=None, start="2026-01-01"):
    n = len(closes)
    if volumes is None:
        volumes = [100.0] * n
    dates = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    frame = pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": volumes,
        }
    )
    return frame


def make_strategy():
    return EmaCrossBaseline(CONFIG)


def test_indicators_match_pandas_ewm_reference():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 21)]
    df = build_candles(closes)

    result = make_strategy().populate_indicators(df.copy(), {"pair": "BTC/USDT"})

    expected_fast = df["close"].ewm(span=12, adjust=False).mean()
    expected_slow = df["close"].ewm(span=26, adjust=False).mean()
    assert result["ema_fast"].iloc[:11].isna().all()
    assert result["ema_slow"].iloc[:25].isna().all()
    pd.testing.assert_series_equal(result["ema_fast"].iloc[11:], expected_fast.iloc[11:], check_names=False)
    pd.testing.assert_series_equal(result["ema_slow"].iloc[25:], expected_slow.iloc[25:], check_names=False)


def test_entry_signal_exactly_on_golden_cross_candle():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 21)]
    df = build_candles(closes)
    strategy = make_strategy()
    df = strategy.populate_indicators(df, {"pair": "BTC/USDT"})

    result = strategy.populate_entry_trend(df, {"pair": "BTC/USDT"})

    signals = result["enter_long"].fillna(0)
    assert list(signals.index[signals == 1]) == [40]
    assert (signals == 0).sum() == len(signals) - 1


def test_exit_signal_exactly_on_death_cross_candle():
    closes = [100.0] * 40 + [100 - i * 2 for i in range(1, 21)]
    df = build_candles(closes)
    strategy = make_strategy()
    df = strategy.populate_indicators(df, {"pair": "BTC/USDT"})

    result = strategy.populate_exit_trend(df, {"pair": "BTC/USDT"})

    signals = result["exit_long"].fillna(0)
    assert list(signals.index[signals == 1]) == [40]
    assert (signals == 0).sum() == len(signals) - 1


def test_no_cross_produces_no_signals_and_zero_volume_blocks_entry():
    strategy = make_strategy()

    rising = build_candles([100.0] + [100 + i for i in range(1, 80)])
    rising = strategy.populate_indicators(rising, {"pair": "BTC/USDT"})
    assert (strategy.populate_entry_trend(rising, {"pair": "BTC/USDT"})["enter_long"].fillna(0) == 0).all()
    assert (strategy.populate_exit_trend(rising, {"pair": "BTC/USDT"})["exit_long"].fillna(0) == 0).all()

    flat = build_candles([100.0] * 80)
    flat = strategy.populate_indicators(flat, {"pair": "BTC/USDT"})
    assert (strategy.populate_entry_trend(flat, {"pair": "BTC/USDT"})["enter_long"].fillna(0) == 0).all()

    dry = build_candles([100.0] * 40 + [100 + i * 2 for i in range(1, 10)], volumes=[0.0] * 49)
    dry = strategy.populate_indicators(dry, {"pair": "BTC/USDT"})
    assert (strategy.populate_entry_trend(dry, {"pair": "BTC/USDT"})["enter_long"].fillna(0) == 0).all()


def test_static_rails_contract():
    strategy = make_strategy()
    assert strategy.stoploss == -0.05
    assert strategy.minimal_roi == {}
    assert strategy.can_short is False
    assert strategy.timeframe == "1h"
    assert strategy.INTERFACE_VERSION == 3
    assert strategy.process_only_new_candles is True
    assert strategy.use_exit_signal is True
    assert strategy.exit_profit_only is False
    assert strategy.ignore_roi_if_entry_signal is False
    assert strategy.startup_candle_count >= 26


def test_protections_are_the_three_decided_rails():
    strategy = make_strategy()
    expected = [
        {"method": "CooldownPeriod", "stop_duration_candles": 2},
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
    assert strategy.protections == expected
