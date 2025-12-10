# AGENTS – One‑off / Sync Scripts

This file applies to everything under `scripts/sync/`.

## Purpose

- Hold **one‑off** or **migration** helpers that mutate quiz data via the
  editor API.
- These scripts are kept for reproducibility and auditability, but are not
  expected to be run frequently.

## Conventions

- Treat scripts here as **idempotent** where possible (safe to re‑run against
  the same quiz).
- Keep behavior narrowly scoped and well‑documented in the module docstring.
- When a script has served its purpose, prefer leaving it here rather than
  deleting it, so future agents can see how existing quizzes were created.
- New migration helpers should also live in this folder, named clearly, e.g.:
  - `sync_teamA_session2_quiz.py`

