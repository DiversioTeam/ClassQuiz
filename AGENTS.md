# AGENTS – ClassQuiz Session Experiments

This file documents what has been done in this fork of **ClassQuiz**, the quirks we hit, and how to run future quiz sessions in the same style. It also serves as guidance for future agents working in this repo.

---

## 1. High‑level goals

- Run **Python training sessions** using ClassQuiz as the quiz engine.
- Keep everything reproducible via **Docker** on macOS (or Linux/Windows with Docker Desktop).
- Generate quizzes **on the fly** from teaching material and archive them as Markdown for discussion.
- Keep a small set of **test accounts** for demos and internal experiments.

All work described below assumes you have cloned this repo (or the Diversio fork)
into some local directory and are running Docker Desktop.

Example:

```bash
git clone git@github.com:DiversioTeam/ClassQuiz.git
cd ClassQuiz
```

---

## 2. Stack and configuration

### Backend / services

- Core app: upstream **ClassQuiz** FastAPI backend + SvelteKit frontend (monorepo).
- Python backend runs in Docker from the existing `Dockerfile`:
  - Base image: `python:3.13-slim`
  - Dependencies pulled from `Pipfile.lock`
  - Extra packages installed in the image: `libpq5`, `libpq-dev`, `libmagic1`, etc.
- Supporting services (from `docker-compose.yml`):
  - `db` – Postgres 14 (alpine)
  - `redis` – Redis
  - `meilisearch` – Search index
  - `api` – FastAPI backend (`classquiz-api`)
  - `worker` – ARQ worker for background jobs
  - `frontend` – SvelteKit app (`classquiz-frontend`)
  - `proxy` – Caddy reverse proxy exposing everything on `http://localhost:8000`

### Frontend

- Built from `frontend/Dockerfile`.
- Originally hard‑coded `API_URL=https://mawoka.eu` in the builder stage; this is acceptable for our usage because the final app calls relative `/api/v1/...` paths behind Caddy.
- Adjusted default **game mode**:
  - `frontend/src/lib/dashboard/start_game.svelte` now sets:
    ```ts
    let selected_game_mode = $state('normal');
    ```
  - “Old‑school mode” (`game_mode="normal"`) is now the default, so **players see both question and answer text** on their devices by default.

### Local Python / `uv` (not used for normal runs)

- We briefly created a `uv` virtualenv and installed backend deps, but this is **not required** for normal sessions since everything is containerized.
- A local attempt to run Alembic migrations failed due to `libmagic` missing on host; this is handled inside the Docker image instead.

---

## 3. Users created for experiments

For internal testing and hosting, we created five accounts via the `/api/v1/users/create` endpoint. All have email verification auto‑skipped (Docker config sets `SKIP_EMAIL_VERIFICATION=True` for the API).

- **Shared password for all accounts**
  - Password: `DevPass123!`

- **Accounts**
  - Amal
    - Username: `Amal`
    - Email: `amal.classquiz@gmail.com`
  - Ashish
    - Username: `Ashish`
    - Email: `ashish.classquiz@gmail.com`
  - Monty
    - Username: `Monty`
    - Email: `monty.classquiz@gmail.com`
  - Umanga
    - Username: `Umanga`
    - Email: `umanga.classquiz@gmail.com`
  - Muhammad
    - Username: `Muhammad`
    - Email: `muhammad.classquiz@gmail.com`

> For instructor‑led sessions we currently use **Monty** as the primary host account.

---

## 4. Quizzes: what exists and how they are generated

### 4.1 Session 1 quiz content

We built a quiz for “**Python Data Model – Session 1**” using slide deck `session_1.html` (bespoke/marp export stored outside the repo, typically under `~/Downloads/`).

The quiz focuses strictly on topics covered in Session 1:

- Objects & names, identity vs equality
- Mutability & aliasing (lists, dicts)
- Shared row pitfalls (“bad matrix” vs “good matrix”)
- Class vs instance attributes and `__dict__`
- Basic GC intuition (last reference, `del`)
- Shallow copies vs nested mutability

### 4.2 Implementation of the Session 1 quiz

- We used the **editor API** for a scripted, reproducible creation:
  1. Log in as `monty.classquiz@gmail.com` via `/api/v1/login/start` and `/api/v1/login/step/1`.
  2. Call `/api/v1/editor/start?edit=false` to obtain an `edit_id`.
  3. POST to `/api/v1/editor/finish?edit_id=...` with a `QuizInput` payload containing:
     - `title`: `Python Data Model – Session 1 Quiz`
     - `description`: `Tricky review of identity, mutability, aliasing, and class vs instance attributes.`
     - `questions`: 15 `QuizQuestion` entries of type `ABCD`, each with:
       - `time: "60"`
       - `answers`: four `ABCDQuizAnswer` items with a single `right=True`.
  4. Confirm via `/api/v1/quiz/list` that the quiz is present for Monty.

- The quiz currently uses **15 questions**:
  - Q1–Q10: core concepts (identity, mutability, bad/good matrix, aliasing, `Config.debug`, immutability set).
  - Q11–Q15: more advanced variants (parameter aliasing, nested list aliasing in dicts, `Settings.theme` with `__dict__`, GC vs `del`, shallow copy semantics).

### 4.3 Markdown documentation

To make the quiz content portable and discussable:

- `quiz_data/monty_python_data_model_session1/session1_quiz.md`
  - Contains all Session 1 questions formatted as slides for `mark`/Markdown‑slides workflows.
  - Uses `---` between slides.
  - Each answer is a checklist; the **correct choice is marked** with `- [x]`, distractors use `- [ ]`.

- `quiz_data/monty_python_data_model_session1/session1_quiz_answer_key.md`
  - One‑page instructor answer key.
  - For each question:
    - States the correct option.
    - Brief justification, referencing only Session 1 concepts.

These files are the **source of truth** for the Session 1 quiz content; the API‑created quiz mirrors them.

### 4.4 Scoring constraints

- Scoring is uniform across questions:
  - `calculate_score` in `classquiz/socket_server/__init__.py` computes up to **1000 points per question**, based on answer correctness and response time relative to the per‑question time limit.
  - There is **no per‑question “weight” or “points” field** in `QuizQuestion` or the editor.
- If future sessions require “hard questions worth more points”, the current workaround is:
  - Add **multiple questions** for the same concept instead of changing per‑question weights.
  - A deeper change would require touching models, scoring code, and UI.

---

## 5. Problems encountered and how they were fixed

### 5.1 Local dev vs Docker confusion

- Initially tried to set up a local environment using `uv`, Alembic, and system packages.
- Hit a runtime error when running Alembic migrations due to missing `libmagic` on the host.
- Resolution:
  - Switched to a **Docker‑first workflow**:
    - All Python deps and OS libraries are installed in the `api` image.
    - Host installation of `libmagic` and similar packages is not required.

### 5.2 Frontend crash: `t.data.quizzes is not iterable`

- After login, the dashboard threw a runtime error (`data.quizzes is not iterable`) when API requests returned 401 JSON objects instead of arrays.
- Root cause:
  - `frontend/src/routes/dashboard/+page.ts` assumed `fetch('/api/v1/quiz/list')` and `fetch('/api/v1/quiztivity/')` always returned lists.
- Fix:
  - Updated loader to:
    - Check `res.ok` before reading JSON.
    - Default to `[]` when requests fail or payloads are not arrays:
      ```ts
      const quiz_res = await fetch('/api/v1/quiz/list?page_size=100');
      let quizzes: unknown = [];
      if (quiz_res.ok) quizzes = await quiz_res.json();
      // same for quiztivities
      return {
        quizzes: Array.isArray(quizzes) ? quizzes : [],
        quiztivities: Array.isArray(quiztivities) ? quiztivities : []
      };
      ```

### 5.3 Player view not showing text

- Observed behavior:
  - Host screen showed both question and answers.
  - Player screen showed only four colored tiles with icons (Kahoot‑style), no question/answer text.
- Root cause:
  - Games were started in `game_mode="kahoot"` (the default), which intentionally hides text on players:
    - In `frontend/src/lib/play/question.svelte`, answer text is wrapped in:
      ```svelte
      {#if game_mode === 'kahoot'}
        <img ... />   <!-- icons only -->
      {:else}
        <p class="m-auto">{answer.answer}</p>
      {/if}
      ```
- Fix:
  - Changed the **default game mode** in the start‑game overlay to `"normal"` (old‑school mode):
    - Players now see question + answer text by default.
  - Host can still explicitly choose the “Normal/Kahoot” mode in the UI if needed.

### 5.4 Cleaning out test responses

- Redis stored in‑progress results under keys like `game_session:<PIN>:...`.
- For a dry‑run game (PIN `124868`), we manually reset state by deleting:
  - `game_session:124868`, `game_session:124868:0`, `:1`, `:2`
  - `game_session:124868:players`, `:players:Monty`
  - `game_session:124868:player_scores`
- Verified via `redis-cli KEYS "game_session:*"` that no stray session keys remained.
- Confirmed via `/api/v1/results/list` that no `GameResults` rows existed for Monty before rebuilding the quiz.

---

## 6. Running and closing the system

### 6.1 First‑time setup (Docker)

From a fresh clone:

```bash
git clone git@github.com:DiversioTeam/ClassQuiz.git
cd ClassQuiz
docker compose up -d
```

What this does:

- Builds and/or starts:
  - Postgres, Redis, Meilisearch
  - API + Worker
  - Frontend (SvelteKit, served via Node)
  - Proxy (Caddy) on `localhost:8000`

Check status:

```bash
docker compose ps
```

You should see `proxy` bound to `0.0.0.0:8000->8080` and all services “Up”.

Once the containers are up, verify the API:

```bash
curl http://localhost:8000/openapi.json | head
```

Then verify the frontend:

- Visit `http://localhost:8000` in a browser.

Finally, bootstrap the shared dev/test users so you can log in with the
same accounts described in §3:

```bash
python scripts/bootstrap_dev_test_users.py
```

By default this script talks to `http://localhost:8000`. If you are using a
different base URL (for example via ngrok), set `CLASSQUIZ_BASE_URL`:

```bash
CLASSQUIZ_BASE_URL=https://your-host.example.com \
  python scripts/bootstrap_dev_test_users.py
```

### 6.2 Stopping the system

To stop containers but keep volumes (DB, etc.):

```bash
docker compose down
```

To also wipe persistent volumes (useful to reset everything):

```bash
docker compose down --volumes
```

For **dev‑only backing services** (without frontend/API) there is also `docker-compose.dev.yml`, but the primary flow is using the main `docker-compose.yml`.

---

## 7. Running a quiz session (host + players)

### 7.1 Host workflow (Monty)

1. Ensure Docker stack is up (`docker compose up -d`).
2. Open browser at `http://localhost:8000`.
3. Log in as host (currently using Monty):
   - Username/email: `Monty` or `monty.classquiz@gmail.com`
   - Password: `DevPass123!`
4. Go to **Dashboard** and locate:
   - `Python Data Model – Session 1 Quiz`
5. Click **Start Game**:
   - The start overlay appears with:
     - Captcha toggle (usually off for local sessions).
     - Two mode cards:
       - Left: “Normal” (Kahoot style, icons only on player devices).
       - Right: “Old‑school mode” (players see question + answers) – this is now the **default** (`game_mode="normal"`).
   - Ensure the right‑hand “Old‑school mode” card is selected unless you explicitly want Kahoot mode.
6. Start the game:
   - A new game PIN and `game_id` are generated.
   - Host is redirected to `/admin?token=...&pin=...` (admin view).
   - Host controls question progression and can show/hide solutions.

### 7.2 Player workflow

1. Players open `http://localhost:8000` in their browsers.
2. They join via the **Play/Join** flow, entering the PIN announced by the host.
3. With `game_mode="normal"`:
   - Each player sees the **question text** and **answer texts** on their own device.
   - They tap/click their choice.
4. Scores are computed server‑side using the shared scoring function.

### 7.3 Resetting between runs

For small test runs:

- You can ignore old `game_session:*` keys; they expire automatically.

If you need a **completely clean slate**:

1. Stop and clear volumes:
   ```bash
   docker compose down --volumes
   ```
2. Bring everything back up (`docker compose up -d`).
3. Recreate quizzes via the scripted approach (or simply rely on the existing Session 1 quiz if persistence is acceptable).

---

## 8. Surveys and feedback collection

ClassQuiz does not have a dedicated “survey” object type; instead, we leverage existing features:

### 8.1 In‑platform surveys (preferred)

- Create a separate quiz (e.g. `Session 1 – Feedback Survey`) using:
  - **VOTING** type questions for Likert‑scale responses (“How confident are you with aliasing?”).
  - **TEXT** type questions for open feedback.
- Run the survey as a **short quiz** at the end of the session:
  - Start it from the Dashboard as another game (often with `game_mode="normal"`).
  - Have participants join with a new PIN.
  - Results are stored in the same mechanism (`GameResults`, Redis, etc.).

### 8.2 External surveys linked from ClassQuiz

- Use the “custom field” or quiz description to point to an external survey tool (e.g. Google Forms).
- Alternatively, use a **TEXT** question whose prompt is:
  - “Enter the short code you get after completing the external survey at <link>.”
- This lets you still track who completed the survey while keeping richer survey tooling outside ClassQuiz.

### 8.3 Documentation

- If a survey quiz is created, mirror it in Markdown in the same way as Session 1:
  - `sessionX_survey.md` – question slides.
  - `sessionX_survey_answer_key.md` – if there are any “correct” answers or canonical mappings.

---

## 9. Guidance for future agents

- **Do not** assume per‑question scoring weights exist; if needed, discuss a design for extending `QuizQuestion` and scoring first.
- When modifying quiz content:
  - Keep Markdown (`quiz_data/monty_python_data_model_session1/session1_quiz.md`, `quiz_data/monty_python_data_model_session1/session1_quiz_answer_key.md`) as the canonical source.
  - Reflect changes into the database via the editor API rather than hand‑editing DB rows.
- When adding new session quizzes:
  - Follow the same pattern:
    - Design in Markdown under `quiz_data/<owner_or_team>_<topic>_<session>/`.
    - Script creation via `/editor/start` + `/editor/finish`.
  - Add new documentation files following the `sessionN_*` naming pattern inside the appropriate subfolder.
- Prefer Docker for all runtime tasks; avoid host‑level migrations unless strictly necessary.

---

## 10. Authoring world‑class technical quizzes (code formatting & structure)

The goal for all future technical quizzes is **high readability under time pressure**. We now have first‑class support for code formatting and syntax highlighting in the frontend. New quizzes **must** follow these practices.

### 10.1 Question structure: title + code block

- Treat each question as two parts:
  - A short **title sentence** that states the task in plain language.
  - An optional **code block** containing the snippet to reason about.
- In the backend (and in Markdown that will be imported), encode this as:
  - Title line(s)
  - A **blank line**
  - Then the code, one statement per line.
- Example (as stored in `question.question` and in `sessionN_quiz.md`):

  ```text
  Given the following shallow copy, what is printed for `nested` and `copy`?

  nested = [[0], [0]]
  copy = list(nested)

  nested[0].append(1)

  print('nested:', nested)
  print('copy:', copy)
  ```

- The frontend splits this into:
  - Title: text above the first blank line (rendered as normal text with inline backticks).
  - Code: everything after the first blank line (rendered via a syntax‑highlighted `<CodeBlock>`).

### 10.2 Choices: inline code where appropriate

- Use **inline backticks** for any answer that is:
  - Code (`x == y`, `a += [5]`, `len(x)`, `Settings.theme`, etc.).
  - Structured data (`[[0, 1], [0]]`, `{'theme': 'dark'}`).
  - Precise output or value (`3`, `2 then 1`, `TypeError` messages, etc.).
- In the DB and Markdown, wrap such answers as:

  ```text
  - [x] `nested: [[0, 1], [0]], copy: [[0, 1], [0]]`
  - [ ] `nested: [[0, 1], [0]], copy: [[0], [0]]`
  ```

- The frontend converts backticks to `<code>` and styles them uniformly:
  - Monospace font.
  - Subtle darker background.
  - Small padding and rounded corners.

- Prefer wrapping the **entire answer** when it reads like a code phrase or output. For longer English sentences that merely *mention* code, it is often clearer to only backtick the code identifiers (e.g. “The list is still alive because `alias` still refers to it.”).

### 10.3 Supported languages and highlighting

- The frontend uses `highlight.js` with a small curated set of languages:
  - Python, JavaScript/TypeScript, Bash/Shell, JSON, SQL.
- `CodeBlock.svelte` will:
  - Use an explicit `language` prop if we ever add it.
  - Otherwise auto‑detect the language from the code.
- For new quizzes:
  - Stick to these languages where possible.
  - Keep code snippets **short and focused** (5–15 lines max) to fit on projector and mobile screens.

### 10.4 How to author quizzes using this pattern

When designing a new technical quiz (e.g. `session2_quiz.md`):

- For **each question**:
  1. Start with a one‑sentence title that clearly states what is being asked:
     - “What does the following code print?”
     - “Which option best describes the behavior of `__slots__`?”
  2. If the question is code‑based, add a blank line and then the code block.
  3. Write 3–5 answer choices:
     - Use backticks around outputs, expressions, or data shapes.
     - Keep each choice as a single line where possible.
     - Avoid mixing too much prose and code in the same choice; prefer either a short coded answer or a short conceptual phrase.

- In Markdown (`sessionN_quiz.md`):
  - Use fenced code blocks for the snippet (` ```python ... ``` `).
  - Use `- [x]` / `- [ ]` for correct/incorrect answers, with backticks as described.
  - Mirror the pattern used in `quiz_data/monty_python_data_model_session1/session1_quiz.md` and `quiz_data/monty_python_data_model_session1/session1_quiz_answer_key.md`.

- In the DB:
  - Keep `QuizQuestion.question` in the exact “title + blank line + code” form.
  - Use the editor API (`/api/v1/editor/start` + `/api/v1/editor/finish`) and scripts (like the ones used for Session 1 and Connection Test Quiz) to update questions programmatically rather than hand‑editing via the UI.

### 10.5 Existing examples to copy

- **Connection Test Quiz**
  - Shows how to combine:
    - One or two very short concept questions.
    - Several full code‑block questions with backticked outputs.
  - Good model for “warm‑up” quizzes that still demonstrate formatting.
  - To ensure this quiz exists and is normalized on a fresh database, run:

    ```bash
    python scripts/sync/sync_connection_test_quiz.py
    ```

- **Python Data Model – Session 1 Quiz**
  - Now uses:
    - Title + code‑block structure for all code‑heavy questions.
    - Backticks for almost all code‑like choices.
  - Use this as the primary reference for future Python/internal‑mechanics quizzes.

### 10.6 Expectations for future agents

- When adding or editing any technical quiz:
  - **Always**:
    - Split code out of question titles into dedicated blocks (title + blank line + code).
    - Use backticks for code‑like choices so they render as inline code.
  - Check the quiz in three views:
    - Dashboard → “View” (`/view/{quiz_id}`) for static layout.
    - Practice mode (`/practice?quiz_id=...`) for per‑question experience.
    - Live play (host + player) for how it feels under time pressure.
- Prefer small, focused questions that test a single idea with clear code and answers rather than long, paragraph‑style prompts.

### 10.7 Quiz formatting linter

To keep quizzes consistent with these conventions, there is a small helper script:

- `scripts/validate_quiz_markdown.py`
  - Usage:
    - `python scripts/validate_quiz_markdown.py quiz_data/monty_python_data_model_session1/session1_quiz.md`
    - You can pass multiple files, e.g. `python scripts/validate_quiz_markdown.py quiz_data/your_team_topic_sessionX/sessionX_quiz.md quiz_data/your_team_topic_sessionY/sessionY_quiz.md`.
  - What it does:
    - Treats `##` headings as question boundaries and `---` as slide separators.
    - Flags **titles** that look code‑like but do **not** have a code block in the same question.
    - Flags **titles** that still mix a lot of code with prose when a block is present, suggesting you move code down.
    - Flags **answers** that look code‑like (matrices, lists, expressions, outputs) but do **not** use backticks.
  - It prints warnings to stderr and returns a non‑zero exit code if it finds issues (useful in CI).

Recommended workflow for new session quizzes:

1. Author `sessionN_quiz.md` using the patterns in §10.1–10.4.
2. Place it under an appropriate subfolder, e.g. `quiz_data/<owner_or_team>_<topic>_<session>/sessionN_quiz.md`.
3. Run `python scripts/validate_quiz_markdown.py quiz_data/<owner_or_team>_<topic>_<session>/sessionN_quiz.md` and address warnings.
4. Once the Markdown looks clean, use the editor API + scripts (as with Session 1) to create/update the quiz in the DB.

---

## 11. Scripts and filesystem layout

To keep the repo tidy as more people add quizzes and helpers:

- **Python helper scripts**
  - Live under `scripts/`.
  - Long‑lived utilities (used across sessions) go directly in `scripts/`:
    - `scripts/validate_quiz_markdown.py`
    - `scripts/simulate_players.py`
    - `scripts/export_results_from_redis.py`
  - One‑off or migration‑style scripts live under `scripts/sync/`:
    - `scripts/sync/sync_session1_quiz_append_new_questions.py`
    - `scripts/sync/sync_session1_tricky_timers.py`
    - `scripts/sync/sync_connection_test_quiz.py`
  - Future agents should avoid adding new `.py` helpers at the repo root; put them in `scripts/` (or a subfolder) instead.

- **Quiz Markdown**
  - All quiz Markdown lives under `quiz_data/`.
  - Each quiz (or closely related quiz family) gets its own subfolder named like:
    - `quiz_data/<owner_or_team>_<topic>_<session>/`
    - Example: `quiz_data/monty_python_data_model_session1/`
  - Within each subfolder, use consistent filenames:
    - `sessionN_quiz.md`
    - `sessionN_quiz_answer_key.md`
    - Optional extras such as `sessionN_survey.md`, `sessionN_survey_answer_key.md`.
  - When documenting new quizzes in this file, reference the full `quiz_data/...` paths so it is obvious where the canonical Markdown lives.
