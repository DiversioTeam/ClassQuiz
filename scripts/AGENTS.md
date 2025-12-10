# AGENTS – Helper Scripts

This file applies to everything under `scripts/` (including nested folders).

## Purpose

- Keep all CLI‑style helper scripts in a single place.
- Make it easy for instructors and engineers to:
  - sync quiz content via the editor API,
  - lint quiz Markdown,
  - simulate players or export results from Redis.

## Layout

- Long‑lived utilities (used across sessions) live **directly** in `scripts/`:
  - `scripts/validate_quiz_markdown.py`
  - `scripts/simulate_players.py`
  - `scripts/export_results_from_redis.py`
- One‑off and migration scripts live under `scripts/sync/`:
  - `scripts/sync/sync_session1_quiz_append_new_questions.py`
  - `scripts/sync/sync_session1_tricky_timers.py`
  - `scripts/sync/sync_connection_test_quiz.py`

## Conventions for new scripts

- Prefer small, single‑purpose CLIs using `argparse`.
- Assume they are run from the **repo root**.
- If a script calls external tools, prefer:
  - `docker compose ...` for talking to running services,
  - `httpx` for HTTP calls (consistent with existing sync scripts).
- Avoid importing application code from `classquiz/` unless necessary; keep
  helpers loosely coupled so they do not break on upstream upgrades.
- Do **not** add new `.py` files at the repo root – put them in `scripts/`
  (or `scripts/sync/` for one‑offs) instead.

