# AGENTS – Monty / Python Data Model Session 1

This file applies to everything under
`quiz_data/monty_python_data_model_session1/`.

## Scope

- Tracks the **Python Data Model – Session 1 Quiz** used in internal training.
- Markdown here is the canonical representation of that quiz:
  - `session1_quiz.md`
  - `session1_quiz_answer_key.md`

## Expectations

- Keep this quiz aligned with the `session_1.html` slide deck:
  - Topics: identity vs equality, mutability & aliasing, shared rows, class vs
    instance attributes and `__dict__`, basic GC intuition, shallow copies,
    nested mutability.
  - Avoid drifting into later topics without explicitly updating the deck.
- When changing questions or answers:
  - Update both Markdown files.
  - Use the editor API (and scripts in `scripts/sync/`) to reflect the changes
    into the live quiz rather than editing the database by hand.
- Before a teaching session, you can sanity‑check formatting with:

  ```bash
  python scripts/validate_quiz_markdown.py quiz_data/monty_python_data_model_session1/session1_quiz.md
  ```

