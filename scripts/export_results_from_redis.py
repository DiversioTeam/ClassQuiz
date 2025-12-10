"""
Export quiz results for a live game directly from Redis.

This is meant as a **rescue tool** when the web UI
freezes or "Get final results" does not respond.

Usage (from repo root, with Docker stack running):

    python scripts/export_results_from_redis.py 913862

It will:
  - Read `game:{PIN}` to discover quiz title and
    number of questions.
  - Read `game_session:{PIN}:player_scores` to get
    the final point totals.
  - Read `game_session:{PIN}:{QUESTION_INDEX}` for
    each question to count correct / answered per
    player.

Output is a simple table you can paste into notes
or slides after a live session.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
DOCKER_COMPOSE_CMD = ("docker", "compose")


def _run_redis_command(args: list[str]) -> str:
    """
    Execute a redis-cli command inside the redis container
    via `docker compose exec`.

    Returns stdout as text. Any docker-compose warnings
    about docker-compose.yml are stripped out.
    """

    proc = subprocess.run(
        [*DOCKER_COMPOSE_CMD, "exec", "-T", "redis", "redis-cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"redis-cli {' '.join(args)} failed: {msg}")

    def _filter(lines: str) -> list[str]:
        out: list[str] = []
        for line in lines.splitlines():
            line = line.strip()
            if not line:
                continue
            # docker compose sometimes prints warnings like:
            # time="..." level=warning msg="...docker-compose.yml..."
            if line.startswith("time=") and "docker-compose.yml" in line:
                continue
            out.append(line)
        return out

    stdout_lines = _filter(proc.stdout)
    # We intentionally ignore stderr for normal commands; if there
    # were serious errors, returncode would be non-zero above.
    return "\n".join(stdout_lines)


def redis_get(key: str) -> str:
    """GET a single Redis key and return its value as text."""

    out = _run_redis_command(["GET", key]).strip()
    if not out or out == "nil":
        return ""
    # For simple string / JSON values, redis-cli prints the value
    # on a single line.
    return out.splitlines()[-1]


def redis_hgetall(key: str) -> dict[str, str]:
    """
    HGETALL a hash key and return it as a dict of strings.

    redis-cli prints alternating lines of field and value:
        field1
        value1
        field2
        value2
    """

    out = _run_redis_command(["HGETALL", key])
    if not out:
        return {}
    lines = out.splitlines()
    if len(lines) % 2 != 0:
        # Unexpected shape; fall back to a best-effort parse.
        # Treat the last line as a dangling value and ignore it.
        lines = lines[: len(lines) - 1]
    it = iter(lines)
    result: Dict[str, str] = {}
    for field in it:
        try:
            value = next(it)
        except StopIteration:
            break
        result[field] = value
    return result


def load_game(pin: str) -> dict:
    """Load the PlayGame JSON for a given game PIN."""

    raw = redis_get(f"game:{pin}")
    if not raw:
        raise SystemExit(f"No Redis game state found for PIN {pin}.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not decode game:{pin} JSON: {exc}") from exc


def collect_player_stats(pin: str, num_questions: int) -> dict[str, dict[str, int]]:
    """
    Scan per-question answer data and build a mapping:

        {player: {"answered": N, "right": M}}
    """

    stats: dict[str, dict[str, int]] = {}
    for index in range(num_questions):
        raw = redis_get(f"game_session:{pin}:{index}")
        if not raw:
            continue
        try:
            answers = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(answers, list):
            continue
        for entry in answers:
            if not isinstance(entry, dict):
                continue
            username = entry.get("username")
            if not username:
                continue
            right = bool(entry.get("right"))
            user_stats = stats.setdefault(username, {"answered": 0, "right": 0})
            user_stats["answered"] += 1
            if right:
                user_stats["right"] += 1
    return stats


def format_table(
    game: dict, scores: dict[str, str], per_player: dict[str, dict[str, int]]
) -> str:
    """Return a human-readable scoreboard table."""

    pin = game.get("game_pin", "<unknown>")
    title = game.get("title", "<unknown quiz>")
    num_questions = len(game.get("questions") or [])

    lines: list[str] = []
    lines.append(
        f"Game PIN {pin} – {title} ({num_questions} question{'s' if num_questions != 1 else ''})"
    )

    header = f"{'Player':<20} {'Points':>8} {'Correct':>8} {'Answered':>9}"
    lines.append(header)
    lines.append("-" * len(header))

    # Union of all player names from scores and per-question data.
    names = set(scores.keys()) | set(per_player.keys())

    def points_for(name: str) -> int:
        try:
            return int(scores.get(name, "0"))
        except ValueError:
            return 0

    sorted_names = sorted(names, key=points_for, reverse=True)

    for name in sorted_names:
        pts = points_for(name)
        s = per_player.get(name, {"answered": 0, "right": 0})
        lines.append(
            f"{name:<20} {pts:>8} {s['right']:>8} {s['answered']:>9}"
        )

    # Simple sanity hints.
    if num_questions:
        incomplete = [
            name
            for name in sorted_names
            if per_player.get(name, {}).get("answered", 0) < num_questions
        ]
        if incomplete:
            lines.append("")
            lines.append(
                "Note: some players have fewer answers recorded than the"
                f" {num_questions} questions in this game."
            )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export final standings for a live game directly from Redis.\n"
            "Use this when the web UI cannot show final results."
        )
    )
    parser.add_argument(
        "game_pin",
        help="Game PIN for the live game (e.g. 913862).",
    )
    args = parser.parse_args(argv)

    pin = args.game_pin

    try:
        game = load_game(pin)
        num_questions = len(game.get("questions") or [])
        scores = redis_hgetall(f"game_session:{pin}:player_scores")
        per_player = collect_player_stats(pin, num_questions)
        if not scores and not per_player:
            raise SystemExit(
                f"No player data found for PIN {pin}. "
                "Has the game started and at least one question been answered?"
            )
        table = format_table(game, scores, per_player)
        print(table)
        return 0
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        # Re-raise SystemExit from helpers so argparse exit codes are preserved.
        raise exc
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
