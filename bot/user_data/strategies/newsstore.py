"""News archive + scheduling for the v0.2 Decide input (spec §3–§4).

The self-archive is the source of truth: raw API payloads are appended as JSONL,
features are derived deterministically from the archive so backtests and live
runs consume identical news. Adapters pin upstream field mappings; the Alpha
Vantage mapping follows the verified schema (research/fact-check-av-cryptopanic-freqai.md).
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from newsfeed import bucket_hourly
from pandas import DataFrame

AV_TIME_PUBLISHED_FMT = "%Y%m%dT%H%M%S"


def normalize_av_response(payload: dict, whitelist_coins: set[str]) -> list[dict]:
    articles: list[dict] = []
    for item in payload.get("feed", []):
        ts = pd.to_datetime(
            item["time_published"], format=AV_TIME_PUBLISHED_FMT, utc=True
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        for ticker_entry in item.get("ticker_sentiment", []):
            ticker = ticker_entry.get("ticker", "")
            if not ticker.startswith("CRYPTO:"):
                continue
            coin = ticker.removeprefix("CRYPTO:")
            if coin not in whitelist_coins:
                continue
            articles.append(
                {
                    "pair": f"{coin}/USDT",
                    "ts": ts,
                    "sentiment": float(ticker_entry["ticker_sentiment_score"]),
                    "relevance": float(ticker_entry["relevance_score"]),
                }
            )
    return articles


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")


def load_archived_payloads(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def should_fetch(now: datetime, fetch_log: list[datetime], max_per_day: int,
                 min_interval_hours: int) -> bool:
    window_start = now - timedelta(hours=24)
    fetched_in_window = sum(1 for t in fetch_log if t > window_start)
    if fetched_in_window >= max_per_day:
        return False
    if not fetch_log:
        return True
    spaced_enough = now - max(fetch_log) >= timedelta(hours=min_interval_hours)
    return spaced_enough


def latest_fetch_ts(fetch_log: list[datetime]) -> datetime:
    if not fetch_log:
        return datetime.now(UTC) - timedelta(days=3)
    return max(fetch_log)


def time_from_literal(ts: datetime) -> str:
    return ts.strftime("%Y%m%dT%H%M")


def load_archive_features(path: Path, whitelist_coins: set[str]) -> DataFrame:
    payload_batches = [r["payload"] for r in load_archived_payloads(path)]
    articles: list[dict] = []
    for payload in payload_batches:
        articles.extend(normalize_av_response(payload, whitelist_coins))
    return bucket_hourly(articles)


def load_archive_features_dir(directory: Path, whitelist_coins: set[str]) -> DataFrame:
    articles: list[dict] = []
    for path in sorted(Path(directory).glob("*.jsonl")):
        for record in load_archived_payloads(path):
            articles.extend(normalize_av_response(record["payload"], whitelist_coins))
    return bucket_hourly(articles)
