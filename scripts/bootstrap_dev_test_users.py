"""
Bootstrap a set of shared **dev/test accounts** on a local ClassQuiz instance.

This is intended for teammates running their own copies of the stack so that
everyone gets the same users (Amal, Ashish, Monty, Umanga, Muhammad) with the
shared password described in the root AGENTS.md.

Usage (from repo root, with Docker stack running):

    python scripts/bootstrap_dev_test_users.py

You can override the target host with:

    CLASSQUIZ_BASE_URL   (default: http://localhost:8000)

The script is idempotent: if a user already exists, it prints a note and
moves on to the next account.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import httpx


DEFAULT_BASE_URL = "http://localhost:8000"


@dataclass
class DevUser:
    username: str
    email: str
    password: str


SHARED_PASSWORD = "DevPass123!"

DEV_USERS: list[DevUser] = [
    DevUser(username="Amal", email="amal.classquiz@gmail.com", password=SHARED_PASSWORD),
    DevUser(username="Ashish", email="ashish.classquiz@gmail.com", password=SHARED_PASSWORD),
    DevUser(username="Monty", email="monty.classquiz@gmail.com", password=SHARED_PASSWORD),
    DevUser(username="Umanga", email="umanga.classquiz@gmail.com", password=SHARED_PASSWORD),
    DevUser(username="Muhammad", email="muhammad.classquiz@gmail.com", password=SHARED_PASSWORD),
]


def create_user_if_needed(client: httpx.Client, user: DevUser) -> None:
    """
    Call /api/v1/users/create for the given user.

    Treat "already exists" errors as success so the script can be safely
    re-run on the same database.
    """

    resp = client.post(
        "/users/create",
        json={
            "username": user.username,
            "email": user.email,
            "password": user.password,
        },
    )

    if resp.status_code in (200, 201):
        print(f"Created dev user: {user.username} <{user.email}>")
        return

    text = (resp.text or "").lower()
    if resp.status_code in (400, 409) and ("already" in text or "exists" in text):
        print(f"User already exists, leaving as-is: {user.username} <{user.email}>")
        return

    # Anything else is unexpected and should be surfaced.
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - CLI helper
        raise SystemExit(
            f"Error creating user {user.username} ({user.email}): {exc.response.status_code} {exc.response.text}"
        ) from exc


def main() -> int:
    base_url = os.environ.get("CLASSQUIZ_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/api/v1"
    print(f"Using ClassQuiz API at: {base_url}")

    try:
        with httpx.Client(base_url=base_url, timeout=10.0, follow_redirects=True) as client:
            for user in DEV_USERS:
                create_user_if_needed(client, user)
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"Unexpected error while bootstrapping dev users: {exc}", file=sys.stderr)
        return 1

    print("Done. Dev/test users are available (or already existed).")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
