# Weekly review — week 1 (gate week 1)

Period: 2026-11-09 → ____ · Downtime gaps this week: (none / list)

## Closed trades (query output)

```
(paste `SELECT id, pair, open_date, close_date, close_profit, close_profit_abs, exit_reason FROM trades WHERE is_open=0 ORDER BY close_date;`)
```

## Rail firings (stoploss-family exits + named locks)

```
(paste stoploss-exit query output and any lock rows that are not `Auto lock`)
```

## Errors / incidents

```
(paste ERROR lines from bot.log, if any)
```

## Anomalies & notes

-
