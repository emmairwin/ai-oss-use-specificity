"""
Hand-grading templates for CHAOSS Consent Policy Specificity.

    python grade.py new chaoss/wg-ai-alignment
    python grade.py new chaoss/wg-ai-alignment --grader emma
    python grade.py check

Writes grades/<owner>__<name>.json with every domain set to null.

The `addressed` values are yours. Do not let a model fill them in — they are
the only independent measurement in this system, and if they come from a model
the comparison is the agent checking its own work.
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

GH = "https://api.github.com"

# Keys must match the agent's schema exactly (chaoss_agent.py DOMAINS).
DOMAINS = [
    "code_contributions",
    "notetaker_bots",
    "content",
    "moderation",
    "review",
    "autonomous",
    "environmental",
    "infrastructure",
    "training_data",
]

VALID = {"yes", "no", "partial"}


def grade_filename(slug: str, grader: str | None = None) -> str:
    """grades/<owner>__<name>.json, or __<grader> appended for a second pass."""
    try:
        owner, name = slug.split("/")
    except ValueError:
        raise SystemExit(f"repo must be owner/name, got: {slug}")
    base = f"{owner}__{name}"
    if grader:
        base += "__" + re.sub(r"[^a-z0-9]+", "-", grader.lower()).strip("-")
    return base + ".json"


def head_sha(slug: str) -> str:
    """Current HEAD, so a later policy change doesn't silently invalidate the
    grade. Empty string if unreachable — the template is still usable."""
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(f"{GH}/repos/{slug}/commits",
                         params={"per_page": 1}, headers=headers, timeout=30)
        r.raise_for_status()
        commits = r.json()
        return commits[0]["sha"] if commits else ""
    except Exception as e:
        print(f"warning: could not resolve HEAD for {slug} ({e}); "
              f"commit_sha left empty — fill it in by hand", file=sys.stderr)
        return ""


def blank_template(slug: str, grader: str, sha: str) -> dict:
    return {
        "repo": slug,
        "graded_by": grader or "",
        "graded_at": "",
        "commit_sha": sha,
        "domains": {d: {"addressed": None, "note": ""} for d in DOMAINS},
    }


def cmd_new(args) -> int:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / grade_filename(args.repo, args.grader)
    if path.exists() and not args.force:
        print(f"{path} already exists; use --force to overwrite", file=sys.stderr)
        return 1

    sha = "" if args.no_sha else head_sha(args.repo)
    path.write_text(json.dumps(blank_template(args.repo, args.grader or "", sha),
                               indent=2) + "\n", encoding="utf-8")

    print(f"wrote {path}")
    print(f"  commit_sha: {sha or '(unresolved — fill in by hand)'}")
    print(f"  set graded_by and graded_at ({date.today().isoformat()}) as you go")
    print("  addressed: yes | no | partial — your judgement, not a model's")
    return 0


def find_nulls(grade: dict) -> list[str]:
    """Domains still unset, plus any domain missing from the file entirely."""
    domains = grade.get("domains", {})
    missing = [d for d in DOMAINS if d not in domains]
    unset = [d for d in DOMAINS
             if d in domains and domains[d].get("addressed") is None]
    return missing + unset


def find_invalid(grade: dict) -> list[str]:
    """Values that aren't yes/no/partial — a typo silently drops a row from
    the comparison, so surface it here rather than at compare time."""
    bad = []
    for d, entry in grade.get("domains", {}).items():
        v = entry.get("addressed")
        if v is not None and v not in VALID:
            bad.append(f"{d}={v!r}")
    return bad


def cmd_check(args) -> int:
    out_dir = Path(args.out_dir)
    files = sorted(out_dir.glob("*.json")) if out_dir.is_dir() else []
    if not files:
        print(f"no grade files in {out_dir}/")
        return 0

    incomplete = 0
    for path in files:
        try:
            grade = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"{path.name}: INVALID JSON — {e}")
            incomplete += 1
            continue

        nulls, invalid = find_nulls(grade), find_invalid(grade)
        meta = []
        if not grade.get("graded_by"):
            meta.append("graded_by empty")
        if not grade.get("graded_at"):
            meta.append("graded_at empty")
        if not grade.get("commit_sha"):
            meta.append("commit_sha empty")

        if nulls or invalid:
            incomplete += 1
            print(f"{path.name}: {len(nulls)}/{len(DOMAINS)} unset")
            for d in nulls:
                print(f"    - {d}")
            for b in invalid:
                print(f"    ! invalid value: {b}")
        else:
            print(f"{path.name}: complete")
        for m in meta:
            print(f"    ~ {m}")

    print(f"\n{len(files) - incomplete}/{len(files)} complete")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    # Shared so --out-dir works after the subcommand, where people type it.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out-dir", default="grades")

    new = sub.add_parser("new", parents=[common],
                         help="write a blank grade template")
    new.add_argument("repo", help="owner/name")
    new.add_argument("--grader", help="grader name; needed for a second grader "
                                      "on the same repo")
    new.add_argument("--force", action="store_true", help="overwrite if it exists")
    new.add_argument("--no-sha", action="store_true", help="skip the GitHub call")
    new.set_defaults(func=cmd_new)

    chk = sub.add_parser("check", parents=[common],
                         help="report grade files with unset domains")
    chk.set_defaults(func=cmd_check)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
