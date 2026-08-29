# ai-oss-specificity

Point it at **any** GitHub repository and it reports how specifically that
project's AI policy addresses each of nine areas where AI shows up — rather
than whether it has one blanket statement covering everything.

Implements [Consent Policy Specificity](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md)
from the CHAOSS AI Alignment *Community Governed Use* metrics model.

## Who it's for

- **Thinking about contributing somewhere?** Check what a project's AI policy
  actually says before you invest effort in a contribution it may reject.
- **Maintaining a project?** See which areas your policy covers and which it
  doesn't.
- **Researching across projects?** Machine-readable JSON out, one repo per run.

It is not tied to any repository. You run it against whatever you want to look
at.

## Setup

**1. Install Python 3.10 or newer** — [python.org/downloads](https://www.python.org/downloads/).

**2. Get the code and its dependencies:**

```bash
git clone https://github.com/emmairwin/ai-oss-specificity.git
```

```bash
cd ai-oss-specificity && pip install -r requirements.txt
```

**3. Create your `.env`:**

```bash
cp .env.example .env
```

Then open `.env` and fill in:

```
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
```

**`ANTHROPIC_API_KEY`** is required — get one at
[console.anthropic.com](https://console.anthropic.com/). It is a paid API key,
not your Claude subscription, and each scan costs a few cents.

**`GITHUB_TOKEN`** is optional but recommended. Without it GitHub allows 60
requests an hour and a single scan can exhaust that. Create one at
[github.com/settings/tokens](https://github.com/settings/tokens) — no scopes
needed, it only reads public repos.

`.env` is gitignored. Never commit it: a key pushed to a public repo is
scraped within minutes, and the charges are yours. If you ever do commit one,
revoke it immediately rather than deleting the commit — the history is already
public by then.

Real environment variables still work and take precedence over `.env`, so CI
can set them directly without a file.

## Run it

```bash
python chaoss_agent.py go-gitea/gitea
```

Takes a minute or two, then writes two files:

- **`chaoss_report.md`** — a policy coverage matrix in the shape the metric
  asks for, with evidence quotes and suggested improvements
- **`chaoss_report.json`** — the same data, machine-readable

### Point it at exact files

By default it looks for `CONTRIBUTING`, `CODE_OF_CONDUCT` and `README` (repo
root or `.github/`), plus any file whose name declares it an AI policy —
`AI_POLICY.md`, `docs/ai-policy.md`, `.NO_AI/README.md` and so on.

If you already know where the policy lives, name it. Faster, cheaper, and it
cannot wander:

```bash
python chaoss_agent.py go-gitea/gitea --files CONTRIBUTING.md
```

```bash
python chaoss_agent.py some/project --files CONTRIBUTING.md docs/policies/ai.md
```

With `--files` the agent gets `read_file` and nothing else — it cannot browse
or search. **That changes what a `no` means**: not addressed *in those files*,
rather than not addressed in the repository. The report says so, in both
formats, so nobody reads a narrow scan as a repo-wide verdict.

The scan errors out if a named file isn't in the repo, rather than quietly
scoring nothing.

### Keeping the cost down

Most of the cost is the agent reading files, so the default filter is
deliberately tight — a wide net on a large repo turns one scan into dozens of
reads. `list_files` returns documentation files only, capped at 250.

If a project keeps its policy somewhere unusual, use `--files` rather than
widening the filter. `GOVERNANCE.md` in particular is *not* scanned by default;
name it if your project puts AI rules there.

## Reading the output


```
area                     addressed  where
code_contributions       yes        CONTRIBUTING.md:214
notetaker_bots           no         -
content                  yes        CONTRIBUTING.md:220
...

addressed:       Code contributions, Content
partial:         - none -
not addressed:   Notetaker / meeting bots, Moderation actions, Review, ...
```

**`yes`** — the policy names that area and states both a supervision level and
who is accountable for it.
**`partial`** — it names the area but leaves those open, *or* the area is only
reached by general wording that never names it.
**`no`** — the policy does not address that area.

Every `yes` and `partial` carries a **verbatim quote and a `file:line`**. Go
read it. The quote is the evidence; the label is one reading of it, and on
contested rows you may reasonably disagree.

### A grid that is mostly `no` is usually correct

Most projects address code contributions, many address documentation, and very
few address anything else. Across 28 published policies surveyed, exactly one
mentioned AI in meetings. Sparse output is the normal result, not a failure to
find something.

### Things it deliberately will not do

- **It won't spread a blanket sentence across areas.** "AI-assisted
  contributions must be disclosed" is evidence about code contributions and
  nothing else. Statements like that are listed separately under
  `unscoped_statements`, with the areas they leave ambiguous.
- **It won't count a reason as a rule.** A project banning AI because "AI tools
  require an unreasonable amount of energy and water" has not set a policy on
  environmental impact. That is reported under `rationale_only_mention` and the
  area still scores `no`.
- **It won't treat writing *about* policy as policy.** A repo can catalogue
  other projects' AI policies and have none of its own.

### Check the quotes

`validation_problems` in the JSON lists any quote the tool could not find in
the file it cited. Empty is what you want. Line numbers are resolved by
searching the file for the quote, never guessed.

## Without an API key: the Claude Code agent

The same nine-domain assessment is also packaged as a Claude Code subagent at
[`.claude/agents/chaoss-specificity.md`](.claude/agents/chaoss-specificity.md).
Clone this repo, open Claude Code in it, and ask:

```
Use the chaoss-specificity agent to score go-gitea/gitea
```

No API key, no Python — it runs on your Claude subscription. It also reads
policies that live on a website rather than in a repo, which `chaoss_agent.py`
cannot. It prints a report rather than writing JSON, so it's the better choice
for reading one project and the worse choice for scanning many.

## Checking whether the output is right

`eval/` holds the material for testing this against human judgement:

- [`eval/GRADING.md`](eval/GRADING.md) — hand-grade a repo yourself, then compare
- `eval/grade.py` — writes a blank grading template pinned to a commit SHA
- `eval/compare.py` — agreement rate, direction of disagreement, per-domain breakdown
- [`eval/runs/prototype-run-1.md`](eval/runs/prototype-run-1.md) — first three runs
- [`eval/policy-survey.md`](eval/policy-survey.md) — 28 published policies, read by hand

The direction of disagreement matters more than the rate: a tool that skews
toward claiming coverage that isn't there is a different problem from one that
scatters, and `compare.py` never averages the two together.

## Known limits

- Reads what is written in the repository. A policy on a project website or in
  a foundation document the repo doesn't link is not seen.
- GitHub code search returns nothing on unindexed repos, so no matches is never
  treated as evidence that an area is unaddressed.
- Two definitions in the metric are still open — what counts as an
  "accountability holder", and whether a carve-out counts as a "scope limit".
  Both move rows between `yes` and `partial`. Neither moves anything between
  `yes` and `no`.
- Only Consent Policy Specificity and part of Use Composition are implemented.
  Policy Change, Use Compliance and Misuse report why they are not.

## Something look wrong?

The reading may be wrong, or the metric's definitions may be. Both are worth
knowing — [open an issue](https://github.com/chaoss/wg-ai-alignment/issues/new)
with the repo, the area, and the quote you'd read differently.
