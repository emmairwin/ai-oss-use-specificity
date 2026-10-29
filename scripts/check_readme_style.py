#!/usr/bin/env python3
"""Flag long prose sentences in README files changed from a base revision."""

import argparse
import re
import subprocess
import sys
from pathlib import Path

MAX_WORDS = 30
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
SENTENCE_RE = re.compile(r'(?<=[.!?])["\'”’)]*\s+')
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def git_diff(base):
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", base, "--", "*.md"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return result.stdout


def changed_readmes(diff):
    files = {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            current = path if Path(path).name.lower() == "readme.md" else None
            if current:
                files.setdefault(current, [])
        elif line.startswith("diff --git "):
            current = None
        elif line.startswith("@@") and current:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2) or 1)
                if count:
                    files[current].append((start, start + count - 1))
    return files


def clean_markdown(text):
    text = LINK_RE.sub(r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text


def prose_blocks(lines):
    block = []
    start = None
    end = None
    in_code = False

    def flush():
        nonlocal block, start, end
        if block:
            yield start, end, " ".join(block)
        block = []
        start = None
        end = None

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            yield from flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if not stripped or stripped.startswith(("#", "|", ">", "![", "<!--", "[^")):
            yield from flush()
            continue
        line = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line)
        if start is None:
            start = number
        end = number
        block.append(line.strip())

    yield from flush()


def changed_line(start, end, ranges):
    return any(start <= changed_end and end >= changed_start for changed_start, changed_end in ranges)


def check_file(path, changed_ranges):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    findings = []
    for start, end, paragraph in prose_blocks(lines):
        if not changed_line(start, end, changed_ranges):
            continue
        for sentence in SENTENCE_RE.split(paragraph):
            words = WORD_RE.findall(clean_markdown(sentence))
            if len(words) > MAX_WORDS:
                findings.append((start, len(words)))
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Check changed README prose for sentences over 30 words."
    )
    parser.add_argument("base", help="Base Git revision to compare against")
    args = parser.parse_args()

    try:
        files = changed_readmes(git_diff(args.base))
        findings = []
        for path, ranges in files.items():
            findings.extend((path, line, count) for line, count in check_file(path, ranges))
    except (OSError, RuntimeError) as error:
        print(f"README style check failed: {error}", file=sys.stderr)
        return 2

    if findings:
        for path, line, count in findings:
            print(f"{path}:{line}: sentence has {count} words (limit: {MAX_WORDS})")
        print("Shorten the sentence or split it into smaller sentences.")
        return 1

    print(f"README style check passed: {len(files)} changed README file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
