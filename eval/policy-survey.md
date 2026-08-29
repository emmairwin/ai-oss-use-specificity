# Policy survey — source material for the eval set

28 policies from [`moderation/README.md`](https://github.com/chaoss/wg-ai-alignment/blob/main/moderation/README.md), read
2026-08-22 to pick eval cases and to see how the nine domains actually
distribute in the wild.

Domain numbers: 1 code · 2 notetaker/meeting · 3 content · 4 moderation ·
5 review-by-reviewer · 6 agentic · 7 environmental · 8 infrastructure ·
9 training data.

## Tally

| Policy | Domains named | # | Notes |
|---|---|---|---|
| Castle Game Engine | 1, 3, 5, 6, 9 | 5 | ~6,200 words, website not repo |
| **Forgejo** | **1, 3, 5, 6** | **4** | **repo file; per-domain supervision differs; explicit accountability clause** |
| LLVM | 1, 3, 4, 6 | 4 | docs site; source of QGIS text |
| yt-dlp | 1, 3, 5, 6 | 4 | 120 words; blanket ban, but enumerated per activity |
| Servo | 1, 3, 7, 8, 9 | 5 | 7/8/9 appear only as rationale |
| GCC | 1, 5, 6 | 3 | permits AI review "supporting human review, not replacing it" |
| Mastodon | 1, 3, 6 | 3 | explicit agent ban |
| NLnet Labs | 1, 3, 5 | 3 | explicitly *permits* AI review |
| Oxide | 1, 3, 5 | 3 | company RFD, not a project policy |
| W3C NOTE | 1, 2, 7 | 3 | **only source anywhere addressing domain 2** |
| Linux Foundation | 1, 3, 9 | 3 | foundation-level; inheritable |
| Apache SF | 1, 3, 9 | 3 | foundation-level; inheritable |
| Gentoo | 3, 7, 9 | 3 | one-sentence rule; 7/9 rationale only |
| postmarketOS | 1, 7, 8 | 3 | 7/8 rationale only |
| KDE GSoC | 1, 3 | 2 | scoped to GSoC, not the whole project |
| Ghostty | 1, 3 | 2 | bans AI-generated media specifically |
| Astropy | 1, 3 | 2 | strong on accountability |
| Jellyfin | 1, 3 | 2 | ~1,850 words, mostly domain 1 detail |
| Zulip | 1, 3 | 2 | ~1,100 words, mostly domain 1 detail |
| Gitea | 1, 3 | 2 | disclosure + accountability |
| AFNix | 1 | 1 | 160 words; single blanket sentence + exceptions. Agent re-scored domain 3 as `no` — the documentation reference is a source being summarized, not content being produced |
| SunPy | 1, 3 | 2 | 70 words, 2 sentences |
| KeePassXC | 1, 6 | 2 | disclosure for "agent-based or vibe coding" |
| scikit-learn | 1 | 1 | in CODE_OF_CONDUCT, framed as etiquette |
| Godot | 1 | 1 | discouraged + entirely-AI prohibited |
| OpenInfra | 1 | 1 | ~2,100 words, all domain 1 |
| QGIS QEP-408 | 1,3,4,5,6 | 5 | **excluded — see below** |
| curl | — | 0 | **excluded — see below** |

## Domain frequency (26 usable — QGIS and curl excluded, see below)

| Domain | Count | |
|---|---|---|
| 1 Code contributions | 25 | █████████████████████████ |
| 3 Content | 18 | ██████████████████ |
| 6 Agentic | 7 | ███████ |
| 5 Review (by reviewer) | 6 | ██████ |
| 7 Environmental | 5 | █████ — all 5 rationale-only |
| 9 Training data | 5 | █████ — 3 of 5 rationale-only |
| 8 Infrastructure | 2 | ██ — both rationale-only |
| 4 Moderation | 1 | █ |
| **2 Notetaker / meeting** | **1** | **█** |

Full per-policy grid and the findings written up for publication:
[`policy-coverage-report.md`](https://github.com/chaoss/wg-ai-alignment/blob/main/notes/ai-policy-coverage-2026-08.md).

## Findings that matter for the metric

### Domain 2 is a near-total blank

One source out of 28 addresses notetaker/meeting bots — the **W3C NOTE on
LLMs in Standards Work**, and even that is a standards-body guidance document
rather than a project's contribution policy. **Zero project repositories in
the list address it.**

This is strong empirical support for the metric's founding premise: "A project
can be highly specific about code contributions and not mention notetaker
bots; that gap is what this metric surfaces." The gap is not hypothetical and
it is not marginal — it is close to universal.

It also means **no repo-based Case C can score `yes` on domain 2.** The
correct grid for the best per-domain policy available still has a `no` there.

### Rationale is not the same as provision — and the agent has no rule for it

Servo, Gentoo, postmarketOS and KDE all invoke energy and water use,
infrastructure load, or training-data copyright — but as *reasons for banning
AI*, not as *rules governing* environmental or training-data use. Servo's
"AI tools require an unreasonable amount of energy and water" is a
justification for its ban; it sets no supervision level, scope, or
accountability holder for environmental impact.

Counting rationale as coverage would show domains 7/8/9 as far better governed
than they are. Not counting it would discard the only place those concerns
appear at all.

**This is unresolved, and it is the most likely cause of run-to-run flipping
on domains 7, 8 and 9.** The handoff predicted exactly this signature: "A
domain that flips between runs usually means the criterion wording is
ambiguous." It needs a decision before the eval runs, not after.

Recommendation: **rationale does not count as addressing a domain** — the
metric asks what the policy *specifies* (supervision, scope, accountability,
proportionality), and a stated concern specifies none of them. But record
rationale mentions in the assessment notes so the signal isn't lost. If you
disagree, the fix is one paragraph in the agent definition; what matters is
that it be written down either way.

### Domain 5 is the sharpest discriminator

Whether maintainers may use AI *to review* splits cleanly, and in both
directions:

- **Forbidden** — Forgejo: "Using general AI for review is forbidden."
- **Permitted** — NLnet Labs: "Your use of LLMs for linting, analysis or
  review is permitted under this policy."
- **Permitted with limits** — GCC: "patch review (supporting human review,
  not replacing it)"
- **Banned when unsupervised** — LLVM: automated review tools that publish
  comments without human review are not allowed

A policy addressing domain 1 tells you nothing about its domain 5 position.
Good evidence for keeping them as separate domains.

## Two entries excluded

**QGIS QEP-408** — self-describes as "a quasi direct adaptation from the LLVM
software 'AI Tool Use Policy'". Its striking domain-4/5/6 coverage is LLVM's
text, down to naming the `@claude` agent. Scoring both would double-count one
policy as two independent data points. It also carries no adoption-status
line, so whether it is in force is unclear.

**curl** — the list points at `curl.se/.well-known/security.txt`, which
contains **no AI or LLM statement at all**. Either the entry is stale or the
intended target is the vulnerability-disclosure policy. Worth fixing in
`moderation/README.md`.

## Access notes

- `matplotlib.org` returned HTTP 403; not assessed.
- `devguide.python.org/getting-started/generative-ai/` returned a redirect
  stub with no policy text; not assessed.
- The W3C blog post carries no policy text — the statement lives at the
  linked `NOTE-llms-standards-20260324`. Fetching the blog alone would have
  produced a false `no` on every domain, which is the
  `search-miss-as-absence` failure in miniature.
