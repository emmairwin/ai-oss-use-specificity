# What this does and does not do

Read this before trusting a number out of it.

## Implemented

**Consent Policy Specificity**, the one metric this tool measures.
[Definition](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md).

For each of nine domains it reports whether the policy states a supervision
level, a scope limit, an accountability holder, and a proportionality
threshold, with a verbatim quote and `file:line` behind every populated cell.
Quotes are verified against the file after the fact; anything that cannot be
found is listed under *Validation problems* rather than silently kept.

## Stubbed, present in the JSON, not implemented

Every report carries these keys with a `status` and a `blocker`. They are
placeholders so the output shape matches the metrics model, not measurements.

| Key | State | Why |
|---|---|---|
| `use_composition_partial` | **partial** | A deterministic scan for agent instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, …) and AI/bot signals in workflow YAML. Real, but it only covers the signals CHAOSS calls detectable today. Named tools, model family, tool ownership, environmental footprint and proportionality are all unimplemented and say so in the output. **Absence of signal is not absence of use.** |
| `policy_change` | **stub** | Needs each policy revision classified as tightening, loosening, or adding. `Repo.history()` and `Repo.commit_patch()` supply the diffs; no classifier is wired in, and none has been validated against hand-graded history. |
| `use_compliance` | **stub** | A derived metric: disclosed use checked against the specificity grid. Composition is only partially detectable, so the comparison would not be sound yet. |
| `misuse` | **stub** | Not automatable as things stand. CHAOSS marks the core signals unknown, text-based AI detectors are unreliable, and license-laundering and wrongful-accusation incidents need maintainer self-report. |

## Rules the tool applies that the metric does not define

The metric names three coverage states but never says what separates them, and
says nothing about several situations that come up constantly. These rules are
this tool's, not CHAOSS's. **Another implementation reading the same metric
would produce different grids.** They are listed here so that is visible rather
than buried in a prompt.

| Rule | What it does |
|---|---|
| **Scoring boundary** | `clear` = supervision plus at least one other attribute; `partial` = one attribute only, or coverage reached solely by general wording; `no` = not addressed. The metric defines none of this. |
| **`not_specified`** | A sixth supervision value. The metric's five all describe a stated position; there is no value for "does not address supervision here", which is the commonest case. |
| **Rationale is not provision** | A policy citing energy and water as a reason to ban AI in code has not set an environmental rule. The domain scores `no`, the quote is surfaced under `rationale_only_mention`. Without this, five projects in the catalogue would appear to govern environmental impact when none do. |
| **Lean** | `restrictive` / `permissive` where a policy shows a direction on a domain without setting a rule. Records disposition without inflating coverage. Not in the metric at all. |
| **Domain attribution** | A blanket sentence counts only for the domains it names; general wording is attributed to code contributions alone. Follows from the metric's question, but the metric does not state it as a rule. |
| **Accountability is authorship** | Naming who enforces a rule, or stating an obligation, is not naming who bears responsibility. The metric says only "who holds accountability", and this is the one attribute observed to flip between runs of the same file. |
| **Accountability is an enum** | `contributor`, `reviewer`, `maintainer`, `project`, `not_specified`. Free text gave 21 spellings of "the contributor" across 31 cells, uncomparable between projects. Maintainer stays separate because maintainers are who moderate. |
| **Maintainer burnout is moderation** | The metric scopes infrastructure strain to server load and hardware cost. Time maintainers spend triaging AI submissions is moderation load. Three of four infrastructure findings in the first corpus were misfiled under this. |
| **Training data means outbound** | The domain is platform user data: whether this project's material may train models. Worrying that models were trained on copyrighted work is a provenance concern about code contributions. All five findings in the first corpus were the inbound sense. |
| **Policy, not writing about policy** | A repository can catalogue other projects' AI policies and have none of its own. Documents that describe, propose or measure are not evidence. |

Settling these in the metric definition is what would make scores comparable
between implementations. Until then, treat output as this tool's reading.

## Known limits

- **GitHub only.** Reads the GitHub API, so Codeberg, GitLab, wikis and
  foundation websites are out of reach, about a third of the CHAOSS
  catalogue. The Claude Code agent in `.claude/agents/` handles those; it can
  fetch any URL.
- **Reads what is in the repository.** A policy on a project website, or in a
  foundation document the repo does not link, is not seen.
- **`--files` narrows what `no` means.** With it, `no` means *not addressed in
  those files*, not repository-wide. Reports say so; the index marks those rows.
- **One domain has been seen to flip** between runs of the same file
  (Servo, Content: `partial` → `clear`). Treat a single run as one reading, not
  a measurement.
- **Not validated against human grading.** `eval/` holds the harness for that
  and it has not been run. Three rows of the hand survey in
  `eval/policy-survey.md` were checked against tool runs and all three were
  wrong, in the tool's favour, which says the survey is unreliable, not that
  the tool is right.

## Cost

Roughly $0.08 per scan on `claude-sonnet-5` at $2/$10 per MTok. Every report
prints its own token count and estimate. The estimate counts cache reads at
full input rate, so it is an upper bound.
