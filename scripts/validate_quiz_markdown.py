#!/usr/bin/env python
"""
Lightweight linter for quiz Markdown files.

This script is meant as a *guideline* tool for authors: it does not enforce
rules, but highlights places where our preferred "title + code + answers"
format is not followed.

Usage:
    python scripts/validate_quiz_markdown.py quiz_data/.../sessionN_quiz.md [more_files...]

What it checks:
    - Questions that mix code-like content directly into the title line
      instead of putting it into a separate code block under the title.
    - Answer lines that look code-like but do not use backticks for
      inline code styling.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable


CODE_LIKE_TOKENS = [
    "==",
    "!=",
    ">=",
    "<=",
    " is ",
    " in ",
    " def ",
    " class ",
    " print(",
    " len(",
    "__dict__",
    "__slots__",
    "__len__",
]

CODE_LIKE_CHARS = set("[]=(){}'\"%+-,.:")


def is_code_like(text: str) -> bool:
    """Heuristic: does this look more like code/output than plain prose?"""
    if any(tok in text for tok in CODE_LIKE_TOKENS):
        return True
    if any(ch in CODE_LIKE_CHARS for ch in text):
        return True
    stripped = text.replace(" ", "")
    if stripped and all(ch.isdigit() or ch in ",.-" for ch in stripped):
        return True
    return False


def iter_questions(lines: list[str]) -> Iterable[tuple[int, list[str]]]:
    """
    Yield (start_index, block_lines) for each question-like block.

    We treat '## ' headings as question boundaries and stop on '---'
    slide separators.
    """
    n = len(lines)
    i = 0
    while i < n:
        if lines[i].startswith("## "):
            start = i
            block: list[str] = [lines[i]]
            i += 1
            while i < n and not lines[i].startswith("## "):
                if lines[i].strip() == "---":
                    break
                block.append(lines[i])
                i += 1
            yield start, block
        else:
            i += 1


def lint_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    warnings = 0

    for start_idx, block in iter_questions(lines):
        header = block[0].strip()

        # Find first non-empty line after the '##' header: that's our title.
        title = ""
        for ln in block[1:]:
            if ln.strip():
                title = ln.rstrip()
                break

        has_code_block = any(ln.strip().startswith("```") for ln in block)

        # 1) Warn if the title looks code-like but we don't have a code block.
        if title and is_code_like(title) and not has_code_block:
            print(
                f"{path}:{start_idx+1}: "
                f"title looks code-like but no code block is present – "
                f"consider moving code into a fenced block under the title.",
                file=sys.stderr,
            )
            warnings += 1

        # 2) Warn if the title mixes a lot of code with prose even when
        # a block exists – this is advisory, not fatal.
        if title and is_code_like(title) and has_code_block:
            print(
                f"{path}:{start_idx+1}: "
                f"title mixes prose and code – consider keeping the title "
                f"pure prose and moving code into the block below.",
                file=sys.stderr,
            )
            warnings += 1

        # 3) Check answers for missing backticks around code-like content.
        for offset, ln in enumerate(block, start=start_idx + 1):
            stripped = ln.lstrip()
            if not (stripped.startswith("- [") and "]" in stripped):
                continue
            # Answer text after "- [ ]" or "- [x]"
            answer_text = re.sub(r"^- \[[ xX]\]\s*", "", stripped)
            if not answer_text:
                continue
            if "`" in answer_text:
                continue  # author already opted into inline code
            if is_code_like(answer_text):
                print(
                    f"{path}:{offset}: "
                    "answer looks code-like but has no backticks – consider wrapping "
                    "the entire answer in `...`.",
                    file=sys.stderr,
                )
                warnings += 1

    if warnings == 0:
        print(f"{path}: OK")
    else:
        print(f"{path}: {warnings} warning(s)", file=sys.stderr)
    return warnings


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: python scripts/validate_quiz_markdown.py quiz_data/.../sessionN_quiz.md [...]",
            file=sys.stderr,
        )
        return 1
    total_warnings = 0
    for arg in argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f"{path}: not found", file=sys.stderr)
            continue
        total_warnings += lint_file(path)
    # Non-zero exit code is useful in CI, but fine for local use too.
    return 0 if total_warnings == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
