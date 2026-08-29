# Ground truth

> **Provisional expected grids — derived from reading the policy text, not
> from an independent human pass.**
>
> Good enough to compare a prototype run against and spot obvious breakage.
> Not good enough to call a run right or wrong on a contested row, because
> they came from the same kind of reading the agent does.
>
> Correct rows as you go; the disagreements are the interesting part. Two
> rows below are flagged as deciding a whole case — those are worth your own
> read before you trust a verdict on them.
>
> Candidates and reasoning: [`policy-survey.md`](policy-survey.md).

Record the commit SHA read. Policies change; a grid without a SHA can't be
compared to anything later.

---

## Case A — one unscoped sentence

**Repo:** AFNix — `https://docs.afnix.fr/policies/ai.html`
**SHA read:** `<fill in>`
**Policy files read:** `<fill in>`

**The sentence, verbatim:**
> AFNix hosted projects do not allow any contributions which are believed to
> include AI generated content, or to be derived from AI generated content.

**Expected grid: 1 partial, 8 no** — the handoff's target shape exactly.

| # | Domain | Expected | Why |
|---|--------|----------|-----|
| 1 | Code contributions | **partial** | supervision = banned. No scope, no accountability holder, no proportionality → one attribute only |
| 2 | Notetaker / meeting bots | no | not named |
| 3 | Content | no | **see trap below** |
| 4 | Moderation actions | no | not named |
| 5 | Review | no | not named |
| 6 | Autonomous / agentic use | no | not named |
| 7 | Environmental impact | no | not named |
| 8 | Infrastructure strain | no | not named |
| 9 | Data use for training | no | not named |

**Why AFNix over Gentoo.** Gentoo is the more famous one-sentence policy, but
its blanket noun is *"content"* — colliding with the name of domain 3 — and
its rationale invokes energy, water and training-data copyright. Two sources
of ambiguity in the case that is supposed to be the cleanest. AFNix's blanket
noun is *"contributions"*, which is unambiguously general, and it carries no
environmental or training rationale. Keep Gentoo as a stress case for later.

**The trap in this case.** AFNix's exceptions mention "AI helping summarize a
documentation page to assist in developing a feature." That is a permitted
*use of AI as an aid*, not a rule about *contributing documentation*. Domain 3
is still `no`. An agent that scores Content `partial` here has confused
"documentation is mentioned" with "documentation contribution is governed" —
a subtler version of the leakage failure, and worth catching.

**Second trap.** "AFNix project maintainers are requested to uphold this
policy… contact the AFNix Board." That names who *enforces*, not who is
*accountable for AI-assisted output*. The accountability attribute stays
`false`. If the agent flips it to `true`, Code becomes `yes` and the case
fails — so this single flag decides the whole case.

---

## Case B — no AI policy

**Repo:** `chaoss/wg-ai-alignment` (this repo)
**SHA read:** `<fill in — use git rev-parse HEAD>`
**Policy files read:** `CONTRIBUTING.md` (64 lines), `README.md` (17 lines),
`.github/ISSUE_TEMPLATE/*.yml`

**Expected grid: 9 no**

**Verified 2026-08-22:**

- `CONTRIBUTING.md` — no AI-use provision. Covers ways to contribute, chairs,
  review periods, DCO. Nothing governing contributors' use of AI.
- `README.md` — describes the working group's subject matter; no policy.
- No `CODE_OF_CONDUCT.md` in this repo.
- **Inherited policy checked:** `CONTRIBUTING.md` links to
  `chaoss/community/CONTRIBUTING.md`. Fetched and confirmed: no AI-related
  content (~390 words). So there is no inherited coverage either. This is the
  check that most often turns a false `9 no` into a real finding, and here it
  came back clean.

**Why this is the hardest possible Case B — and the best one.** The repo is
*full* of AI policy: nine domains of metric definitions, a 40-entry curated
list of other projects' AI policies in `moderation/README.md`, taxonomies of
supervision levels. Every retrieval signal points at "this repo is about AI
policy."

None of it is *this project's own policy governing its own contributors*.

An agent that scores the metric definitions as policy will return a rich,
confident, entirely wrong grid. That is a category error — measuring
instrument mistaken for the thing measured — and it is the most dangerous
failure available to this agent, because the output looks authoritative.

Your own observation drives the point: this repo has no policy. Under the
retired vocabulary you'd have called that "silent," which reads as though the
group declined to speak. It didn't. It just hasn't written one yet — which is
precisely why `no` is the better term.

---

## Case C — genuinely per-domain

**Repo:** Forgejo — `codeberg.org/forgejo/governance`, `AIAgreement.md`
**SHA read:** `<fill in>`
**Policy files read:** `AIAgreement.md` (~480 words)

**Expected grid: 4 yes, 0 partial, 5 no**

Chosen over Castle Game Engine (5 domains, but 6,200 words on a website) and
LLVM (4 domains, docs site) because it is a real adopted policy living in a
repo file, and because **its supervision level genuinely differs per domain**
rather than one rule restated. That is what "per-domain" is supposed to mean.

| # | Domain | Expected | Supervision | Scope | Acct | Prop | Evidence |
|---|--------|----------|---|---|---|---|---|
| 1 | Code contributions | **yes** | banned + disclosure | ✓ | ✓ | – | "Forgejo does not accept works of authorship (code, documentation, etc.) either partially or completely generated by AI"; accountability from clause 3 |
| 2 | Notetaker / meeting bots | no | – | – | – | – | not named |
| 3 | Content | **yes** | banned | ✓ | – | – | clause 2 names documentation; clause 4 names "commit messages, pull request messages, documentation, code comments and issues" |
| 4 | Moderation actions | no | – | – | – | – | not named |
| 5 | Review | **yes** | banned | ✓ | – | – | "Using general AI for review is forbidden." Scope from the general-vs-narrow AI distinction + "If the change contains changes to the UX it has to be approved by a human reviewer." |
| 6 | Autonomous / agentic use | **yes** | banned | ✓ | – | – | "It is not allowed to use AI in an autonomous-looking way to contribute in Forgejo. This also applies when someone engages in 'vibe coding' or uses so-called 'agent mode'." |
| 7 | Environmental impact | no | – | – | – | – | not named |
| 8 | Infrastructure strain | no | – | – | – | – | not named |
| 9 | Data use for training | no | – | – | – | – | **rationale trap — see below** |

**Scope attribute, clause 4:** "We exclude machine translation and tooling
that helps with grammar and spelling check." An explicit carve-out is a scope
limit. This is what lifts domains 1 and 3 from `partial` to `yes`, so if you
judge it otherwise, say so — it changes four rows.

**Accountability, clause 3:** "The accountability of using AI in a
contribution lies with the person that makes that contribution." General
language, so under the attribution rule it lands on domain 1 only. If you
think it should distribute across every domain the policy addresses, that is
a defensible reading — but it must be written into the agent definition,
because leaving it to per-run judgement is how domains start flipping.

**The rationale trap, domain 9:** footnote 1 reads "it is almost impossible to
ascertain whether output of an AI does not violate somebody else's copyright."
That is a *reason for the ban*, not a rule about training-data use. It
specifies no supervision level, no scope, no accountability holder. Domain 9
stays `no` under the recommended rule in
[`policy-survey.md`](policy-survey.md#rationale-is-not-the-same-as-provision--and-the-agent-has-no-rule-for-it).
**Settle that rule before running.** It is currently unwritten, and it governs
domains 7, 8 and 9 across every case.

---

## A note on what the survey found

Across 24 policies, **exactly one** addresses domain 2 (notetaker / meeting
bots), and it is a W3C standards-body note, not a project contribution policy.
No repository in the list addresses it at all.

So no repo-based Case C can score `yes` on domain 2 — the best available
per-domain policy still has five `no` rows. That is not a weakness in the
eval. It is the metric's founding claim showing up in the data on the first
pass.
