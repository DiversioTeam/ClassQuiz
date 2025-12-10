"""
Update the time limit for the harder Session 1 questions
to 75 seconds via the editor API.

We treat the \"hard\" questions as the ones defined in
`sync_session1_quiz_append_new_questions.build_new_question_definitions`
and identified by their `marker` strings.

Usage (with Docker stack running on localhost:8000, from repo root):

    python scripts/sync/sync_session1_tricky_timers.py

You can override defaults via:

    CLASSQUIZ_BASE_URL   (default: http://localhost:8000)
    CLASSQUIZ_EMAIL      (default: monty.classquiz@gmail.com)
    CLASSQUIZ_PASSWORD   (default: DevPass123!)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import httpx

from sync_session1_quiz_append_new_questions import (  # type: ignore
    DEFAULT_BASE_URL,
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    DEFAULT_QUIZ_TITLE,
    build_new_question_definitions,
    login_and_get_token,
    find_quiz_id,
)


TRICKY_TIME_SECONDS = 75


def mark_tricky_questions(quiz: dict[str, Any]) -> bool:
    """
    Set the `time` field of the hard/container questions to TRICKY_TIME_SECONDS.

    We locate them by checking for the marker substring inside the question text.
    Returns True if any question was modified.
    """

    markers: list[str] = [d["marker"] for d in build_new_question_definitions()]
    questions: list[dict[str, Any]] = quiz.get("questions", [])
    total = len(questions)
    # In the current design the hard questions are appended at the
    # end of the quiz. Use this as a secondary signal so that even
    # if a marker string changes slightly, the last N questions are
    # still treated as tricky.
    tail_start_index = max(0, total - len(markers))

    changed = False

    for idx, q in enumerate(questions):
        text = q.get("question", "") or ""
        is_tricky = idx >= tail_start_index or any(marker in text for marker in markers)
        if is_tricky:
            current = str(q.get("time", "") or "")
            desired = str(TRICKY_TIME_SECONDS)
            if current != desired:
                q["time"] = desired
                changed = True

    quiz["questions"] = questions
    return changed


def push_quiz_update(client: httpx.Client, quiz_id: str, quiz: dict[str, Any]) -> None:
    """Send the updated quiz back via the editor API."""

    quiz_input = {
        "public": quiz.get("public", False),
        "title": quiz["title"],
        "description": quiz.get("description") or "",
        "cover_image": quiz.get("cover_image"),
        "background_color": quiz.get("background_color"),
        "background_image": quiz.get("background_image"),
        "questions": quiz["questions"],
    }

    start_resp = client.post(
        "/editor/start",
        params={"edit": "true", "quiz_id": quiz_id},
    )
    start_resp.raise_for_status()
    edit_id = start_resp.json()["token"]

    finish_resp = client.post("/editor/finish", params={"edit_id": edit_id}, json=quiz_input)
    finish_resp.raise_for_status()
    print(f"Quiz {quiz_id} updated successfully with new timers for tricky questions.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Set time=75s for the harder alias/container questions "
            "in the Session 1 quiz via the editor API."
        ),
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CLASSQUIZ_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for Caddy / ClassQuiz (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("CLASSQUIZ_EMAIL", DEFAULT_EMAIL),
        help="Login email (default: monty.classquiz@gmail.com)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("CLASSQUIZ_PASSWORD", DEFAULT_PASSWORD),
        help="Login password (default: DevPass123!)",
    )
    parser.add_argument(
        "--quiz-id",
        help="Quiz UUID to update; if omitted, the quiz is located by title.",
    )
    parser.add_argument(
        "--quiz-title",
        default=os.environ.get("CLASSQUIZ_QUIZ_TITLE", DEFAULT_QUIZ_TITLE),
        help="Quiz title to search for when --quiz-id is not provided.",
    )

    args = parser.parse_args()
    api_base = args.base_url.rstrip("/") + "/api/v1"

    try:
        with httpx.Client(base_url=api_base, timeout=10.0, follow_redirects=True) as client:
            token = login_and_get_token(client, args.email, args.password)
            client.headers["Authorization"] = f"Bearer {token}"

            quiz_id = args.quiz_id or find_quiz_id(client, args.quiz_title)
            get_resp = client.get(f"/quiz/get/{quiz_id}")
            get_resp.raise_for_status()
            quiz = get_resp.json()

            if not mark_tricky_questions(quiz):
                print("No timer changes needed; tricky questions already at desired time.")
                return

            push_quiz_update(client, quiz_id, quiz)
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
