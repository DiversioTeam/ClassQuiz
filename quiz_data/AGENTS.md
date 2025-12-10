# AGENTS – Quiz Markdown

This file applies to everything under `quiz_data/`.

## Purpose

- Keep all quiz Markdown in a predictable place.
- Make it easy for multiple teams to author and review quizzes that can be
  synced into ClassQuiz via the editor API.

## Layout

- Each quiz (or closely related quiz family) gets its own subfolder:
  - `quiz_data/<owner_or_team>_<topic>_<session>/`
  - Example: `quiz_data/monty_python_data_model_session1/`
- Within each folder, prefer consistent filenames:
  - `sessionN_quiz.md`
  - `sessionN_quiz_answer_key.md`
  - Optional extras like `sessionN_survey.md`, `sessionN_survey_answer_key.md`.

## Authoring workflow

- Write questions in Markdown following the conventions from the root
  `AGENTS.md` (§10 “Authoring world‑class technical quizzes”).
- Before syncing to the DB, run:

  ```bash
  python scripts/validate_quiz_markdown.py quiz_data/.../sessionN_quiz.md
  ```

  and address warnings where reasonable.

- Treat Markdown as the **canonical source of truth**; update quizzes in the
  database via the editor API and helper scripts rather than editing DB rows
  directly.

