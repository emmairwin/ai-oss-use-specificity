# Prototype run 1 — 2026-08-22

First end-to-end execution of the agent. Three cases, one run each, run
concurrently. Digest of grids and substantive notes; not a verbatim paste of
the three full reports.

## Results vs. expected

| Case | Target | Expected | Got | Match |
|---|---|---|---|---|
| A | AFNix `docs.afnix.fr/policies/ai.html` | 1 partial, 8 no | **1 yes, 0 partial, 8 no** | domains ✓ / one attribute ✗ |
| B | `chaoss/wg-ai-alignment` @ `36f2bb3` | 9 no | **9 no** | ✓ exact |
| C | `forgejo/governance` @ `1926448` | 4 yes, 0 partial, 5 no | **4 yes, 0 partial, 5 no** | ✓ exact, every row |

Nine domains × three cases = 27 rows. **26 matched.** The single divergence is
an attribute flag, not a domain score.

## Case A — AFNix

Grid: Code `yes`; all eight others `no`.

**Leakage test passed.** The operative noun is "contributions", naming no
domain. The agent attributed it to Code only and said so explicitly: "It was
deliberately not propagated to Content, Review, Moderation or Agentic use,
even though each could arguably be read into 'contributions.' Eight `no` rows
follow from that single decision."

**Both planted traps caught:**

- *"content" as false friend* — the phrase "AI generated content" appears four
  times, but denotes generated output in general, not the Content domain's
  artifacts. Domain 3 scored `no` despite the keyword density.
- *"speech to text"* — not counted as domain 2. Correctly read as an
  accessibility carve-out for an author composing their own work, naming no
  meeting or recording. This trap was not flagged in advance; the agent found
  it unprompted.

**The one divergence — accountability.** Scored `true` (¶3 names maintainers
and Board as enforcers; ¶4 attaches consequences to the contributor), which
lifts Code from `partial` to `yes`. Draft ground truth predicted `false` on
the grounds that enforcement structure is not authorship accountability.

Both readings are defensible, which means the metric is underdetermined here.
See "What this run changed" below.

**Self-flagged instability:** domain 5. "AI assisting as part of static
analysis or debugging workflows" could read as review-adjacent; scored `no`
because it sits in the paragraph governing what a *contributor* may use. The
agent named this as the one contestable row and predicted a second assessor
could score it `partial`. Worth a second run to see if it holds.

## Case B — chaoss/wg-ai-alignment

Grid: 9 `no`.

**Category-error test passed**, which was the point of this case. 386 lines of
domain-specific AI language sit in `metrics/`, and none of it was attributed.
The agent's reasoning: every line "describes how to assess someone else's
policy… a definition is not a provision." The ~55 policies linked from
`moderation/README.md` were excluded for the same reason — counting them
"would produce a near-perfect grid measuring the wrong repository entirely."

It also excluded `.claude/agents/chaoss-specificity.md` — its own definition —
as untracked and binding no contributor. Not anticipated.

**Inherited coverage checked and negative**, matching the manual check.

**Incidental finding:** `CONTRIBUTING.md:5` links to
`http://github.com/chaoss/community/CONTRIBUTING.md`, which is not a valid
GitHub blob URL and 404s for a human. Missing `/blob/main/`. Worth fixing.

**Unusual observation:** no rationale either. Most projects without AI rules
still cite energy, water or training-data concerns as reasons. Here those
appear only as measurement targets. Genuinely nothing yet — which is the
distinction `no` was chosen to preserve over the retired "silent".

## Case C — forgejo/governance

Grid: Code, Content, Review, Agentic `yes`; Notetaker, Moderation,
Environmental, Infrastructure, Training `no`.

Matched the predicted grid on all nine rows including every attribute flag
except where noted below. The agent enumerated the full governance tree via
the Codeberg API and read all ten Markdown policy files, plus the Code of
Conduct in the separate `forgejo/code-of-conduct` repo.

**Rationale rule applied correctly, and more sharply than expected.** Domain 9
scored `no`. Footnote 1 — "it is almost impossible to ascertain whether output
of an AI does not violate somebody else's copyright" — was read as "a concern
about the provenance of third-party models' training data, not a rule about
Forgejo's own data." That distinction is finer than the rule as written and is
worth folding back into the agent definition.

**Enforcement hook found and correctly not counted.** The Code of Conduct
lists "Using AI in a way that goes against the Forgejo AI Agreement" among
unacceptable behaviours. The agent called this "a genuine strength worth
reporting" but declined to score it as Moderation coverage, since it is
enforcement of the policy rather than a rule about AI performing moderation.
Correct, and the kind of call that separates a useful report from a flattering
one.

**Self-flagged instability:** scope on domain 6. Scope was awarded for
delineating *kind* of use rather than volume. Clause 5's general-vs-narrow AI
distinction and clause 4's translation carve-out are strong; clause 6's
enumeration of "vibe coding" and "agent mode" is weaker. A stricter reading of
scope as volume-only would drop Agentic to `partial`.

**The domain-2 finding, made concrete.** Forgejo's governance repo stores
`records/**` — mp3 recordings of governance videoconferences — and
`DECISION-MAKING.md` §3.7 describes holding real-time Matrix/Jitsi meetings.
No rule anywhere governs AI recording or transcription of them.

So the project with the most sophisticated per-domain AI policy in the
24-policy survey records its own meetings and has no policy about AI doing so.
That is the metric's founding claim, demonstrated in its own best case rather
than argued.

## What this run changed

**1. The accountability attribute is underdefined in the metric.**
`ai-use-consent-policy-specificity.md` says only "Who holds accountability."
That does not distinguish:

- **authorship accountability** — who is answerable for the AI-assisted output
  (Forgejo clause 3: "The accountability of using AI in a contribution lies
  with the person that makes that contribution")
- **enforcement accountability** — who upholds the policy and who bears
  consequences (AFNix ¶3–¶4)

AFNix has the second without the first. Which one counts decides `partial` vs
`yes`, and it will move rows on nearly every project scored. This needs a
one-line decision in the metric definition, then a matching sentence in the
agent.

**2. The rationale rule held, and wants refining.** It worked on Forgejo
domain 9, but the agent drew a finer line than the rule states — rationale
about *third-party* training data vs. a rule about *the project's own* data.
Fold that distinction in.

**3. Scope needs a definition.** Both A and C flagged scope as their least
stable attribute. The metric says "Scope or volume limits"; the agent has been
reading kind-of-use carve-outs as scope. Decide whether an exemption ("we
exclude machine translation") is a scope limit or something else. This governs
four rows in Case C alone.

**4. Two eval-set corrections for `moderation/README.md`.** curl's entry points
at a `security.txt` with no AI statement; QGIS QEP-408 is a self-described
"quasi direct adaptation" of the LLVM policy. See
[`policy-survey.md`](../policy-survey.md).

## Verdict

The two failure modes that produce confident-wrong output — leakage and
category error — did not occur in any of the three cases, and the agent caught
one trap unprompted. Every remaining disagreement is a place where the *metric*
is ambiguous, not where the agent is wrong.

That is the useful outcome from a prototype: it turned three underspecified
definitions into three concrete decisions.
