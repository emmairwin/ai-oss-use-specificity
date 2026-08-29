# Consent Policy Specificity — eval harness

Purpose: find out whether the agent's nine-domain criteria are stable and
correct **before** any score it produces is shown to a maintainer or used in
CHAOSS work.

## How to run the agent

In a Claude Code session opened at the repo root:

```
Use the chaoss-specificity agent to score kubernetes/kubernetes
```

That's it. The agent definition lives in `.claude/agents/chaoss-specificity.md`.
No API key, no Python, no install — it runs inside your existing session.

If Claude says the agent type isn't found, the session was started before the
file existed. Exit and reopen Claude Code from the repo root and it will
register.

## The two things this eval tests

**1. Correctness** — does the grid match ground truth?

The failure mode that matters is *blanket-language leakage*: a repo says
"AI-assisted contributions must be disclosed" and the agent marks content,
moderation, review and agentic use as covered. The metric exists to surface
that gap. An agent that smooths it over produces a report worse than nothing,
because it tells a maintainer they have coverage they don't have.

**2. Stability** — does the same repo score the same way twice?

A domain that flips between runs almost always means the *criterion wording
is ambiguous*, not that the run was unlucky. Fix the wording in the agent
definition; don't average the runs.

**This is a prototype.** Run each case once, read the output, fix what's
obviously broken, run again. Repeat runs are for chasing a specific domain you
suspect is unstable — not a standing requirement before you're allowed to look
at results. You learn more from one run you actually read than from three you
tallied.

## Case design

| Case | Repo profile | Correct grid |
|---|---|---|
| A | One unscoped sentence about AI | **1 partial, 8 no** — partial on Code contributions only |
| B | No AI policy at all | **9 no** |
| C | Genuinely per-domain policy | The only case that should produce any `yes` |

Case A is the load-bearing one. If the agent returns anything other than one
`partial` and eight `no`, the domain-attribution rule isn't holding.

Case B guards the opposite error: an agent that manufactures coverage from
ambient CONTRIBUTING.md language.

Case C guards over-correction — an agent tuned so hard against leakage that it
can no longer recognise real per-domain policy when it exists.

## Recording results

Ground truth goes in `ground-truth.md` — filled in by a human who has read the
policy, **before** any agent run. Writing it after you've seen a run is how
you accidentally grade the agent against itself.

Each run goes in `runs/<case>-<n>.md` verbatim — paste the agent's output
unedited, including anything that looks wrong.

Then score with `scoring.md`.

## What a failure looks like

- **Leakage** — a domain scored `yes`/`partial` whose evidence quote never
  names that domain. Cause: the domain-attribution rule is too weak.
- **Search-miss-as-absence** — `no` justified by "no matches found" rather than by
  having read the files. Cause: the agent grepped instead of reading.
- **Phantom line numbers** — cited line doesn't contain the quote. Cause: the
  agent counted instead of using `Grep -n`.
- **Flip** — same domain, different score across the 3 runs. Cause: ambiguous
  criterion wording. This is a bug in the agent definition, not noise.

## Known limits carried over from the design handoff

- GitHub code search returns nothing on unindexed repos. **No matches must
  never be read as evidence that a domain is unaddressed.**
- Metric definitions are still being drafted — several sections read "To be
  added". Pin the commit SHA you scored against so results stay comparable.
- File-rename history is not followed, so a policy file that moved loses its
  history at the rename. Relevant to Policy Change, not to this metric.

## Terminology decision

**`silent` is not used as a term in this metric.** The third state is
`no` — "the policy does not address this domain."

The reason to avoid it: "silent" describes the *community's disposition*
rather than the *document's content*, and it carries an implication of having
chosen not to speak. A project that hasn't written an AI policy yet has not
gone quiet on the subject; it simply hasn't written one. In a metric whose
whole purpose is to help maintainers see gaps without being scolded for them,
that connotation works against the goal.

The design handoff floated **`stated / inferred / silent`** for the CHAOSS PR.
That scale is retired. Note it was never a clean substitute anyway: it mixes
two different axes — `inferred` describes *how the assessor derived a finding*,
while `partial` describes *how much the policy actually says*. The implemented
scale answers the second question, which is what the metric asks.

Still open: whether `yes / partial / no` is the right surface wording for the
published metric, or whether something like `specific / general / not
addressed` reads better in a coverage matrix a maintainer sees. That is a
labelling choice only — the three underlying states and the rule that
separates them do not change.
