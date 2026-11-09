import json
from pathlib import Path

from freqtrade.configuration.config_validation import validate_config_schema

BOT_DIR = Path(__file__).resolve().parents[1]


def load_public_config():
    return json.loads((BOT_DIR / "config.json").read_text(encoding="utf-8"))


def test_public_config_validates_and_carries_the_decided_keys():
    config = load_public_config()

    validate_config_schema(config)

    assert config["dry_run"] is True
    assert config["dry_run_wallet"] == 1000
    assert config["max_open_trades"] == 1
    assert config["stake_currency"] == "USDT"
    assert config["stake_amount"] == 250
    assert config["db_url"] == "sqlite:///bot/tradesv3.dryrun.sqlite"
    assert config["cancel_open_orders_on_exit"] is True
    assert config["dataformat_ohlcv"] == "feather"
    assert config["trading_mode"] == "spot"
    assert config["exchange"]["name"] == "bybit"
    assert config["exchange"]["pair_whitelist"] == ["BTC/USDT"]
    assert config["pairlists"] == [{"method": "StaticPairList"}]
    assert config["order_types"]["entry"] == "market"
    assert config["order_types"]["exit"] == "market"
    assert config["entry_pricing"]["price_side"] == "other"
    assert config["exit_pricing"]["price_side"] == "other"
    assert config["strategy"] == "EmaCrossBaseline"
    assert config["user_data_dir"] == "bot/user_data"


def test_public_config_leaves_rails_and_state_to_their_owners():
    config = load_public_config()

    assert "api_server" not in config
    assert "timeframe" not in config
    assert "stoploss" not in config
    assert "initial_state" not in config
    assert "protections" not in config


def test_private_overlay_template_merges_and_validates():
    template = json.loads((BOT_DIR / "config-private.example.json").read_text(encoding="utf-8"))

    merged = {**load_public_config(), **template}
    validate_config_schema(merged)

    api = template["api_server"]
    assert api["enabled"] is True
    assert api["listen_ip_address"] == "127.0.0.1"
    assert api["username"] == "freqtrade"
    assert api["password"].startswith("CHANGE_ME")


def test_real_private_config_is_ignored_by_git():
    gitignore = (Path(__file__).resolve().parents[2] / ".gitignore").read_text(encoding="utf-8")
    assert "bot/config-private.json" in gitignore
    assert "bot/tradesv3.dryrun.sqlite" in gitignore
    assert "bot/user_data/data/" in gitignore
