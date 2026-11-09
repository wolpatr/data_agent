# Manual interventions log

One line per manual action (what/when/why/bot state). Allowed: pause entries, force-exit, full stop, manual locks. Forbidden: force-entering trades, editing the dry-run DB.

| Date | Action | Command | Reason | Bot state |
|---|---|---|---|---|
| 2026-11-09 ~18:52Z | Re-arm (started trading) | `POST /api/v1/start` | first-run smoke complete; paper-run gate clock starts | stopped → running |
