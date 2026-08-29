# Agent vs. hand grades

Compares what the agent said about a repo against what a human says, so
somebody can tell whether any of the agent's output is right.

Requires Python 3.10+ and `requests` (used only to resolve a commit SHA;
`compare.py` never touches the network).

## 1. Generate a template

```bash
python grade.py new chaoss/wg-ai-alignment
```

Writes `grades/chaoss__wg-ai-alignment.json` with all nine domains set to
`null`, and fills `commit_sha` with the repo's current HEAD so a later policy
change doesn't silently invalidate your grade. If GitHub is unreachable the
SHA is left empty and you'll be told — fill it in by hand.

For a second grader on the same repo:

```bash
python grade.py new chaoss/wg-ai-alignment --grader emma
```

## 2. Fill it in

Read the repo's policy and set each domain to `yes`, `no`, or `partial`. Add a
`note` saying why — the notes are printed next to every disagreement and are
usually what explains it.

Set `graded_by` and `graded_at` too. `graded_by` is what keys a grader; without
it the filename is used.

> **Do not let a model fill these in.** They are the only independent
> measurement in this system. If they come from a model, the comparison is the
> agent checking its own work and the numbers mean nothing.

Check what's outstanding:

```bash
python grade.py check
```

Reports unset domains per file, invalid values (a typo like `"Yes"` would
otherwise silently drop that row from the comparison), and empty metadata.

## 3. Compare

```bash
python compare.py chaoss_report.json
```

Takes one or more agent reports — the JSON `chaoss_agent.py` already writes.
Reads every completed grade file from `grades/`, matches on the `repo` field,
and writes a dated JSON artifact plus a text summary to `comparisons/`.

## Reading the output

**Human-to-human agreement comes first**, and it bounds everything below it. If
two people reading the same policy disagree on a domain, the agent can't be
expected to do better. Those domains are flagged `taxonomy_ambiguous` and
excluded from the agent comparison — they're a finding for the CHAOSS working
group about the metric's wording, not a bug in the agent.

With only one grader per repo there's no human baseline, and the tool says so.
A second grader on even one repo tells you how much of the disagreement is the
agent and how much is the taxonomy.

**Direction matters more than the rate.** Two counts, never averaged:

- `too_generous` — the agent claimed more coverage than the human found
- `too_harsh` — the agent claimed less

A tool that is 80% accurate and skews generous is a different problem from one
that is 80% accurate and scatters. The first is inventing coverage that isn't
there, which is the failure this metric exists to prevent. Ordering is
`no` < `partial` < `yes`, so a `partial` where the human said `yes` counts as
mildly harsh, not as a wash.

**The per-domain table** shows where disagreement concentrates. Expect it in
the domains a general statement could be stretched to cover — content, review,
moderation.

**The disagreement list is the actual output.** Each entry gives the domain,
both verdicts, your note, and the agent's quote with `file:line`. The
percentages are a summary of that list; the list is where you find out whether
the agent is wrong or the metric is.

## What counts as a result

If agreement is poor, that is the finding. Don't adjust the comparison to be
kinder.

After two rounds of prompt fixes, if agreement is still under roughly 60% or
still skews strongly generous, report it: this judgement may not be reliably
automatable in its current form. That is a legitimate answer, not a failure to
tune hard enough.

## Files

| | |
|---|---|
| `grade.py` | template generation, completeness check |
| `compare.py` | comparison; deterministic, offline, no model calls |
| `grades/` | your grade files, one per repo per grader |
| `comparisons/` | dated JSON + text output |
