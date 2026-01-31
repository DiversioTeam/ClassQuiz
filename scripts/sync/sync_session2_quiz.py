"""
Create or update the Session 2 Quiz (Python Data Model – Hard Mode)
via the ClassQuiz editor API.

This script:
1. Logs in as Monty (or a custom user via env/flags).
2. Checks if the quiz already exists by title.
3. If it exists, updates it; otherwise creates it from scratch.

Usage (from repo root, with Docker stack running):

    python scripts/sync/sync_session2_quiz.py

Override defaults via env vars or flags:

    CLASSQUIZ_BASE_URL   (default: http://localhost:8888)
    CLASSQUIZ_EMAIL      (default: monty.classquiz@gmail.com)
    CLASSQUIZ_PASSWORD   (default: DevPass123!)

    python scripts/sync/sync_session2_quiz.py --base-url https://your-host \\
        --email you@example.com --password 'secret'
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import textwrap
from typing import Any

import httpx


DEFAULT_BASE_URL = "http://localhost:8888"
DEFAULT_EMAIL = "monty.classquiz@gmail.com"
DEFAULT_PASSWORD = "DevPass123!"
QUIZ_TITLE = "Python Data Model – Session 2 Quiz (Hard Mode)"
QUIZ_DESCRIPTION = "Quick warm-up (Session 1 recap), then deep protocol puzzles from Session 2."

# Fixed seed for reproducible shuffling - change this to reshuffle all questions
SHUFFLE_SEED = 42


def _clean(text: str) -> str:
    """Normalize leading/trailing whitespace on a multi-line question."""
    return textwrap.dedent(text).strip("\n")


def build_questions() -> list[dict[str, Any]]:
    """Build all 30 Hard Mode questions for the Session 2 quiz."""

    # Track question index for deterministic shuffling
    question_counter = [0]

    def q(
        question: str,
        time: int,
        answers: list[tuple[str, bool]],
    ) -> dict[str, Any]:
        # Shuffle answers deterministically based on question number
        rng = random.Random(SHUFFLE_SEED + question_counter[0])
        question_counter[0] += 1
        shuffled_answers = answers.copy()
        rng.shuffle(shuffled_answers)

        return {
            "question": _clean(question),
            "time": str(time),
            "type": "ABCD",
            "answers": [
                {"right": is_right, "answer": text, "color": None}
                for text, is_right in shuffled_answers
            ],
            "image": None,
            "hide_results": False,
        }

    return [
        # Q1 – The Copy That Wasn't (Easy)
        q(
            """
            What does this print?

            m = [[0] * 3] * 2
            m[0][1] = 9
            print(m)
            """,
            60,
            [
                ("`[[0, 9, 0], [0, 9, 0]]`", True),
                ("`[[0, 9, 0], [0, 0, 0]]`", False),
                ("`[[0, 0, 0], [0, 9, 0]]`", False),
                ("`[[0, 9, 0]]`", False),
            ],
        ),
        # Q2 – Alias vs Copy (Easy)
        q(
            """
            What does this print?

            a = [1, 2]
            b = a
            c = a[:]

            b.append(3)
            print(a, c)
            """,
            60,
            [
                ("`[1, 2, 3] [1, 2]`", True),
                ("`[1, 2, 3] [1, 2, 3]`", False),
                ("`[1, 2] [1, 2, 3]`", False),
                ("`[1, 2] [1, 2]`", False),
            ],
        ),
        # Q3 – The Sneaky Shared List (Medium)
        q(
            """
            What does this print?

            class C:
                xs = []
                def add(self, v):
                    self.xs.append(v)

            c1 = C()
            c2 = C()

            c1.add(1)
            c2.add(2)

            print(c1.xs, c2.xs)
            """,
            75,
            [
                ("`[1, 2] [1, 2]`", True),
                ("`[1] [2]`", False),
                ("`[1, 2] [2]`", False),
                ("`[] []`", False),
            ],
        ),
        # Q4 – Shadowboxing Attributes (Medium)
        q(
            """
            What does this print?

            class C:
                xs = []

            c = C()

            c.xs.append(1)      # mutate the class list
            c.xs = ["local"]    # rebind: creates an instance attribute
            C.xs.append(2)      # mutate the class list again

            print(c.xs, C.xs)
            """,
            75,
            [
                ("`['local'] [1, 2]`", True),
                ("`[1, 2] [1, 2]`", False),
                ("`['local', 2] [1]`", False),
                ("`['local'] [2]`", False),
            ],
        ),
        # Q5 – Iterable Without __iter__ (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class W:
                def __init__(self):
                    self.data = [10, 20]

                def __getitem__(self, i):
                    print("get", i)
                    return self.data[i]

            for x in W():
                print("x", x)
            """,
            90,
            [
                ("`get 0 | x 10 | get 1 | x 20 | get 2`", True),
                ("`get 0 | get 1 | get 2`", False),
                ("`x 10 | x 20`", False),
                ("`TypeError`", False),
            ],
        ),
        # Q6 – __iter__ Returned a Liar (Hard)
        q(
            """
            What prints?

            class BadIter:
                def __iter__(self):
                    return self

            try:
                for x in BadIter():
                    print("body", x)
            except Exception as e:
                print(type(e).__name__)
            """,
            90,
            [
                ("`TypeError`", True),
                ("`StopIteration`", False),
                ("`AttributeError`", False),
                ("`body None`", False),
            ],
        ),
        # Q7 – "in" Without __contains__ (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class A:
                def __init__(self):
                    self.data = [1, 2, 3]

                def __iter__(self):
                    print("iter")
                    for x in self.data:
                        print("yield", x)
                        yield x

            class B(A):
                def __contains__(self, item):
                    print("contains")
                    return item in self.data

            print("A:", 2 in A())
            print("B:", 2 in B())
            """,
            90,
            [
                ("`iter | yield 1 | yield 2 | A: True | contains | B: True`", True),
                ("`contains | B: True | iter | yield 1 | yield 2 | A: True`", False),
                ("`iter | yield 1 | yield 2 | yield 3 | A: True | contains | B: True`", False),
                ("`A: True | B: True`", False),
            ],
        ),
        # Q8 – __contains__ Takes Priority (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class C:
                def __iter__(self):
                    print("iter")
                    yield 1

                def __contains__(self, item):
                    print("contains")
                    raise RuntimeError("boom")

            try:
                print(1 in C())
            except RuntimeError:
                print("caught")
            """,
            90,
            [
                ("`contains | caught`", True),
                ("`iter | contains | caught`", False),
                ("`iter | caught`", False),
                ("`False`", False),
            ],
        ),
        # Q9 – Slices Are Objects (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class S:
                def __getitem__(self, idx):
                    print(type(idx).__name__, idx)
                    return 0

            s = S()
            _ = s[1]
            _ = s[1:4]
            _ = s[:]
            """,
            90,
            [
                ("`int 1 | slice slice(1, 4, None) | slice slice(None, None, None)`", True),
                ("`int 1 | int 1:4 | int :`", False),
                ("`slice 1 | slice 1:4 | slice :`", False),
                ("`TypeError`", False),
            ],
        ),
        # Q10 – Truthiness: __bool__ Beats __len__ (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class W:
                def __len__(self):
                    print("len")
                    return 10

                def __bool__(self):
                    print("bool")
                    return False

            w = W()
            print(bool(w))

            if w:
                print("T")
            else:
                print("F")
            """,
            90,
            [
                ("`bool | False | bool | F`", True),
                ("`len | bool | False | F`", False),
                ("`len | 10 | bool | False | F`", False),
                ("`bool | False | len | 10 | F`", False),
            ],
        ),
        # Q11 – __bool__ Must Return bool (Medium)
        q(
            """
            What prints?

            class Bad:
                def __bool__(self):
                    return 1

            try:
                print(bool(Bad()))
            except TypeError as e:
                print(type(e).__name__)
            """,
            75,
            [
                ("`TypeError`", True),
                ("`True`", False),
                ("`1`", False),
                ("`False`", False),
            ],
        ),
        # Q12 – __len__ Must Be Non-Negative (Medium)
        q(
            """
            What prints?

            class BadLen:
                def __len__(self):
                    return -1

            try:
                print(len(BadLen()))
            except Exception as e:
                print(type(e).__name__)
            """,
            75,
            [
                ("`ValueError`", True),
                ("`-1`", False),
                ("`TypeError`", False),
                ("`0`", False),
            ],
        ),
        # Q13 – __repr__ Must Return str (Medium)
        q(
            """
            What prints?

            class BadRepr:
                def __repr__(self):
                    return b"oops"

            try:
                print(repr(BadRepr()))
            except TypeError as e:
                print(type(e).__name__)
            """,
            75,
            [
                ("`TypeError`", True),
                ("`b'oops'`", False),
                ("`'oops'`", False),
                ("`AttributeError`", False),
            ],
        ),
        # Q14 – f-strings: !r vs default (Medium)
        q(
            """
            What does this print?

            class X:
                def __repr__(self):
                    return "R"

                def __str__(self):
                    return "S"

            x = X()
            print(f"{x} {x!r}")
            """,
            75,
            [
                ("`S R`", True),
                ("`R S`", False),
                ("`S S`", False),
                ("`R R`", False),
            ],
        ),
        # Q15 – NotImplemented Is a Relay Baton (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class A:
                def __eq__(self, other):
                    print("A")
                    return NotImplemented

            class B:
                def __eq__(self, other):
                    print("B")
                    return True

            print(A() == B())
            """,
            90,
            [
                ("`A | B | True`", True),
                ("`A | True`", False),
                ("`B | True`", False),
                ("`A | B | False`", False),
            ],
        ),
        # Q16 – When Nobody Knows (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class A:
                def __eq__(self, other):
                    print("A")
                    return NotImplemented

            class B:
                def __eq__(self, other):
                    print("B")
                    return NotImplemented

            print(A() == B())
            """,
            90,
            [
                ("`A | B | False`", True),
                ("`A | B | True`", False),
                ("`A | False`", False),
                ("`TypeError`", False),
            ],
        ),
        # Q17 – NotImplemented Even On Yourself (Very Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class A:
                def __eq__(self, other):
                    print("eq")
                    return NotImplemented

            a = A()
            print(a == a)
            """,
            90,
            [
                ("`eq | eq | True`", True),
                ("`eq | True`", False),
                ("`True`", False),
                ("`eq | eq | False`", False),
            ],
        ),
        # Q18 – The Symmetry Bug (Very Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class A:
                def __eq__(self, other):
                    print("A")
                    return False  # notice: NOT NotImplemented

            class B:
                def __eq__(self, other):
                    print("B")
                    return True

            print(A() == B())
            print(B() == A())
            """,
            90,
            [
                ("`A | False | B | True`", True),
                ("`A | B | True | B | A | True`", False),
                ("`A | True | B | False`", False),
                ("`B | True | A | False`", False),
            ],
        ),
        # Q19 – Ordering Is Less Forgiving (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class L:
                def __lt__(self, other):
                    print("L<")
                    return NotImplemented

            class R:
                def __gt__(self, other):
                    print("R>")
                    return NotImplemented

            try:
                print(L() < R())
            except TypeError:
                print("TypeError")
            """,
            90,
            [
                ("`L< | R> | TypeError`", True),
                ("`L< | R> | False`", False),
                ("`L< | False`", False),
                ("`False`", False),
            ],
        ),
        # Q20 – "Why Can't I Put This In a set?" (Hard)
        q(
            """
            What prints?

            class Person:
                def __init__(self, name):
                    self.name = name

                def __eq__(self, other):
                    if not isinstance(other, Person):
                        return NotImplemented
                    return self.name == other.name

            p = Person("Ada")

            try:
                {p}
            except TypeError as e:
                print(type(e).__name__)
            """,
            90,
            [
                ("`TypeError`", True),
                ("`{'Ada'}`", False),
                ("`{Person(\"Ada\")}`", False),
                ("`None`", False),
            ],
        ),
        # Q21 – The Broken Hash Contract (Hard)
        q(
            """
            What does this print?

            class Person:
                def __init__(self, name):
                    self.name = name

                def __eq__(self, other):
                    return isinstance(other, Person) and self.name == other.name

                __hash__ = object.__hash__  # identity-based hash

            p1 = Person("Ada")
            p2 = Person("Ada")

            print(p1 == p2, len({p1, p2}))
            """,
            90,
            [
                ("`True 2`", True),
                ("`True 1`", False),
                ("`False 2`", False),
                ("`False 1`", False),
            ],
        ),
        # Q22 – Mutating a Key After Insertion (Very Hard)
        q(
            """
            What does this print?

            class Tag:
                def __init__(self, name):
                    self.name = name

                def __hash__(self):
                    return hash(self.name)

                def __eq__(self, other):
                    return isinstance(other, Tag) and self.name == other.name

            t = Tag("prod")
            s = {t}

            print(t in s)
            t.name = "dev"
            print(t in s)
            """,
            90,
            [
                ("`True` then `False`", True),
                ("`True` then `True`", False),
                ("`False` then `False`", False),
                ("`TypeError`", False),
            ],
        ),
        # Q23 – NotImplemented In Addition (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class L:
                def __add__(self, other):
                    print("L+")
                    return NotImplemented

            class R:
                def __radd__(self, other):
                    print("R+r")
                    return "ok"

            print(L() + R())
            """,
            90,
            [
                ("`L+ | R+r | ok`", True),
                ("`R+r | L+ | ok`", False),
                ("`L+ | TypeError`", False),
                ("`ok`", False),
            ],
        ),
        # Q24 – Why sum() Fails Without __radd__ (Hard)
        q(
            """
            What prints?

            class Num:
                def __init__(self, x):
                    self.x = x

                def __repr__(self):
                    return f"Num({self.x})"

                def __add__(self, other):
                    if not isinstance(other, Num):
                        return NotImplemented
                    return Num(self.x + other.x)

            try:
                print(sum([Num(1), Num(2)]))
            except TypeError as e:
                print(type(e).__name__)
            """,
            90,
            [
                ("`TypeError`", True),
                ("`Num(3)`", False),
                ("`3`", False),
                ("`NotImplemented`", False),
            ],
        ),
        # Q25 – The sum() Identity Trick (Hard)
        q(
            """
            What does this print?

            class Num:
                def __init__(self, x):
                    self.x = x

                def __repr__(self):
                    return f"Num({self.x})"

                def __add__(self, other):
                    if not isinstance(other, Num):
                        return NotImplemented
                    return Num(self.x + other.x)

                def __radd__(self, other):
                    if other == 0:      # for sum()
                        return self
                    return self.__add__(other)

            print(sum([Num(1), Num(2)]))
            """,
            90,
            [
                ("`Num(3)`", True),
                ("`3`", False),
                ("`TypeError`", False),
                ("`Num(1)`", False),
            ],
        ),
        # Q26 – Callable Objects Keep State (Medium)
        q(
            """
            What does this print?

            class Counter:
                def __init__(self):
                    self.n = 0

                def __call__(self, step=1):
                    self.n += step
                    return self.n

            c = Counter()
            print(c(), c(2), c())
            """,
            75,
            [
                ("`1 3 4`", True),
                ("`1 2 3`", False),
                ("`0 2 3`", False),
                ("`1 2 4`", False),
            ],
        ),
        # Q27 – Memoization: Same Input, Less Work (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class Cache:
                def __init__(self):
                    self.cache = {}

                def __call__(self, x):
                    if x in self.cache:
                        print("hit", x)
                        return self.cache[x]
                    print("miss", x)
                    self.cache[x] = x * x
                    return self.cache[x]

            f = Cache()
            print(f(3), f(3), f(4))
            """,
            90,
            [
                ("`miss 3 | hit 3 | miss 4 | 9 9 16`", True),
                ("`miss 3 | miss 3 | miss 4 | 9 9 16`", False),
                ("`hit 3 | hit 3 | hit 4 | 9 9 16`", False),
                ("`miss 3 | hit 3 | miss 4 | 9 16 9`", False),
            ],
        ),
        # Q28 – __exit__ Can Swallow Exceptions (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class Demo:
                def __enter__(self):
                    print("enter")
                    return "VALUE"

                def __exit__(self, exc_type, exc, tb):
                    print("exit", exc_type.__name__ if exc_type else None)
                    return True

            with Demo() as v:
                print("in", v)
                1 / 0

            print("after")
            """,
            90,
            [
                ("`enter | in VALUE | exit ZeroDivisionError | after`", True),
                ("`enter | in VALUE | ZeroDivisionError`", False),
                ("`enter | exit ZeroDivisionError | after`", False),
                ("`enter | in VALUE | exit None | after`", False),
            ],
        ),
        # Q29 – __exit__ Still Runs, But Exception Escapes (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class Demo:
                def __enter__(self):
                    print("enter")
                    return "VALUE"

                def __exit__(self, exc_type, exc, tb):
                    print("exit", exc_type.__name__ if exc_type else None)
                    return False

            try:
                with Demo() as v:
                    print("in", v)
                    1 / 0
                print("after")
            except ZeroDivisionError:
                print("crash")
            """,
            90,
            [
                ("`enter | in VALUE | exit ZeroDivisionError | crash`", True),
                ("`enter | in VALUE | crash`", False),
                ("`enter | in VALUE | exit ZeroDivisionError | after`", False),
                ("`enter | exit ZeroDivisionError | crash`", False),
            ],
        ),
        # Q30 – Two Managers, One With: Exit Order (Hard)
        q(
            """
            What is the exact output? Use `|` to represent newlines.

            class M:
                def __init__(self, name):
                    self.name = name

                def __enter__(self):
                    print("enter", self.name)
                    return self

                def __exit__(self, exc_type, exc, tb):
                    print("exit", self.name)
                    return False

            with M("A"), M("B"):
                print("body")
            """,
            90,
            [
                ("`enter A | enter B | body | exit B | exit A`", True),
                ("`enter A | enter B | body | exit A | exit B`", False),
                ("`enter A | body | enter B | exit B | exit A`", False),
                ("`enter A | enter B | exit B | exit A | body`", False),
            ],
        ),
    ]


def build_quiz_payload() -> dict[str, Any]:
    """Build the full quiz input payload."""
    return {
        "public": False,
        "title": QUIZ_TITLE,
        "description": QUIZ_DESCRIPTION,
        "cover_image": None,
        "background_color": None,
        "background_image": None,
        "questions": build_questions(),
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
    return step_data["access_token"]


def find_quiz_id(client: httpx.Client, title: str) -> str | None:
    """Find the quiz ID for the given title. Returns None if not found."""
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


def create_quiz(client: httpx.Client, quiz_input: dict[str, Any]) -> str:
    """Create a new quiz and return its ID."""
    start_resp = client.post("/editor/start", params={"edit": "false"})
    start_resp.raise_for_status()
    edit_id = start_resp.json()["token"]

    finish_resp = client.post("/editor/finish", params={"edit_id": edit_id}, json=quiz_input)
    finish_resp.raise_for_status()

    # The editor/finish endpoint returns null on success, so we need to find the quiz by title
    quiz_id = find_quiz_id(client, quiz_input["title"])
    if not quiz_id:
        raise RuntimeError("Quiz was created but could not be found by title.")
    return quiz_id


def update_quiz(client: httpx.Client, quiz_id: str, quiz_input: dict[str, Any]) -> None:
    """Update an existing quiz."""
    start_resp = client.post(
        "/editor/start",
        params={"edit": "true", "quiz_id": quiz_id},
    )
    start_resp.raise_for_status()
    edit_id = start_resp.json()["token"]

    finish_resp = client.post("/editor/finish", params={"edit_id": edit_id}, json=quiz_input)
    finish_resp.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or update the Session 2 Quiz (Hard Mode) via the editor API.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CLASSQUIZ_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for Caddy / ClassQuiz (default: http://localhost:8888)",
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
        help="Quiz UUID to update; if omitted, the quiz is located by title or created if missing.",
    )

    args = parser.parse_args()
    api_base = args.base_url.rstrip("/") + "/api/v1"

    try:
        with httpx.Client(base_url=api_base, timeout=30.0, follow_redirects=True) as client:
            print(f"Logging in as {args.email}...")
            token = login_and_get_token(client, args.email, args.password)
            client.headers["Authorization"] = f"Bearer {token}"

            quiz_input = build_quiz_payload()

            if args.quiz_id:
                quiz_id = args.quiz_id
                print(f"Updating quiz {quiz_id}...")
                update_quiz(client, quiz_id, quiz_input)
                print(f"Quiz {quiz_id} updated successfully.")
            else:
                existing_id = find_quiz_id(client, QUIZ_TITLE)
                if existing_id:
                    print(f"Found existing quiz {QUIZ_TITLE!r} with id {existing_id}")
                    print("Updating quiz...")
                    update_quiz(client, existing_id, quiz_input)
                    print(f"Quiz {existing_id} updated successfully.")
                else:
                    print(f"No quiz named {QUIZ_TITLE!r} found; creating a new one...")
                    quiz_id = create_quiz(client, quiz_input)
                    print(f"Created quiz with id {quiz_id}")

            print("Done!")

    except httpx.HTTPStatusError as exc:
        print(f"HTTP Error: {exc.response.status_code} - {exc.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
