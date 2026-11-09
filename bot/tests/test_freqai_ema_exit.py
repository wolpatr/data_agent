import pandas as pd
from FreqaiEmaExit import FreqaiEmaExit

CONFIG = {
    "strategy": "FreqaiEmaExit",
    "stake_currency": "USDT",
    "dry_run": True,
    "v02_feature_groups": {"market": True, "news": True, "macro": False},
    "freqai": {
        "enabled": True,
        "identifier": "v02-ema-exit",
        "train_period_days": 30,
        "backtest_period_days": 0.042,
        "feature_parameters": {"include_timeframes": ["1h"], "include_corr_pairlist": ["BTC/USDT"],
                               "include_shifted_candles": 2, "label_period_candles": 6},
        "data_split_parameters": {"test_size": 0.25},
        "model_training_parameters": {},
    },
}


def make_strategy(**overrides):
    config = {**CONFIG, **overrides}
    return FreqaiEmaExit(config)


def make_frame(n, closes, volumes=None):
    dates = pd.date_range(start="2026-01-01", periods=n, freq="1h", tz="UTC")
    volumes = volumes if volumes is not None else [100.0] * n
    return pd.DataFrame(
        {"date": dates, "open": closes, "high": closes, "low": closes, "close": closes, "volume": volumes}
    )


def test_strategy_rails_contract_matches_v01():
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


def test_feature_groups_add_percent_prefixed_columns():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 21)]
    df = make_frame(len(closes), closes)
    strategy = make_strategy()

    out = strategy.feature_engineering_standard(df.copy(), {"pair": "BTC/USDT"})

    for col in ("%-f_ret_1", "%-f_rsi14", "%-f_vol_zscore", "%-f_ema12_26_dist"):
        assert col in out.columns


def test_feature_group_toggle_off_removes_market_columns():
    closes = [100.0] * 40
    df = make_frame(len(closes), closes)
    strategy = make_strategy(v02_feature_groups={"market": False, "news": False, "macro": False})

    out = strategy.feature_engineering_standard(df.copy(), {"pair": "BTC/USDT"})

    assert "%-f_rsi14" not in out.columns


def test_set_freqai_targets_emits_string_up_flat_with_nan_tail():
    closes = [100.0] * 40 + [100 + i * 2 for i in range(1, 41)]
    df = make_frame(len(closes), closes)
    strategy = make_strategy()

    out = strategy.set_freqai_targets(df.copy(), {"pair": "BTC/USDT"})

    target = out["&-up_flat"]
    assert target.iloc[-6:].isna().all()
    assert target.iloc[34] == "up"
    assert target.iloc[33] == "flat"
    assert set(target.dropna().unique()) <= {"up", "flat"}


def make_pred_frame():
    closes = [100.0] * 40 + [100 - i * 2 for i in range(1, 21)]
    df = make_frame(len(closes), closes)
    df["do_predict"] = 1
    df["&-up_flat"] = "up"
    df["up"] = 0.9
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    df.loc[len(df) - 1, "&-up_flat"] = "flat"
    df.loc[len(df) - 1, "up"] = 0.2
    return df


def test_entry_gated_by_do_predict_class_and_probability():
    strategy = make_strategy()
    df = make_pred_frame()

    out = strategy.populate_entry_trend(df, {"pair": "BTC/USDT"})

    signals = out["enter_long"].fillna(0)
    expected_idx = list(range(len(out) - 1))
    assert list(signals.index[signals == 1]) == expected_idx


def test_exit_fires_on_death_cross_only():
    closes = [100.0] * 40 + [100 - i * 2 for i in range(1, 21)]
    df = make_frame(len(closes), closes)
    strategy = make_strategy()

    from featurelab import market_features

    df = market_features(df)
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()

    out = strategy.populate_exit_trend(df, {"pair": "BTC/USDT"})

    signals = out["exit_long"].fillna(0)
    assert signals.value_counts().get(1, 0) >= 1
    first_signal = signals.index[signals == 1][0]
    expected = signals.index[signals == 1]
    assert list(expected) == list(range(first_signal, len(df))) or len(expected) <= 3


def test_bot_loop_start_is_safe_without_api_key():
    strategy = make_strategy()
    import datetime as dt

    strategy.bot_loop_start(dt.datetime.now(dt.UTC))


def test_entry_is_gated_off_when_probability_column_missing():
    strategy = make_strategy()
    df = make_pred_frame().drop(columns=["up"])

    out = strategy.populate_entry_trend(df, {"pair": "BTC/USDT"})

    assert (out["enter_long"].fillna(0) == 0).all()
