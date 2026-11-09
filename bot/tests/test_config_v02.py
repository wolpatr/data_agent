import json
from pathlib import Path

import pytest
from freqtrade.configuration.config_validation import validate_config_schema

BOT_DIR = Path(__file__).resolve().parents[1]


def load_v02_config():
    return json.loads((BOT_DIR / "config-v02.json").read_text(encoding="utf-8"))


def test_config_v02_schema_valid_with_decided_keys():
    config = load_v02_config()

    validate_config_schema(config)

    assert config["max_open_trades"] == 3
    assert config["dry_run"] is True
    assert config["db_url"] == "sqlite:///bot/tradesv3.dryrun.v02.sqlite"
    assert config["freqaimodel"] == "LightGBMClassifier"
    assert config["exchange"]["pair_whitelist"] == [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "LINK/USDT", "DOGE/USDT",
    ]
    freqai = config["freqai"]
    assert freqai["enabled"] is True
    assert freqai["identifier"] == "v02-ema-exit"
    assert freqai["train_period_days"] == 30
    assert freqai["backtest_period_days"] == pytest.approx(0.042)
    assert freqai["live_retrain_hours"] == 24
    assert freqai["expiration_hours"] == 48
    fp = freqai["feature_parameters"]
    assert fp["include_timeframes"] == ["1h"]
    assert fp["include_corr_pairlist"] == ["BTC/USDT"]
    assert fp["label_period_candles"] == 6
    assert freqai["data_split_parameters"]["test_size"] == 0.25
    assert config["v02_feature_groups"] == {"market": True, "news": True, "macro": False}
    assert config["order_types"]["entry"] == "market"
    assert config["cancel_open_orders_on_exit"] is True


def test_config_v02_leaves_rails_and_state_to_their_owners():
    config = load_v02_config()

    assert "api_server" not in config
    assert "timeframe" not in config
    assert "stoploss" not in config
    assert "initial_state" not in config
    assert "protections" not in config
