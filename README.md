# data_agent

Autonomous crypto trading agent (v0.1: freqtrade dry-run, BTC/USDT Bybit spot, 1h, EMA-crossover baseline).

- Mission: `MISSION.md` · Decisions map: `.scratch/agent-v01-spec/map.md` · Build spec: `.scratch/agent-v01-spec/spec.md`
- Runbook: `docs/playbook.md` · Interventions log: `docs/interventions.md`
- Dependencies are managed with **uv**: `uv sync` to create `.venv`, then run everything as `uv run <command>` (e.g. `uv run pytest bot/tests -q`, `uv run freqtrade trade -c bot/config.json -c bot/config-private.json`).
