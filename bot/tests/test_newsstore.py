import json
from datetime import UTC
from pathlib import Path

import pytest

AV_SAMPLE = {
    "feed": [
        {
            "title": "Bitcoin fund inflows accelerate",
            "url": "https://example.com/a1",
            "time_published": "20261109T091500",
            "overall_sentiment_score": 0.25,
            "ticker_sentiment": [
                {"ticker": "CRYPTO:BTC", "relevance_score": "0.8", "ticker_sentiment_score": "0.6"},
                {"ticker": "FOREX:USD", "relevance_score": "0.2", "ticker_sentiment_score": "-0.1"},
            ],
        },
        {
            "title": "Macro rates steer risk assets",
            "url": "https://example.com/a2",
            "time_published": "20261109T094500",
            "overall_sentiment_score": -0.4,
            "ticker_sentiment": [{"ticker": "FOREX:USD", "relevance_score": "0.9", "ticker_sentiment_score": "-0.4"}],
        },
        {
            "title": "Ethereum upgrade lands",
            "url": "https://example.com/a3",
            "time_published": "20261109T102000",
            "overall_sentiment_score": 0.7,
            "ticker_sentiment": [{"ticker": "CRYPTO:ETH", "relevance_score": "1.0", "ticker_sentiment_score": "0.8"}],
        },
    ]
}


def test_normalize_av_response_maps_whitelist_tickers_to_pairs():
    from newsstore import normalize_av_response

    articles = normalize_av_response(AV_SAMPLE, whitelist_coins={"BTC", "ETH"})

    btc = [a for a in articles if a["pair"] == "BTC/USDT"]
    eth = [a for a in articles if a["pair"] == "ETH/USDT"]
    assert len(articles) == 2
    assert len(btc) == 1 and len(eth) == 1
    assert btc[0]["ts"] == "2026-11-09T09:15:00Z"
    assert btc[0]["sentiment"] == pytest.approx(0.6)
    assert btc[0]["relevance"] == pytest.approx(0.8)
    assert eth[0]["ts"] == "2026-11-09T10:20:00Z"
    assert eth[0]["sentiment"] == pytest.approx(0.8)
    assert eth[0]["relevance"] == pytest.approx(1.0)


def test_archive_roundtrip_appends_and_reads(tmp_path):
    from newsstore import append_jsonl, load_archived_payloads

    path = Path(tmp_path) / "av" / "2026-11-09.jsonl"
    append_jsonl(path, {"fetch_ts": "t1", "payload": {"a": 1}})
    append_jsonl(path, {"fetch_ts": "t2", "payload": {"b": 2}})

    records = load_archived_payloads(path)
    assert [r["fetch_ts"] for r in records] == ["t1", "t2"]
    assert records[0]["payload"]["a"] == 1


def test_quota_scheduler_spreads_fetches_within_budget():
    from datetime import datetime, timedelta

    from newsstore import should_fetch

    now = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)
    fetch_log = [now - timedelta(hours=h) for h in (1, 2, 3)]
    assert should_fetch(now, fetch_log, max_per_day=25, min_interval_hours=1) is True
    fetch_log_recent = [now - timedelta(minutes=20)]
    assert should_fetch(now, fetch_log_recent, max_per_day=25, min_interval_hours=1) is False
    saturating = [now - timedelta(hours=1) for _ in range(25)]
    assert should_fetch(now, saturating, max_per_day=25, min_interval_hours=1) is False


def test_newsstore_build_pair_features_from_archive(tmp_path):
    from newsstore import append_jsonl, load_archive_features, load_archived_payloads

    path = Path(tmp_path) / "av" / "2026-11-09.jsonl"
    append_jsonl(path, {"fetch_ts": "t1", "payload": AV_SAMPLE})

    features = load_archive_features(path, whitelist_coins={"BTC", "ETH"})

    set_rows = features.loc["BTC/USDT"]
    assert set_rows.loc["2026-11-09T09:00:00Z"]["news_count"] == 1
    eth = features.loc["ETH/USDT"]
    assert eth.loc["2026-11-09T10:00:00Z"]["news_sentiment_mean"] == pytest.approx(0.8)
    assert json.dumps([r["payload"] for r in load_archived_payloads(path)])


def test_load_archive_features_dir_merges_all_daily_files(tmp_path):
    from newsstore import append_jsonl, load_archive_features_dir

    av_dir = Path(tmp_path) / "av"
    append_jsonl(av_dir / "2026-11-08.jsonl", {"fetch_ts": "t0", "payload": AV_SAMPLE})
    day2 = {
        "feed": [
            {
                "title": "Follow-up",
                "url": "u",
                "time_published": "20261110T093000",
                "overall_sentiment_score": 0.1,
                "ticker_sentiment": [
                    {"ticker": "CRYPTO:BTC", "relevance_score": "1.0", "ticker_sentiment_score": "0.3"}
                ],
            }
        ]
    }
    append_jsonl(av_dir / "2026-11-10.jsonl", {"fetch_ts": "t1", "payload": day2})

    features = load_archive_features_dir(av_dir, {"BTC", "ETH"})

    btc = features.loc["BTC/USDT"]
    assert btc.loc["2026-11-09T09:00:00Z"]["news_count"] == 1
    assert btc.loc["2026-11-10T09:00:00Z"]["news_count"] == 1
