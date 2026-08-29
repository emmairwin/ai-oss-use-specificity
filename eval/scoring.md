# Scoring sheet

Nine domains × 3 cases × 3 runs = 81 cells.

## Per-run: correctness

For each case, compare the run's grid to `ground-truth.md`.

| Case | Run | Domains matching truth (/9) | Wrong domains | Failure type |
|------|-----|------------------------------|---------------|--------------|
| A | 1 | | | |
| A | 2 | | | |
| A | 3 | | | |
| B | 1 | | | |
| B | 2 | | | |
| B | 3 | | | |
| C | 1 | | | |
| C | 2 | | | |
| C | 3 | | | |

Failure types: `leakage` · `search-miss-as-absence` · `phantom-line` ·
`missed-real-policy` · `attribute-error` (right domain score, wrong attribute
flags).

## Across runs: stability

| # | Domain | A1/A2/A3 | B1/B2/B3 | C1/C2/C3 | Stable? |
|---|--------|----------|----------|----------|---------|
| 1 | Code contributions | | | | |
| 2 | Notetaker / meeting bots | | | | |
| 3 | Content | | | | |
| 4 | Moderation actions | | | | |
| 5 | Review | | | | |
| 6 | Autonomous / agentic use | | | | |
| 7 | Environmental impact | | | | |
| 8 | Infrastructure strain | | | | |
| 9 | Data use for training | | | | |

**Any domain that flips is a defect in the agent definition.** Go read the
criterion wording for that domain and find the ambiguity. Don't average, don't
take best-of-three, don't rerun hoping for a cleaner draw.

## Evidence integrity spot-check

Sample 5 cited `path:line` pairs per run and verify the quote is actually
there:

```bash
sed -n '<line>p' <path>
```

Any miss is disqualifying for the whole run — if one line number is invented,
you can't trust the others, and a reader who clicks through and lands on
unrelated text will discard the entire report.

## What "working well enough" looks like

This is a prototype, so this is a read-and-judge list, not a gate you have to
clear before the output counts:

- Case A returns roughly `1 partial, 8 no` — if domains it never names come
  back covered, the attribution rule is too weak
- Case B returns `9 no` — if it finds policy in the metric definitions, the
  category-error rule is too weak
- Case C finds the domains you found, and doesn't invent a `yes`
- Cited lines actually contain the quotes

Two failures matter more than the rest, because they're the ones that produce
confident wrong answers rather than obviously bad ones: **leakage** (coverage
manufactured from blanket language) and **category error** (scoring documents
*about* policy as policy). Everything else is tuning.

Scores from a prototype are drafts of the *criteria*, not measurements of the
*repo* — useful for improving the metric, not yet for telling a maintainer
where they stand.
