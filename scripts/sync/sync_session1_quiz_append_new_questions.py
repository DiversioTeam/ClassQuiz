"""
Append the new hard container / namespace questions to the
existing “Python Data Model – Session 1 Quiz” via the editor API.

Usage (with Docker stack running on localhost:8000, from repo root):

    python scripts/sync/sync_session1_quiz_append_new_questions.py

You can override defaults via:

    python scripts/sync/sync_session1_quiz_append_new_questions.py \
        --base-url http://localhost:8000 \
        --email monty.classquiz@gmail.com \
        --password DevPass123! \
        --quiz-id <uuid>  # optional, otherwise found by title
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
DEFAULT_QUIZ_TITLE = "Python Data Model – Session 1 Quiz"


def build_new_question_definitions() -> List[Dict[str, Any]]:
    """Return metadata for the new questions to append."""

    return [
        {
            "marker": "Row aliasing across copies",
            "question": """
                Row aliasing across copies: what gets printed?

                row = [0]
                matrix = [row] * 3
                clone = matrix[:]

                row.append(1)
                matrix[1].append(2)

                print("row:", row)
                print("matrix:", matrix)
                print("clone:", clone)
            """,
            "answers": [
                "row: [0, 1, 2], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1, 2], [0, 1, 2], [0, 1, 2]]",
                "row: [0, 1, 2], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1], [0, 1], [0, 1]]",
                "row: [0, 1], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1], [0, 1], [0, 1]]",
                "row: [0, 1, 2], matrix: [[0, 1], [0, 1], [0, 1]], clone: [[0, 1, 2], [0, 1, 2], [0, 1, 2]]",
            ],
            "right_index": 0,
        },
        {
            "marker": "Tuple of lists: shared vs copied",
            "question": """
                Tuple of lists: shared vs copied – what gets printed?

                inner = [0]
                t1 = (inner, inner)
                t2 = (inner[:], inner[:])

                inner.append(1)

                print("t1:", t1)
                print("t2:", t2)
            """,
            "answers": [
                "t1: ([0, 1], [0, 1]), t2: ([0], [0])",
                "t1: ([0], [0]), t2: ([0, 1], [0, 1])",
                "t1: ([0, 1], [0, 1]), t2: ([0, 1], [0, 1])",
                "t1: ([0], [0, 1]), t2: ([0], [0, 1])",
            ],
            "right_index": 0,
        },
        {
            "marker": "Dict values: mutate vs rebind",
            "question": """
                Dict values: mutate vs rebind – what do these fields contain?

                shared = []
                config = {"a": shared, "b": shared}

                config["a"].append(1)
                config["b"] = config["b"] + [2]

                print("config['a']:", config["a"])
                print("config['b']:", config["b"])
            """,
            "answers": [
                "config['a']: [1], config['b']: [1, 2]",
                "config['a']: [1, 2], config['b']: [1, 2]",
                "config['a']: [1, 2], config['b']: [2]",
                "config['a']: [1], config['b']: [2]",
            ],
            "right_index": 0,
        },
        {
            "marker": "Mutate inner, then rebind slot",
            "question": """
                Mutate inner list, then rebind the slot – what do `data` and `alias` see?

                def tweak(seq):
                    first = seq[0]
                    first.append("X")
                    seq[0] = first + ["Y"]

                data = [[1], [2]]
                alias = data

                tweak(data)

                print("data:", data)
                print("alias:", alias)
            """,
            "answers": [
                "data: [[1, 'X', 'Y'], [2]], alias: [[1, 'X', 'Y'], [2]]",
                "data: [[1, 'X'], [2]], alias: [[1, 'X'], [2]]",
                "data: [[1, 'X', 'Y'], [2]], alias: [[1], [2]]",
                "data: [[1], [2]], alias: [[1, 'X', 'Y'], [2]]",
            ],
            "right_index": 0,
        },
        {
            "marker": "Breaking aliases with rebinding",
            "question": """
                Breaking aliases with rebinding – what do `a`, `b`, and `nums` contain?

                nums = [1, 2, 3]
                a = nums
                b = nums[:]

                nums = nums + [4]
                nums.append(5)

                print("a:", a)
                print("b:", b)
                print("nums:", nums)
            """,
            "answers": [
                "a: [1, 2, 3], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]",
                "a: [1, 2, 3, 4, 5], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]",
                "a: [1, 2, 3, 4], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]",
                "a: [1, 2, 3, 4], b: [1, 2, 3, 4], nums: [1, 2, 3, 4, 5]",
            ],
            "right_index": 0,
        },
        {
            "marker": "Outer rebind vs inner mutate with slices",
            "question": """
                Outer rebind vs inner mutate with slices – what do the three lists contain?

                rows = [[0], [0]]
                alias = rows
                clone = rows[:]

                alias[0] = [1]
                clone[1].append(2)

                print("rows:", rows)
                print("alias:", alias)
                print("clone:", clone)
            """,
            "answers": [
                "rows: [[1], [0, 2]], alias: [[1], [0, 2]], clone: [[0], [0, 2]]",
                "rows: [[1], [0]], alias: [[1], [0]], clone: [[1], [0, 2]]",
                "rows: [[1], [0, 2]], alias: [[1], [0]], clone: [[0], [0, 2]]",
                "rows: [[1], [0, 2]], alias: [[1], [0, 2]], clone: [[1], [0, 2]]",
            ],
            "right_index": 0,
        },
        {
            "marker": "*= with nested lists",
            "question": """
                Using `*=` with a list of lists – what happens to `nested` and `alias`?

                nested = [[1], [2]]
                alias = nested

                nested *= 2
                nested[0].append(3)

                print("nested:", nested)
                print("alias:", alias)
            """,
            "answers": [
                "nested: [[1, 3], [2], [1, 3], [2]], alias: [[1, 3], [2], [1, 3], [2]]",
                "nested: [[1, 3], [2], [1], [2]], alias: [[1, 3], [2], [1], [2]]",
                "nested: [[1, 3], [2], [1, 3], [2]], alias: [[1], [2]]",
                "nested: [[1], [2], [1], [2]], alias: [[1, 3], [2], [1, 3], [2]]",
            ],
            "right_index": 0,
        },
        {
            "marker": "Module vs class vs instance name",
            "question": """
                Module vs class vs instance name – what does `obj.show()` print?

                x = "module"

                class Thing:
                    x = "class"
                    def __init__(self):
                        self.x = "instance"
                    def show(self):
                        print(x, self.x, Thing.x)

                obj = Thing()
                obj.show()
            """,
            "answers": [
                "It prints `module instance class`.",
                "It prints `class instance class`.",
                "It prints `module class instance`.",
                "It prints `instance instance instance`.",
            ],
            "right_index": 0,
        },
        {
            "marker": "Global rebinding vs aliased list",
            "question": """
                Global rebinding vs aliased list – what do `items` and `alias` contain?

                items = []

                def add():
                    items.append(\"A\")

                def reset():
                    global items
                    items = []

                add()
                alias = items
                reset()

                print("items:", items)
                print("alias:", alias)
            """,
            "answers": [
                "items: [], alias: ['A']",
                "items: ['A'], alias: ['A']",
                "items: [], alias: []",
                "items: ['A'], alias: []",
            ],
            "right_index": 0,
        },
    ]


def build_question_payload(defn: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an internal question definition into a QuizQuestion payload."""

    question_text = textwrap.dedent(defn["question"]).strip("\n")

    answers_payload: List[Dict[str, Any]] = []
    for index, answer_text in enumerate(defn["answers"]):
        answers_payload.append(
            {
                "right": index == defn["right_index"],
                "answer": f"`{answer_text}`" if "[" in answer_text or "items:" in answer_text or "alias:" in answer_text else answer_text,
                "color": None,
            }
        )

    return {
        "question": question_text,
        "time": "60",
        "type": "ABCD",
        "answers": answers_payload,
        "image": None,
        "hide_results": False,
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
        f"/login/step/1",
        params={"session_id": session_id},
        json={"auth_type": "PASSWORD", "data": password},
    )
    step_resp.raise_for_status()
    step_data = step_resp.json()
    token = step_data["access_token"]
    return token


def find_quiz_id(client: httpx.Client, title: str) -> str:
    """Find the quiz id for the given title for the current user."""

    resp = client.get("/quiz/list", params={"page_size": 100, "page": 1})
    resp.raise_for_status()
    quizzes = resp.json()

    matches = [quiz for quiz in quizzes if quiz.get("title") == title]
    if not matches:
        raise RuntimeError(f"Quiz with title {title!r} not found in /quiz/list.")
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple quizzes with title {title!r} found; "
            f"pass --quiz-id explicitly to disambiguate."
        )
    return matches[0]["id"]


def append_new_questions_if_missing(quiz: Dict[str, Any]) -> bool:
    """
    Append new questions to quiz['questions'] if they are not present yet.

    Returns True if any questions were added.
    """

    questions: List[Dict[str, Any]] = quiz.get("questions", [])
    existing_texts = [q.get("question", "") for q in questions]

    new_definitions = build_new_question_definitions()
    added_any = False

    for defn in new_definitions:
        marker: str = defn["marker"]
        if any(marker in text for text in existing_texts):
            continue
        questions.append(build_question_payload(defn))
        added_any = True

    quiz["questions"] = questions
    return added_any


def update_quiz(
    client: httpx.Client,
    quiz_id: str,
) -> None:
    """Fetch quiz, append new questions, and push update via editor API."""

    get_resp = client.get(f"/quiz/get/{quiz_id}")
    get_resp.raise_for_status()
    quiz = get_resp.json()

    changed = append_new_questions_if_missing(quiz)
    if not changed:
        print("No new questions to add; quiz already contains all markers.")
        return

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

    finish_resp = client.post(f"/editor/finish", params={"edit_id": edit_id}, json=quiz_input)
    finish_resp.raise_for_status()
    print(f"Quiz {quiz_id} updated successfully with new hard questions.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append hard container / namespace questions to the Session 1 quiz via the editor API.",
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
            update_quiz(client, quiz_id)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
