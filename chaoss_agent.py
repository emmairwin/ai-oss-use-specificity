"""
Score any GitHub repo against the CHAOSS AI Alignment "Community Governed Use"
metrics model, specifically:

  Consent Policy Specificity  - agent-judged, 9 domains x 4 attributes
  Use Composition (partial)   - deterministic scan of agent/bot signals

https://github.com/chaoss/wg-ai-alignment/tree/main/metrics/ai-alignment-community-governed-use

Point it at any repository - yours, or one you are thinking about contributing
to. It is not tied to a project.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    export GITHUB_TOKEN=ghp_...
    python chaoss_agent.py chaoss/wg-ai-alignment
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import anthropic
import requests

# Load ANTHROPIC_API_KEY / GITHUB_TOKEN from a .env file if one is present.
# Optional: real environment variables still work and take precedence.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MODEL = "claude-sonnet-5"
MAX_TURNS = 30
GH = "https://api.github.com"

# --- Taxonomy, verbatim from ai-use-consent-policy-specificity.md ------------

DOMAINS = [
    ("code_contributions", "Code contributions (PRs, issues, comments)"),
    ("notetaker_bots", "Notetaker / meeting bots (recorded discussion, closed or small-group content)"),
    ("content", "Content (documentation, blogs, design assets)"),
    ("moderation", "Moderation actions"),
    ("review", "Review (who or what may review using AI)"),
    ("autonomous", "Autonomous / agentic use"),
    ("environmental", "Environmental Impact (energy use, water use, hardware/carbon footprint)"),
    ("infrastructure", "Infrastructure strain (server load, hardware cost/financing)"),
    ("training_data", "Data use for training (platform user data)"),
]

# "not_specified" rather than "silent": the metric describes what a document
# says, not whether a community chose to speak.
SUPERVISION_LEVELS = [
    "banned",
    "human_in_the_loop",
    "disclosure_required",
    "limited_unsupervised",
    "fully_unsupervised",
    "not_specified",
]


# --- GitHub access ----------------------------------------------------------

class Repo:
    def __init__(self, slug: str):
        self.slug = slug
        self.session = requests.Session()
        headers = {"Accept": "application/vnd.github+json"}
        if token := os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)
        self._cache: dict[str, str] = {}
        self.default_branch = self._get(f"/repos/{slug}").get("default_branch", "main")

    def _get(self, path: str, **params):
        for attempt in range(3):
            r = self.session.get(f"{GH}{path}", params=params, timeout=30)
            if r.status_code == 403 and "rate limit" in r.text.lower():
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError(f"rate limited on {path}")

    def head_sha(self) -> str:
        try:
            commits = self._get(f"/repos/{self.slug}/commits", per_page=1)
            return commits[0]["sha"] if commits else ""
        except (requests.HTTPError, KeyError, IndexError):
            return ""

    def tree(self) -> list[str]:
        data = self._get(f"/repos/{self.slug}/git/trees/{self.default_branch}",
                         recursive="1")
        if data.get("truncated"):
            print("warning: file tree truncated by GitHub", file=sys.stderr)
        return [n["path"] for n in data.get("tree", []) if n["type"] == "blob"]

    def read(self, path: str, max_chars: int = 40_000) -> str:
        if path in self._cache:
            return self._cache[path]
        try:
            data = self._get(f"/repos/{self.slug}/contents/{path}")
        except requests.HTTPError as e:
            return f"ERROR: could not read {path} ({e.response.status_code})"
        if isinstance(data, list):
            return f"ERROR: {path} is a directory"
        if data.get("encoding") != "base64":
            return f"ERROR: {path} is not a text file"
        text = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n...[truncated, {len(text)} chars total]"
        self._cache[path] = text
        return text

    def search(self, query: str) -> list[str]:
        try:
            data = self._get("/search/code", q=f"{query} repo:{self.slug}")
        except requests.HTTPError:
            return []
        return [i["path"] for i in data.get("items", [])[:20]]

    def commit_patch(self, sha: str, path: str) -> str:
        """Unified diff for one file in one commit, or '' if unavailable."""
        try:
            data = self._get(f"/repos/{self.slug}/commits/{sha}")
        except requests.HTTPError:
            return ""
        for f in data.get("files", []):
            if f.get("filename") == path:
                return f.get("patch", "")
        return ""

    def history(self, path: str) -> list[dict]:
        """Commits touching one file - the raw input for the Policy Change metric."""
        try:
            commits = self._get(f"/repos/{self.slug}/commits", path=path, per_page=100)
        except requests.HTTPError:
            return []
        return [{"sha": c["sha"][:8],
                 "date": c["commit"]["author"]["date"][:10],
                 "message": c["commit"]["message"].split("\n")[0]} for c in commits]


# --- Use Composition: deterministic, no model needed ------------------------

AGENT_FILES = [
    "AGENTS.md", "CLAUDE.md", ".cursorrules", ".cursor/rules",
    ".github/copilot-instructions.md", ".windsurfrules", "GEMINI.md",
    ".aider.conf.yml", ".continue/config.json",
]
# The three files that almost always carry contributor policy, at the repo root
# or under .github/. Keeping the default this tight matters: every extra
# candidate is a file the agent may read, and reading is where the tokens go.
CORE_POLICY_FILES = re.compile(
    r"^(\.github/)?(CONTRIBUTING|CODE[-_]OF[-_]CONDUCT|README)(\.[a-z]+)?$",
    re.I,
)

# A dedicated AI policy, wherever the project chose to put it.
DECLARED_AI_POLICY = re.compile(
    r"(ai[-_. ]?policy|policy[-_. ]?ai|ai[-_. ]?use|ai[-_. ]?agreement|"
    r"ai[-_. ]?tool|llm[-_. ]?polic|generative[-_. ]?ai|no[-_.]ai)",
    re.I,
)
BOT_HINT = re.compile(r"(dependabot|renovate|copilot|codex|claude|gpt|llm|"
                      r"ai-|bot\b|agent)", re.I)


def scan_composition(repo: Repo, tree: list[str]) -> dict:
    """CHAOSS Use Composition, limited to the signals it calls detectable today."""
    present = [f for f in AGENT_FILES if f in tree]
    workflows = [p for p in tree if p.startswith(".github/workflows/")]
    bot_workflows = []
    for wf in workflows[:40]:
        body = repo.read(wf, max_chars=8000)
        hits = sorted({m.group(0).lower() for m in BOT_HINT.finditer(body)})
        if hits:
            bot_workflows.append({"path": wf, "signals": hits})
    return {
        "agent_instruction_files": present,
        "workflow_count": len(workflows),
        "workflows_with_ai_or_bot_signals": bot_workflows,
        "awaiting_implementation": {
            "specific_tools_in_use": "Awaiting implementation: named-product "
                                     "detection beyond known file signatures",
            "model_type": "Awaiting implementation: underlying model/family",
            "ai_tool_owner": "Awaiting implementation: ownership and data control",
            "environmental_footprint": "Awaiting implementation: model/system card "
                                       "and ESG disclosure",
            "proportionality": "Awaiting implementation: resource use relative to "
                               "contributor count (needs platform usage data)",
        },
        "note": "Detection only. Absence of signal is not absence of use.",
    }


def candidate_policy_files(tree: list[str]) -> list[str]:
    """CONTRIBUTING, CODE_OF_CONDUCT and README, plus any file whose name
    declares it an AI policy.

    Deliberately narrow. A wide net costs real money: the agent tends to read
    what it is shown, and on a large repo a loose filter turns one scan into
    dozens of file reads. If a project keeps its policy somewhere unusual, name
    it with --files rather than widening this.
    """
    core = [p for p in tree if CORE_POLICY_FILES.match(p)]
    declared = [p for p in tree
                if DECLARED_AI_POLICY.search(p)
                and p.lower().endswith((".md", ".rst", ".txt"))]
    return sorted(set(core + declared))[:20]


# --- Agent tools ------------------------------------------------------------

TOOLS = [
    {
        "name": "list_files",
        "description": "List documentation files (.md/.rst/.txt) in the repo. Use "
                       "only if the shortlist you were given looks incomplete - it "
                       "is capped, and on a large repo it is expensive.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_file",
        "description": "Read one file's full text by exact repo-relative path.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "search_code",
        "description": "Full-text search the repo, returns matching paths. Use for "
                       "domain terms you haven't located yet, e.g. 'notetaker', "
                       "'recording', 'carbon'. May return nothing on unindexed "
                       "repos - no matches is NOT evidence that a domain is "
                       "unaddressed.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

SUBMIT = {
    "name": "submit_specificity",
    "description": "Submit the Consent Policy Specificity grid. Call exactly once, "
                   "with one entry for every domain.",
    "input_schema": {
        "type": "object",
        "properties": {
            "domains": {
                "type": "array",
                "minItems": len(DOMAINS),
                "maxItems": len(DOMAINS),
                "items": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string",
                                   "enum": [d[0] for d in DOMAINS]},
                        "supervision_level": {"type": "string",
                                              "enum": SUPERVISION_LEVELS},
                        "scope_or_volume_limits": {
                            "type": "string",
                            "description": "Stated limit, or 'not_specified'.",
                        },
                        "accountability_holder": {
                            "type": "string",
                            "description": "Who the policy makes accountable, or "
                                           "'not_specified'.",
                        },
                        "proportionality": {
                            "type": "string",
                            "description": "Stated resource-to-community-size "
                                           "threshold, or 'not_specified' / "
                                           "'not_applicable'.",
                        },
                        "addressed": {
                            "type": "string",
                            "enum": ["yes", "no", "partial"],
                            "description": "yes: the policy names this area and "
                                           "states supervision and accountability "
                                           "for it. partial: named but incomplete, "
                                           "OR reached only by general language "
                                           "that does not name it. no: the policy "
                                           "does not address it.",
                        },
                        "evidence": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "quote": {"type": "string",
                                              "description": "Verbatim excerpt, "
                                                             "under 40 words. Copy "
                                                             "exactly; line numbers "
                                                             "are resolved for you."},
                                },
                                "required": ["path", "quote"],
                            },
                        },
                        "rationale_only_mention": {
                            "type": "string",
                            "description": "If the policy raises this domain as a "
                                           "REASON for some other rule but sets no "
                                           "rule about it, quote that here and "
                                           "still score addressed='no'. Otherwise "
                                           "empty string.",
                        },
                        "suggested_improvement": {
                            "type": "string",
                            "description": "For 'no' and 'partial' only: one "
                                           "concrete sentence saying what the "
                                           "policy would need to state to close "
                                           "this gap - naming the missing "
                                           "attribute (supervision level, scope "
                                           "limit, accountability holder, or "
                                           "proportionality). Describe what is "
                                           "missing; do not prescribe how "
                                           "permissive or restrictive the rule "
                                           "should be, which is the community's "
                                           "decision. Empty string when "
                                           "addressed='yes'.",
                        },
                        "reasoning": {"type": "string"},
                    },
                    "required": ["domain", "supervision_level",
                                 "scope_or_volume_limits", "accountability_holder",
                                 "proportionality", "addressed", "evidence",
                                 "rationale_only_mention", "suggested_improvement",
                                 "reasoning"],
                },
            },
            "unscoped_statements": {
                "type": "array",
                "description": "Policy statements about AI that do not name the "
                               "domains they apply to. Each is a finding in its "
                               "own right, not a pass.",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "quote": {"type": "string",
                                  "description": "Verbatim, under 40 words"},
                        "areas_named": {
                            "type": "array",
                            "items": {"type": "string",
                                      "enum": [d[0] for d in DOMAINS]},
                            "description": "Areas this statement explicitly names.",
                        },
                        "domains_left_ambiguous": {
                            "type": "array",
                            "items": {"type": "string",
                                      "enum": [d[0] for d in DOMAINS]},
                            "description": "Areas a reader could plausibly think "
                                           "this covers but which it does not name.",
                        },
                    },
                    "required": ["path", "quote", "areas_named",
                                 "domains_left_ambiguous"],
                },
            },
            "overall_posture": {
                "type": "string",
                "description": "One-sentence roll-up of AI use posture across all "
                               "domains, as the metric permits alongside the grid.",
            },
        },
        "required": ["domains", "unscoped_statements", "overall_posture"],
    },
}

SYSTEM = f"""You apply the CHAOSS "Consent Policy Specificity" metric to a \
repository. You are measuring how specifically a community's AI policy addresses \
each domain where AI shows up, rather than one blanket statement covering all use.

The point of this metric is to surface gaps. A project can be highly specific \
about code contributions and never mention notetaker bots; that gap is the \
finding. Do not smooth it over.

Your reader is often someone deciding whether to contribute to this project. \
They need to know what the policy actually says and where, so quote accurately \
and never overstate coverage.

For each of the nine domains, determine whether the policy specifies a \
supervision level, a scope limit, an accountability holder, and where relevant a \
proportionality threshold - or does not address it.

Supervision levels, from the metric: {', '.join(SUPERVISION_LEVELS[:-1])}. \
Use "not_specified" when the policy does not address supervision for that domain.

Rules that matter more than coverage:

- Any level other than "not_specified" REQUIRES a verbatim quote from a file you \
actually opened. Never quote a file you did not read.

- A blanket AI statement covers only the domains it actually names. If a policy \
says "disclose AI use in pull requests", that is evidence for code_contributions, \
NOT for content, moderation, or notetaker bots.

- When a statement about AI does not name any domain at all - e.g. "AI-assisted \
contributions must be disclosed", where "contributions" is undefined - record it \
in unscoped_statements and list the domains it leaves ambiguous. Attribute it to \
code_contributions only. For every other domain set addressed="no". \
Never mark a domain covered on the strength of language that does not name it.

- POLICY THE PROJECT HOLDS ITSELF TO, not policy it writes about. A repository \
may contain other projects' policies, curated lists, research corpora, policy \
templates it publishes for others, or metric definitions describing how to \
assess AI policy. None of that is the project's own consent policy. Before \
counting any document as evidence, ask: does this text bind contributors to this \
repository? If it describes, catalogues, proposes, or measures rather than binds, \
it is not policy. This error is more dangerous than over-broad attribution, \
because it produces a rich, confident grid measuring the wrong object.

- RATIONALE IS NOT PROVISION. Policies often justify a ban by citing energy and \
water use, strain on infrastructure, or the copyright status of training data. A \
stated concern does not address a domain; only a stated rule does. "AI tools \
require an unreasonable amount of energy and water" is a reason for a rule about \
code contributions - it sets no supervision level for environmental impact. Score \
that domain "no" and put the quote in rationale_only_mention. This applies \
hardest to environmental, infrastructure and training_data, where rationale is \
usually the only place those concerns appear.

- A domain the policy does not address is a real, reportable result. Most repos \
do not address most domains. A grid that is mostly "no" is very likely correct.

- addressed is "yes" only when the policy names the area AND states both a \
supervision level and an accountability holder for it. "partial" when it names \
the area but leaves those open, or when the area is reached only by general \
wording that does not name it. "no" when the policy does not address it.

- Judge only what is written in this repository. Not the maintainer's reputation, \
not what similar projects do, not what a project like this probably intends.

- SUGGESTED IMPROVEMENTS. For every domain scored "no" or "partial", write one \
concrete sentence naming the attribute that is missing - supervision level, \
scope limit, accountability holder, or proportionality threshold. Say what the \
policy does not state, not what it ought to permit or forbid. "The policy does \
not say whether maintainers may use AI to review contributions" is useful. \
"The project should ban AI review" is not: how permissive to be is the \
community's decision, and this metric measures specificity, not strictness. \
Leave it empty for domains scored "yes".
"""


def run(repo: Repo, shortlist: list[str], log_path: Path,
        only_files: bool = False) -> dict:
    """Score one repo.

    only_files=True means the caller named the policy files explicitly. The
    agent then gets read_file alone - it cannot browse or search - so a domain
    scored "no" means "not addressed in these files", not "not addressed in
    this repo".
    """
    client = anthropic.Anthropic()
    log = log_path.open("w", encoding="utf-8")

    def record(kind, payload):
        log.write(json.dumps({"kind": kind, "payload": payload}, default=str) + "\n")
        log.flush()

    domain_list = "\n".join(f"- {k}: {label}" for k, label in DOMAINS)

    if only_files:
        scope = (
            "Assess ONLY these files. They were named explicitly, so do not go "
            "looking for others - you have no tool to browse or search:\n"
            + "\n".join(shortlist) +
            "\n\nRead every one of them in full before scoring. Because scope "
            'is limited to these files, "no" means the domain is not addressed '
            "in them. Do not claim anything about the rest of the repository."
        )
    else:
        scope = (
            "Candidate policy files found by pre-filter (read the relevant "
            "ones; use list_files if this looks wrong):\n"
            + "\n".join(shortlist)
        )

    messages = [{
        "role": "user",
        "content": (
            f"Repository: {repo.slug} (branch {repo.default_branch})\n\n"
            f"Domains to assess:\n{domain_list}\n\n"
            f"{scope}"
            "\n\nGather evidence, then call submit_specificity."
        ),
    }]

    tools = [t for t in TOOLS if t["name"] == "read_file"] if only_files else TOOLS

    def doc_listing(_):
        """Docs only, capped. Dumping a full tree was the single biggest token
        sink - a 6,000-file repo put 6,000 paths into context in one call."""
        docs = [p for p in repo.tree()
                if p.lower().endswith((".md", ".rst", ".txt"))]
        if len(docs) > 250:
            return ("\n".join(docs[:250]) +
                    f"\n...[{len(docs)} documentation files total, truncated. "
                    f"Re-run with --files if the policy is not listed above.]")
        return "\n".join(docs)

    dispatch = {
        "list_files": doc_listing,
        "read_file": lambda a: repo.read(a["path"]),
        "search_code": lambda a: "\n".join(repo.search(a["query"])) or "No matches.",
    }

    for turn in range(MAX_TURNS):
        force = turn == MAX_TURNS - 1
        resp = client.messages.create(
            model=MODEL,
            max_tokens=12000,
            system=SYSTEM,
            tools=tools + [SUBMIT],
            tool_choice=({"type": "tool", "name": "submit_specificity"} if force
                         else {"type": "auto"}),
            messages=messages,
        )
        record("assistant", [b.model_dump() for b in resp.content])
        messages.append({"role": "assistant", "content": resp.content})

        calls = [b for b in resp.content if b.type == "tool_use"]
        if not calls:
            messages.append({"role": "user",
                             "content": "Call submit_specificity now."})
            continue

        results = []
        for call in calls:
            if call.name == "submit_specificity":
                log.close()
                return call.input
            try:
                out, err = dispatch[call.name](call.input), False
            except Exception as e:
                out, err = f"{type(e).__name__}: {e}", True
            record("tool", {"name": call.name, "input": call.input,
                            "output": out[:2000], "error": err})
            results.append({"type": "tool_result", "tool_use_id": call.id,
                            "content": out, "is_error": err})
        messages.append({"role": "user", "content": results})

    log.close()
    raise RuntimeError("hit MAX_TURNS without a report")


def locate(body: str, quote: str) -> int | None:
    """Return the 1-based line where the quote starts, or None if absent.
    Whitespace-insensitive, so wrapped markdown still matches."""
    norm = lambda t: " ".join(t.split()).lower()
    q = norm(quote)
    if not q:
        return None
    lines = body.split("\n")
    # Build normalized text plus a map from normalized position -> line number.
    flat, line_at = [], []
    for i, line in enumerate(lines, 1):
        for tok in line.split():
            flat.append(tok.lower())
            line_at.append(i)
    hay = " ".join(flat)
    pos = hay.find(q)
    if pos == -1:
        return None
    return line_at[hay.count(" ", 0, pos)]


def validate(grid: dict, repo: Repo, tree: list[str]) -> list[str]:
    """Check every domain is present, resolve each quote to a line number, and
    reject any claim whose quote is not actually in the file."""
    problems = []
    seen = {d["domain"] for d in grid["domains"]}
    for missing in {d[0] for d in DOMAINS} - seen:
        problems.append(f"{missing}: no entry returned")
    treeset = set(tree)

    def resolve(items, label):
        for ev in items:
            if ev["path"] not in treeset:
                ev["line"] = None
                problems.append(f"{label}: path not in repo - {ev['path']}")
                continue
            line = locate(repo.read(ev["path"]), ev["quote"])
            ev["line"] = line
            if line is None:
                problems.append(f"{label}: quote not found in {ev['path']}")

    for d in grid["domains"]:
        if d["addressed"] != "no" and not d["evidence"]:
            problems.append(f"{d['domain']}: addressed '{d['addressed']}' with no evidence")
        resolve(d["evidence"], d["domain"])
    for u in grid.get("unscoped_statements", []):
        resolve([u], "unscoped")
    return problems


def print_summary(grid: dict) -> None:
    labels = dict(DOMAINS)
    order = {k: i for i, (k, _) in enumerate(DOMAINS)}
    rows = sorted(grid["domains"], key=lambda x: order.get(x["domain"], 99))

    print(f"\n{'area':24} {'addressed':10} where")
    for d in rows:
        ev = d["evidence"][0] if d["evidence"] else None
        where = "-" if not ev else (
            f"{ev['path']}:{ev['line']}" if ev.get("line") else f"{ev['path']}:?")
        print(f"{d['domain']:24} {d['addressed']:10} {where}")
        for extra in d["evidence"][1:]:
            ln = extra.get("line")
            print(f"{'':24} {'':10} {extra['path']}:{ln if ln else '?'}")

    # Name the domains in each state. Counts alone make a reader re-scan the grid.
    print()
    for state, header in (("yes", "addressed"), ("partial", "partial"),
                          ("no", "not addressed")):
        names = [labels[d["domain"]].split(" (")[0]
                 for d in rows if d["addressed"] == state]
        print(f"{header + ':':16} {', '.join(names) if names else '- none -'}")

    print(f"\nposture: {grid['overall_posture']}")

    for d in rows:
        if d.get("rationale_only_mention"):
            print(f"\nraised as rationale only ({d['domain']}), not a rule:")
            print(f"  \"{d['rationale_only_mention']}\"")

    for u in grid.get("unscoped_statements", []):
        ln = u.get("line")
        print(f"\nunscoped statement: {u['path']}:{ln if ln else '?'}")
        print(f"  \"{u['quote']}\"")
        left = ", ".join(labels.get(d, d) for d in u["domains_left_ambiguous"])
        print(f"  leaves unnamed: {left or 'none'}")


def write_markdown(report: dict, path: Path) -> None:
    """Policy coverage matrix, in the shape the metric asks for:
    'a policy coverage matrix that shows which areas are clear, partial, or
    missing', with the four consent-type attributes as columns."""
    labels = dict(DOMAINS)
    order = {k: i for i, (k, _) in enumerate(DOMAINS)}
    grid = report["consent_policy_specificity"]
    rows = sorted(grid["domains"], key=lambda x: order.get(x["domain"], 99))
    tick = lambda v: "–" if not v or v.lower() in {"not_specified",
                                                  "not_applicable"} else "✓"
    L = []
    w = L.append

    w(f"# AI policy coverage — {report['repo']}")
    w("")
    w("**Metric:** [Consent Policy Specificity](https://github.com/chaoss/"
      "wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/"
      "ai-use-consent-policy-specificity.md) "
      "· CHAOSS AI Alignment, *Community Governed Use*")
    if report.get("commit_sha"):
        w(f"**Commit:** `{report['commit_sha']}`")
    scope = report.get("scope", {})
    w(f"**Files assessed:** {', '.join(f'`{f}`' for f in scope.get('files_assessed', [])) or '—'}")
    if scope.get("mode") == "named_files":
        w("")
        w("> Scope was limited to the files named above, so **not addressed** "
          "here means *not addressed in those files* — not that the project is "
          "silent repository-wide.")
    w("")

    w("## Coverage matrix")
    w("")
    w("| Domain | Addressed | Supervision | Scope | Accountability | Proportionality |")
    w("|---|---|---|:-:|:-:|:-:|")
    for d in rows:
        sup = d["supervision_level"]
        sup_cell = "–" if sup == "not_specified" else f"`{sup}`"
        w(f"| {labels[d['domain']].split(' (')[0]} | **{d['addressed']}** | "
          f"{sup_cell} | {tick(d['scope_or_volume_limits'])} | "
          f"{tick(d['accountability_holder'])} | {tick(d['proportionality'])} |")
    w("")

    for state, header in (("yes", "Addressed"), ("partial", "Partial"),
                          ("no", "Not addressed")):
        names = [labels[d["domain"]].split(" (")[0]
                 for d in rows if d["addressed"] == state]
        w(f"**{header} ({len(names)}):** {', '.join(names) if names else '— none —'}")
    w("")
    w(f"**Overall posture:** {grid['overall_posture']}")
    w("")

    w("## Evidence")
    w("")
    for d in rows:
        w(f"### {labels[d['domain']]} — {d['addressed']}")
        for ev in d["evidence"]:
            loc = f"{ev['path']}:{ev['line']}" if ev.get("line") else ev["path"]
            w(f"> {ev['quote']}")
            w("")
            w(f"`{loc}`")
            w("")
        if d.get("rationale_only_mention"):
            w(f"*Raised as rationale for another rule, not as a rule about this "
              f"domain:* “{d['rationale_only_mention']}”")
            w("")
        if not d["evidence"] and not d.get("rationale_only_mention"):
            w(f"{d['reasoning']}")
            w("")

    gaps = [d for d in rows if d["addressed"] != "yes"
            and d.get("suggested_improvement")]
    if gaps:
        w("## Suggested improvements")
        w("")
        w("What the policy would need to state to close each gap. These describe "
          "*missing specificity*, not a recommended position — how permissive or "
          "restrictive to be is the community's decision.")
        w("")
        for d in gaps:
            w(f"- **{labels[d['domain']].split(' (')[0]}** "
              f"({d['addressed']}) — {d['suggested_improvement']}")
        w("")

    unscoped = grid.get("unscoped_statements", [])
    if unscoped:
        w("## Blanket statements")
        w("")
        w("Statements about AI that do not name the areas they apply to. Each is "
          "a finding in its own right: a reader may assume coverage the wording "
          "does not actually provide.")
        w("")
        for u in unscoped:
            loc = f"{u['path']}:{u['line']}" if u.get("line") else u["path"]
            w(f"> {u['quote']}")
            w("")
            w(f"`{loc}` — names: "
              f"{', '.join(labels[a].split(' (')[0] for a in u['areas_named']) or 'nothing specific'}"
              f"; leaves ambiguous: "
              f"{', '.join(labels[a].split(' (')[0] for a in u['domains_left_ambiguous']) or 'nothing'}")
            w("")

    if report.get("validation_problems"):
        w("## Validation problems")
        w("")
        for prob in report["validation_problems"]:
            w(f"- {prob}")
        w("")

    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(
        description="Score any GitHub repo for AI policy specificity.")
    p.add_argument("repo", help="owner/name")
    p.add_argument("--files", nargs="+", metavar="PATH",
                   help="Assess only these files instead of searching the repo. "
                        "Paths are repo-relative, e.g. --files CONTRIBUTING.md "
                        "docs/ai-policy.md. Scoring is then confined to them.")
    p.add_argument("--out", default="chaoss_report.json",
                   help="JSON output path (default: chaoss_report.json)")
    p.add_argument("--md", metavar="PATH",
                   help="Markdown coverage-matrix report path "
                        "(default: alongside --out, with a .md suffix)")
    p.add_argument("--skip-composition", action="store_true")
    args = p.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. See README.md.")

    repo = Repo(args.repo)
    tree = repo.tree()

    if args.files:
        missing = [f for f in args.files if f not in set(tree)]
        if missing:
            sys.exit(f"not in {args.repo} on branch {repo.default_branch}: "
                     + ", ".join(missing))
        shortlist = list(args.files)
        print(f"{len(tree)} files in repo; assessing {len(shortlist)} named "
              f"file(s) only", file=sys.stderr)
    else:
        shortlist = candidate_policy_files(tree)
        print(f"{len(tree)} files, {len(shortlist)} policy candidates",
              file=sys.stderr)
        if not shortlist:
            sys.exit("no policy candidates found. Name the files yourself with "
                     "--files if you know where the policy is.")

    grid = run(repo, shortlist, Path("transcript.jsonl"),
               only_files=bool(args.files))
    problems = validate(grid, repo, tree)

    report = {
        "repo": args.repo,
        "commit_sha": repo.head_sha(),
        "metric_model": "CHAOSS AI Alignment - Community Governed Use",
        # How the files were chosen changes what "no" means, so record it.
        "scope": {
            "mode": "named_files" if args.files else "repo_search",
            "files_assessed": shortlist,
            "note": ("Scoring confined to the files named on the command line; "
                     "'no' means not addressed in those files."
                     if args.files else
                     "Files chosen by pre-filter over the whole repo tree."),
        },
        "consent_policy_specificity": grid,
        "validation_problems": problems,
    }
    if not args.skip_composition:
        report["use_composition_partial"] = scan_composition(repo, tree)
    report["policy_change"] = {
        "status": "Awaiting implementation: Policy Change",
        "blocker": "Draft classifier not wired in or validated against hand-graded "
                   "history. Repo.history() and Repo.commit_patch() supply the diffs.",
    }
    report["use_compliance"] = {
        "status": "Awaiting implementation: Use Compliance",
        "blocker": "Derived metric. Requires disclosed-use data (Use Composition) "
                   "checked against the specificity grid. Composition is only "
                   "partially detectable, so the comparison is not yet sound.",
    }
    report["misuse"] = {
        "status": "Awaiting implementation: Misuse",
        "blocker": "Not automatable. CHAOSS marks the core signals unknown: text-"
                   "based AI detectors are unreliable, and license-laundering and "
                   "wrongful-accusation incidents need maintainer self-report.",
    }
    out_json = Path(args.out)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_md = Path(args.md) if args.md else out_json.with_suffix(".md")
    write_markdown(report, out_md)

    print_summary(grid)

    if args.files:
        print("\nscope: only the files named on the command line, so "
              "'not addressed' means not addressed in those files")

    gaps = [d for d in grid["domains"]
            if d["addressed"] != "yes" and d.get("suggested_improvement")]
    if gaps:
        labels = dict(DOMAINS)
        order = {k: i for i, (k, _) in enumerate(DOMAINS)}
        print("\nsuggested improvements:")
        for d in sorted(gaps, key=lambda x: order.get(x["domain"], 99)):
            print(f"  {d['domain']} ({d['addressed']})")
            print(f"    {d['suggested_improvement']}")

    if problems:
        print(f"\n{len(problems)} validation problem(s):", file=sys.stderr)
        for prob in problems:
            print(f"  - {prob}", file=sys.stderr)
    print(f"\nreport: {out_json}")
    print(f"        {out_md}")


if __name__ == "__main__":
    main()
