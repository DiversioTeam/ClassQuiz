"""
Utility script to normalize the formatting of the
\"Connection Test Quiz\" so that it follows the same
title + blank-line + code-block pattern we use for
Session quizzes.

It updates the quiz in-place via the editor API:

1. Logs in with PASSWORD auth (Monty by default).
2. Locates the quiz by title (or uses --quiz-id).
3. Rewrites question text for the code-heavy items
   so that participants see:
      - A short prose title, and
      - A nicely formatted code block.

Usage (from repo root, with Docker stack running):

    python scripts/sync/sync_connection_test_quiz.py

You can override defaults via env vars or flags:

    CLASSQUIZ_BASE_URL   (default: http://localhost:8000)
    CLASSQUIZ_EMAIL      (default: monty.classquiz@gmail.com)
    CLASSQUIZ_PASSWORD   (default: DevPass123!)

    python scripts/sync/sync_connection_test_quiz.py --base-url https://your-host \
        --email you@example.com --password 'secret'
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from typing import Any, Dict, List

import httpx


DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_EMAIL = "monty.classquiz@gmail.com"
DEFAULT_PASSWORD = "DevPass123!"
DEFAULT_QUIZ_TITLE = "Connection Test Quiz"


def _clean_question(text: str) -> str:
    """Normalize leading/trailing whitespace on a multi-line question."""

    return textwrap.dedent(text).strip("\n")


def build_updated_question_texts() -> Dict[int, str]:
    """
    Return the desired question text for each index (0-based)
    in the Connection Test Quiz.

    We keep the existing simple conceptual questions as-is and
    only reformat the code-heavy ones to follow the
    \"title + blank line + code\" pattern.
    """

    return {
        # Q1
        0: _clean_question(
            """
            Given this function, what does `sum_positive([-1, 1, 2])` print?

            def sum_positive(nums):
                total = 0
                for n in nums:
                    if n > 0:
                        total += n
                return total

            print(sum_positive([-1, 1, 2]))
            """
        ),
        # Q5
        4: _clean_question(
            """
            What does this loop print?

            total = 0
            for i in range(3):
                total += i
            print(total)
            """
        ),
        # Q6
        5: _clean_question(
            """
            For this code, what gets printed?

            values = [1, 2, 3]
            for v in values:
                if v % 2 == 0:
                    print(v)
            """
        ),
        # Q7
        6: _clean_question(
            """
            What does this program print?

            x = 1

            def f():
                x = 2
                print(x)

            f()
            print(x)
            """
        ),
    }


def login_and_get_token(client: httpx.Client, email: str, password: str) -> str:
    """Perform the two-step login flow and return the access token."""

    start_resp = client.post("/login/start", json={"email": email})
    start_resp.raise_for_status()
    start_data = start_resp.json()

    session_id = start_data["session_id"]
    step_1_methods = set(start_data.get("step_1", []))
    if "PASSWORD" not in step_1_methods:
        raise RuntimeError("Account is not configured for PASSWORD login; cannot proceed.")

    step_resp = client.post(
        "/login/step/1",
        params={"session_id": session_id},
        json={"auth_type": "PASSWORD", "data": password},
    )
    step_resp.raise_for_status()
    step_data = step_resp.json()
    token = step_data["access_token"]
    return token


def find_quiz_id(client: httpx.Client, title: str) -> str | None:
    """Find the quiz id for the given title for the current user.

    Returns the quiz ID or ``None`` if no matching quiz exists.
    """

    resp = client.get("/quiz/list", params={"page_size": 100, "page": 1})
    resp.raise_for_status()
    quizzes = resp.json()

    matches = [quiz for quiz in quizzes if quiz.get("title") == title]
    if not matches:
        return None
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple quizzes with title {title!r} found; "
            f"pass --quiz-id explicitly to disambiguate."
        )
    return matches[0]["id"]


def apply_question_text_updates(quiz: Dict[str, Any]) -> bool:
    """
    Update the question text for the Connection Test Quiz in-place.

    Returns True if any question text was changed.
    """

    questions: List[Dict[str, Any]] = quiz.get("questions", [])
    desired_texts = build_updated_question_texts()

    changed = False
    for idx, new_text in desired_texts.items():
        if idx >= len(questions):
            raise RuntimeError(
                f"Expected question index {idx} to exist, "
                f"but quiz only has {len(questions)} questions."
            )
        old_text = questions[idx].get("question", "")
        if old_text != new_text:
            print(f"Updating question {idx + 1} text")
            questions[idx]["question"] = new_text
            changed = True
        else:
            print(f"Question {idx + 1} already up to date")

    quiz["questions"] = questions
    return changed


def push_quiz_update(client: httpx.Client, quiz_id: str, quiz: Dict[str, Any]) -> None:
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
    print(f"Quiz {quiz_id} updated successfully.")


def build_connection_test_quiz_payload() -> Dict[str, Any]:
    """
    Build a minimal quiz definition for the Connection Test Quiz.

    This mirrors the structure we currently use in our internal instance:
    seven short questions to verify connectivity and formatting.
    """

    def q(question: str, time: int, answers: list[tuple[str, bool]]) -> Dict[str, Any]:
        return {
            "question": _clean_question(question),
            "time": str(time),
            "type": "ABCD",
            "answers": [{"right": is_right, "answer": text, "color": None} for text, is_right in answers],
            "image": None,
            "hide_results": False,
        }

    questions: List[Dict[str, Any]] = [
        q(
            """
            Given this function, what does `sum_positive([-1, 1, 2])` print?

            def sum_positive(nums):
                total = 0
                for n in nums:
                    if n > 0:
                        total += n
                return total

            print(sum_positive([-1, 1, 2]))
            """,
            30,
            [
                ("`3`", True),
                ("`2`", False),
                ("`6`", False),
                ("`It raises a TypeError`", False),
            ],
        ),
        q(
            "Quick sanity check: what is `1 + 1`?",
            30,
            [
                ("`1`", False),
                ("`2`", True),
                ("`3`", False),
                ("`4`", False),
            ],
        ),
        q(
            "Which of these is a day of the week?",
            30,
            [
                ("`Blue`", False),
                ("`Circle`", False),
                ("`Wednesday`", True),
                ("`Triangle`", False),
            ],
        ),
        q(
            "Read the sentence and answer: <b>All participants will complete a short survey after the quiz.</b> Which statement is true?",
            45,
            [
                ("Only some participants will complete a survey.", False),
                ("No surveys will be used.", False),
                ("Every participant is expected to complete a survey.", True),
                ("The survey happens before the quiz.", False),
            ],
        ),
        q(
            """
            What does this loop print?

            total = 0
            for i in range(3):
                total += i
            print(total)
            """,
            30,
            [
                ("`3`", True),
                ("`2`", False),
                ("`6`", False),
                ("`It raises an error`", False),
            ],
        ),
        q(
            """
            For this code, what gets printed?

            values = [1, 2, 3]
            for v in values:
                if v % 2 == 0:
                    print(v)
            """,
            30,
            [
                ("`1`", False),
                ("`2`", True),
                ("`3`", False),
                ("`1 3`", False),
            ],
        ),
        q(
            """
            What does this program print?

            x = 1

            def f():
                x = 2
                print(x)

            f()
            print(x)
            """,
            30,
            [
                ("`2 then 1`", True),
                ("`1 then 2`", False),
                ("`2 then 2`", False),
                ("`1 then 1`", False),
            ],
        ),
    ]

    return {
        "public": False,
        "title": DEFAULT_QUIZ_TITLE,
        "description": "Short warm-up quiz to verify connectivity and formatting.",
        "cover_image": None,
        "background_color": None,
        "background_image": None,
        "questions": questions,
    }


def create_quiz_if_missing(client: httpx.Client, title: str) -> str:
    """
    Ensure the Connection Test Quiz exists for the current user.

    Returns the quiz ID (existing or newly created).
    """

    existing_id = find_quiz_id(client, title)
    if existing_id is not None:
        print(f"Found existing quiz {title!r} with id {existing_id}")
        return existing_id

    print(f"No quiz named {title!r} found; creating a new one.")
    quiz_input = build_connection_test_quiz_payload()

    start_resp = client.post(
        "/editor/start",
        params={"edit": "false"},
    )
    start_resp.raise_for_status()
    edit_id = start_resp.json()["token"]

    finish_resp = client.post("/editor/finish", params={"edit_id": edit_id}, json=quiz_input)
    finish_resp.raise_for_status()
    data = finish_resp.json()
    quiz_id = data.get("id") or data.get("quiz_id")
    if not quiz_id:
        raise RuntimeError("Editor API did not return a quiz id after creation.")
    print(f"Created Connection Test Quiz with id {quiz_id}")
    return quiz_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize code formatting for the Connection Test Quiz via the editor API.",
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

            quiz_id = args.quiz_id or create_quiz_if_missing(client, args.quiz_title)
            get_resp = client.get(f"/quiz/get/{quiz_id}")
            get_resp.raise_for_status()
            quiz = get_resp.json()

            changed = apply_question_text_updates(quiz)
            if not changed:
                print("No question text changes needed; quiz already normalized.")
                return

            push_quiz_update(client, quiz_id, quiz)
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
