"""
Compare agent output against hand grades.

    python compare.py chaoss_report.json
    python compare.py reports/*.json --grades grades --out-dir comparisons

Reads agent reports that already exist and every completed grade file, and
reports agreement, the direction of disagreement, a per-domain breakdown, and
the disagreements themselves.

No model calls. No network. Deterministic, the functions below take plain
dicts and return plain dicts so they can be unit-tested directly.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

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

# Ordinal severity. Higher means the assessor claimed more coverage.
RANK = {"no": 0, "partial": 1, "yes": 2}


# --- pure comparison logic --------------------------------------------------

def human_consensus(by_grader: dict[str, dict]) -> tuple[dict, dict]:
    """Reduce several graders on one repo to a consensus verdict per domain.

    Returns (consensus, ambiguous).

    A domain where two humans reading the same policy disagree is flagged
    `taxonomy_ambiguous` and excluded from the agent comparison. The agent
    cannot be expected to beat the humans, and the disagreement is evidence
    that the metric's wording is ambiguous rather than that either grader is
    wrong. That is a finding for the working group, not a bug in the agent.
    """
    consensus, ambiguous = {}, {}
    for domain in DOMAINS:
        votes = {g: grade[domain] for g, grade in by_grader.items()
                 if domain in grade and grade[domain] is not None}
        if not votes:
            continue
        distinct = set(votes.values())
        if len(distinct) == 1:
            consensus[domain] = next(iter(distinct))
        else:
            ambiguous[domain] = dict(votes)
    return consensus, ambiguous


def classify(human: str, agent: str) -> str:
    """agree | too_generous | too_harsh.

    too_generous: the agent claimed more coverage than the human found.
    too_harsh:    the agent claimed less.

    These are never combined. A tool that is 80% accurate and skews generous
    is a different problem from one that is 80% accurate and scatters.
    """
    if human == agent:
        return "agree"
    return "too_generous" if RANK[agent] > RANK[human] else "too_harsh"


def compare_repo(slug: str, agent: dict, by_grader: dict[str, dict],
                 notes: dict[str, dict]) -> dict:
    """Compare one repo. `agent` maps domain -> agent entry dict."""
    consensus, ambiguous = human_consensus(by_grader)

    rows, missing_from_agent = [], []
    for domain, human_verdict in consensus.items():
        entry = agent.get(domain)
        if entry is None:
            missing_from_agent.append(domain)
            continue
        agent_verdict = entry.get("addressed")
        if agent_verdict not in RANK:
            missing_from_agent.append(domain)
            continue

        evidence = entry.get("evidence") or []
        first = evidence[0] if evidence else {}
        line = first.get("line")
        rows.append({
            "domain": domain,
            "human": human_verdict,
            "agent": agent_verdict,
            "result": classify(human_verdict, agent_verdict),
            "human_note": notes.get(domain, {}).get("note", ""),
            "agent_quote": first.get("quote", ""),
            "agent_location": (
                f"{first['path']}:{line}" if first.get("path") and line
                else (first.get("path", "") or "")
            ),
            "agent_reasoning": entry.get("reasoning", ""),
        })

    compared = len(rows)
    agreed = sum(1 for r in rows if r["result"] == "agree")
    return {
        "repo": slug,
        "graders": sorted(by_grader),
        "compared": compared,
        "agreed": agreed,
        "agreement_rate": round(agreed / compared, 4) if compared else None,
        "too_generous": sum(1 for r in rows if r["result"] == "too_generous"),
        "too_harsh": sum(1 for r in rows if r["result"] == "too_harsh"),
        "taxonomy_ambiguous": ambiguous,
        "missing_from_agent": missing_from_agent,
        "rows": rows,
    }


def aggregate(results: list[dict]) -> dict:
    """Roll up across repos. Generous and harsh stay separate throughout."""
    compared = sum(r["compared"] for r in results)
    agreed = sum(r["agreed"] for r in results)

    per_domain = {d: {"compared": 0, "agreed": 0,
                      "too_generous": 0, "too_harsh": 0, "ambiguous": 0}
                  for d in DOMAINS}
    for res in results:
        for row in res["rows"]:
            slot = per_domain[row["domain"]]
            slot["compared"] += 1
            if row["result"] == "agree":
                slot["agreed"] += 1
            else:
                slot[row["result"]] += 1
        for domain in res["taxonomy_ambiguous"]:
            per_domain[domain]["ambiguous"] += 1

    for slot in per_domain.values():
        slot["agreement_rate"] = (round(slot["agreed"] / slot["compared"], 4)
                                  if slot["compared"] else None)

    return {
        "repos": len(results),
        "domains_compared": compared,
        "agreed": agreed,
        "agreement_rate": round(agreed / compared, 4) if compared else None,
        "too_generous": sum(r["too_generous"] for r in results),
        "too_harsh": sum(r["too_harsh"] for r in results),
        "taxonomy_ambiguous": sum(len(r["taxonomy_ambiguous"]) for r in results),
        "per_domain": per_domain,
    }


# --- loading ----------------------------------------------------------------

def load_agent_reports(paths: list[Path]) -> dict[str, dict]:
    """slug -> {domain: entry}. Accepts one report object or a list of them."""
    out = {}
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"skipping {path}: {e}", file=sys.stderr)
            continue
        for report in (data if isinstance(data, list) else [data]):
            slug = report.get("repo")
            grid = (report.get("consent_policy_specificity") or {}).get("domains")
            if not slug or not grid:
                print(f"skipping {path}: no repo/consent_policy_specificity",
                      file=sys.stderr)
                continue
            out[slug] = {d["domain"]: d for d in grid if "domain" in d}
    return out


def load_grades(grades_dir: Path) -> tuple[dict, dict, list]:
    """Returns (verdicts, notes, skipped).

    verdicts: slug -> grader -> {domain: verdict}
    notes:    slug -> grader -> {domain: {"note": ...}}
    """
    verdicts, notes, skipped = {}, {}, []
    if not grades_dir.is_dir():
        return verdicts, notes, skipped

    for path in sorted(grades_dir.glob("*.json")):
        try:
            grade = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            skipped.append(f"{path.name}: {e}")
            continue

        slug = grade.get("repo")
        if not slug:
            skipped.append(f"{path.name}: no repo field")
            continue

        domains = grade.get("domains", {})
        filled = {d: e.get("addressed") for d, e in domains.items()
                  if e.get("addressed") in RANK}
        if not filled:
            skipped.append(f"{path.name}: no completed domains")
            continue

        grader = grade.get("graded_by") or path.stem
        verdicts.setdefault(slug, {})[grader] = filled
        notes.setdefault(slug, {})[grader] = domains
    return verdicts, notes, skipped


# --- rendering --------------------------------------------------------------

def render_text(results: list[dict], totals: dict, skipped: list[str],
                unmatched: list[str]) -> str:
    L = []
    w = L.append

    w("CHAOSS Consent Policy Specificity, agent vs. hand grades")
    w(f"generated {datetime.now().isoformat(timespec='seconds')}")
    w("")

    # Human-to-human first: it bounds what the agent could possibly achieve.
    multi = [r for r in results if len(r["graders"]) > 1]
    if multi:
        w("HUMAN-TO-HUMAN AGREEMENT")
        w("-" * 60)
        for res in multi:
            n_amb = len(res["taxonomy_ambiguous"])
            w(f"{res['repo']}  graders: {', '.join(res['graders'])}")
            w(f"  {len(DOMAINS) - n_amb}/{len(DOMAINS)} domains agreed")
            for domain, votes in res["taxonomy_ambiguous"].items():
                detail = ", ".join(f"{g}={v}" for g, v in sorted(votes.items()))
                w(f"  ! taxonomy_ambiguous: {domain}. {detail}")
        w("")
        w("  Domains flagged taxonomy_ambiguous are excluded from the agent")
        w("  comparison below. Two people reading the same policy disagreed, so")
        w("  the metric's wording is the problem, not the agent.")
        w("")
    elif results:
        w("HUMAN-TO-HUMAN AGREEMENT")
        w("-" * 60)
        w("  Only one grader per repo, no human baseline available.")
        w("  A second grader on at least one repo would tell you how much of")
        w("  any disagreement below is the agent and how much is the taxonomy.")
        w("")

    w("OVERALL")
    w("-" * 60)
    if not totals["domains_compared"]:
        w("  Nothing to compare.")
    else:
        w(f"  repos compared      {totals['repos']}")
        w(f"  domains compared    {totals['domains_compared']}")
        w(f"  agreed              {totals['agreed']} "
          f"({totals['agreement_rate']:.0%})")
        w(f"  too generous        {totals['too_generous']}   "
          f"(agent claimed more coverage than the human found)")
        w(f"  too harsh           {totals['too_harsh']}   "
          f"(agent claimed less)")
        w(f"  taxonomy ambiguous  {totals['taxonomy_ambiguous']}   (excluded)")
        w("")
        w("  Generous and harsh are reported separately on purpose. Do not")
        w("  average them, the skew is the diagnosis, not the rate.")
    w("")

    w("PER DOMAIN")
    w("-" * 60)
    w(f"  {'domain':22} {'n':>3} {'agree':>6} {'gen':>4} {'harsh':>6} {'amb':>4}")
    for domain in DOMAINS:
        s = totals["per_domain"][domain]
        rate = f"{s['agreement_rate']:.0%}" if s["agreement_rate"] is not None else "-"
        w(f"  {domain:22} {s['compared']:>3} {rate:>6} "
          f"{s['too_generous']:>4} {s['too_harsh']:>6} {s['ambiguous']:>4}")
    w("")

    w("PER REPO")
    w("-" * 60)
    for res in results:
        rate = (f"{res['agreement_rate']:.0%}"
                if res["agreement_rate"] is not None else "-")
        w(f"  {res['repo']:40} {res['agreed']}/{res['compared']} ({rate})"
          f"  gen={res['too_generous']} harsh={res['too_harsh']}")
        if res["missing_from_agent"]:
            w(f"    missing from agent report: "
              f"{', '.join(res['missing_from_agent'])}")
    w("")

    w("DISAGREEMENTS")
    w("-" * 60)
    w("This list is the output. The percentages above summarise it.")
    w("")
    any_rows = False
    for res in results:
        bad = [r for r in res["rows"] if r["result"] != "agree"]
        if not bad:
            continue
        any_rows = True
        w(f"{res['repo']}")
        for row in bad:
            w(f"  {row['domain']}  human={row['human']}  agent={row['agent']}"
              f"  [{row['result']}]")
            if row["human_note"]:
                w(f"    human:  {row['human_note']}")
            if row["agent_quote"]:
                w(f"    agent:  \"{row['agent_quote']}\"")
            if row["agent_location"]:
                w(f"            {row['agent_location']}")
            if not row["agent_quote"] and row["agent_reasoning"]:
                w(f"    agent:  (no quote) {row['agent_reasoning'][:200]}")
            w("")
    if not any_rows:
        w("  None.")
        w("")

    if unmatched:
        w("NOT COMPARED")
        w("-" * 60)
        for line in unmatched:
            w(f"  {line}")
        w("")
    if skipped:
        w("SKIPPED GRADE FILES")
        w("-" * 60)
        for line in skipped:
            w(f"  {line}")
        w("")

    return "\n".join(L)


# --- entry point ------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("reports", nargs="+", type=Path,
                   help="agent report JSON file(s)")
    p.add_argument("--grades", type=Path, default=Path("grades"))
    p.add_argument("--out-dir", type=Path, default=Path("comparisons"))
    args = p.parse_args()

    agent = load_agent_reports(args.reports)
    verdicts, notes, skipped = load_grades(args.grades)

    if not agent:
        print("no usable agent reports", file=sys.stderr)
        return 1
    if not verdicts:
        print(f"no completed grade files in {args.grades}/. "
              f"run `grade.py check` to see what's outstanding", file=sys.stderr)
        return 1

    unmatched = []
    unmatched += [f"{slug}: graded but no agent report"
                  for slug in sorted(set(verdicts) - set(agent))]
    unmatched += [f"{slug}: agent report but no grade"
                  for slug in sorted(set(agent) - set(verdicts))]

    results = []
    for slug in sorted(set(agent) & set(verdicts)):
        # Notes come from whichever grader is alphabetically first; every
        # grader's verdict is still shown for ambiguous domains.
        first = sorted(verdicts[slug])[0]
        results.append(compare_repo(slug, agent[slug], verdicts[slug],
                                    notes[slug][first]))

    totals = aggregate(results)
    text = render_text(results, totals, skipped, unmatched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    json_path = args.out_dir / f"comparison-{stamp}.json"
    text_path = args.out_dir / f"comparison-{stamp}.txt"
    json_path.write_text(json.dumps(
        {"generated_at": datetime.now().isoformat(timespec="seconds"),
         "totals": totals, "repos": results,
         "not_compared": unmatched, "skipped_grade_files": skipped},
        indent=2) + "\n", encoding="utf-8")
    text_path.write_text(text + "\n", encoding="utf-8")

    print(text)
    print(f"\nwrote {json_path}")
    print(f"wrote {text_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
