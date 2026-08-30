"""
Scan every target in eval/targets.txt, one after another.

    python scan_all.py                 # all of them
    python scan_all.py --dry-run       # list what would run, cost nothing
    python scan_all.py --only polars   # substring match on the repo slug

Each scan is an independent process, so one failure does not stop the rest.
Costs real money - roughly $0.08 per scan. --dry-run first.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent


def targets(path: Path) -> list[tuple[str, str]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            out.append((parts[0], parts[1]))
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, default=HERE / "eval" / "targets.txt")
    p.add_argument("--only", help="substring filter on the repo slug")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    todo = targets(args.targets)
    if args.only:
        todo = [t for t in todo if args.only.lower() in t[0].lower()]
    if not todo:
        sys.exit("nothing to scan")

    print(f"{len(todo)} target(s)")
    if args.dry_run:
        for slug, path in todo:
            print(f"  {slug} :: {path}")
        return 0

    failed = []
    start = time.monotonic()
    for i, (slug, path) in enumerate(todo, 1):
        print(f"\n{'=' * 70}\n[{i}/{len(todo)}] {slug} :: {path}\n{'=' * 70}",
              flush=True)
        r = subprocess.run(
            [sys.executable, str(HERE / "chaoss_agent.py"), slug,
             "--files", path],
            cwd=HERE)
        if r.returncode != 0:
            failed.append(slug)
            print(f"  FAILED ({r.returncode}) - continuing", flush=True)

    mins = (time.monotonic() - start) / 60
    print(f"\n{'=' * 70}")
    print(f"done: {len(todo) - len(failed)}/{len(todo)} in {mins:.1f} min")
    if failed:
        print("failed: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
