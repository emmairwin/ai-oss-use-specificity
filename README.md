# AI policy specificity: an evaluation

An evaluation of the CHAOSS metric
[Consent Policy Specificity](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md),
applied to the open source AI policies collected by the CHAOSS AI Alignment
working group in
[moderation/README.md](https://github.com/chaoss/wg-ai-alignment/blob/main/moderation/README.md).

**[Read the reports](reports/)**

## What the metric asks

How specifically does a community's AI policy address each domain where AI
shows up, rather than one blanket statement covering all use?

A project can be exact about code contributions and never mention notetaker
bots. That gap is what the metric is for.

Nine domains: code contributions, notetaker and meeting bots, content,
moderation actions, review, autonomous and agentic use, environmental impact,
infrastructure strain, and data use for training. Each is checked for four
attributes the metric calls consent-type attributes: a supervision level, a
scope or volume limit, who holds accountability, and a proportionality
threshold.

## What is here

One report per project, plus an [index](reports/) with a coverage matrix
across all of them.

Each report gives a nine-row grid, a verbatim quote and line reference behind
every populated cell, and a note on anything the policy raises as a reason
without setting a rule about it.

## How to read a report

`clear`, `partial` and `no` describe **what the policy says**, not whether the
project is doing the right thing. A permissive policy that states its position
precisely scores the same as a restrictive one that does. The metric measures
specificity, not strictness.

A sparse grid is the normal result. Most projects address code contributions,
many address documentation, and few address anything else.

## Status

This is an evaluation in progress, not a finished measurement.

- The readings have **not been checked against human grading**. That is the
  next step and the most important one.
- One domain has been seen to give different answers on repeated runs of the
  same policy, so treat a single report as one reading.
- Several scoring rules needed to produce a grid are not in the CHAOSS metric
  definition, which means another implementation could reach different
  conclusions from the same policies.
- The tooling that produced these reports is not published yet. It will be
  once the readings have been checked.

Corrections are welcome. Every row in the index has a link for reporting one.

## Credit

The policy collection is the work of the CHAOSS AI Alignment working group.
The metric is theirs. This repository holds one evaluation against it.
