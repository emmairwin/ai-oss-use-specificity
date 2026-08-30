# AI policy coverage — go-gitea/gitea

**Metric:** [Consent Policy Specificity](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md) · CHAOSS AI Alignment, *Community Governed Use*
**Commit:** `eea03676d36fa9bf2aa8830eac28ce0eb35d6f4c`
**Files assessed:** `CONTRIBUTING.md`

> Scope was limited to the files named above, so **not addressed** here means *not addressed in those files* — not that the project is silent repository-wide.

## Coverage matrix

| Domain | Addressed | Supervision | Scope | Accountability | Proportionality |
|---|---|---|:-:|:-:|:-:|
| Code contributions | **yes** | `human_in_the_loop` | – | ✓ | – |
| Notetaker / meeting bots | **no** | – | – | – | – |
| Content | **no** | – | – | – | – |
| Moderation actions | **no** | – | – | – | – |
| Review | **no** | – | – | – | – |
| Autonomous / agentic use | **no** | – | – | – | – |
| Environmental Impact | **no** | – | – | – | – |
| Infrastructure strain | **no** | – | – | – | – |
| Data use for training | **no** | – | – | – | – |

**Addressed (1):** Code contributions
**Partial (0):** — none —
**Not addressed (8):** Notetaker / meeting bots, Content, Moderation actions, Review, Autonomous / agentic use, Environmental Impact, Infrastructure strain, Data use for training

**Overall posture:** CONTRIBUTING.md contains one specific, named AI policy — for code contributions (PRs/issues), requiring disclosure and human review/testing with contributor and maintainer accountability — while notetaker bots, content, moderation, review, autonomous/agentic use, environmental impact, infrastructure strain, and training-data use are entirely unaddressed in this file.

## Evidence

### Code contributions (PRs, issues, comments) — yes
> Contributions made with the assistance of AI tools are welcome, but contributors must use them responsibly and disclose that use clearly.

`CONTRIBUTING.md:55`

> Review AI-generated code closely before marking a pull request ready for review.

`CONTRIBUTING.md:57`

> Manually test the changes and add appropriate automated tests where feasible.

`CONTRIBUTING.md:58`

> Only use AI to assist in contributions that you understand well enough to explain, defend, and revise yourself during review.

`CONTRIBUTING.md:59`

> Disclose AI-assisted content clearly.

`CONTRIBUTING.md:60`

> Do not use AI to reply to questions about your issue or pull request.

`CONTRIBUTING.md:61`

> AI may be used to help draft issues and pull requests, but contributors remain responsible for the accuracy, completeness, and intent of what they submit.

`CONTRIBUTING.md:62`

> Maintainers reserve the right to close pull requests and issues that do not disclose AI assistance, that appear to be low-quality AI-generated content, or where the contributor cannot explain or defend the proposed changes themselves.

`CONTRIBUTING.md:64`

### Notetaker / meeting bots (recorded discussion, closed or small-group content) — no
CONTRIBUTING.md contains no mention of notetaker or meeting-recording bots, or of recorded discussion/closed-group content in any form.

### Content (documentation, blogs, design assets) — no
The AI Contribution Policy names only issues and pull requests. The separate Documentation section describes where docs live and how they are updated but does not mention AI at all, so AI use for documentation, blogs, or design assets is not addressed.

### Moderation actions — no
The Issue locking section describes moderation-like actions (locking closed/merged issue threads) but makes no mention of AI being used to perform or assist moderation. The 'Maintainers reserve the right to close...' clause is enforcement of the AI-disclosure rule, not a statement about AI being used as a moderation tool.

### Review (who or what may review using AI) — no
The 'Review AI-generated code closely before marking a pull request ready for review' instruction governs the contributor's own pre-submission check of their AI-assisted code, not who or what may use AI to perform the maintainer-side code review. The Reviewing PRs and Code review sections contain no mention of AI being used by reviewers.

### Autonomous / agentic use — no
The policy assumes a human contributor is using AI as an assistive tool ('contributors remain responsible...', 'Only use AI to assist in contributions that you understand') but does not name or address fully autonomous/agentic AI systems operating without direct human submission or action.

### Environmental Impact (energy use, water use, hardware/carbon footprint) — no
CONTRIBUTING.md contains no mention of energy use, water use, hardware footprint, or carbon impact related to AI tools, either as rationale or as rule.

### Infrastructure strain (server load, hardware cost/financing) — no
CONTRIBUTING.md does not mention infrastructure strain, server load, or hardware cost/financing in connection with AI use anywhere in the document.

### Data use for training (platform user data) — no
CONTRIBUTING.md does not address the use of Gitea's own contributor/user data (code, issues, comments) for training AI models in any form.

## Suggested improvements

What the policy would need to state to close each gap. These describe *missing specificity*, not a recommended position — how permissive or restrictive to be is the community's decision.

- **Notetaker / meeting bots** (no) — The policy would need to name meeting/discussion recording or transcription bots explicitly and state a supervision level and accountability holder for their use.
- **Content** (no) — The policy would need to state whether AI may be used for documentation, blog posts, or design assets, and name a supervision level and accountability holder for that use.
- **Moderation actions** (no) — The policy would need to state whether AI may assist maintainers in moderation actions (locking issues, banning users, etc.) and specify supervision and accountability for that use.
- **Review** (no) — The policy would need to state whether maintainers/reviewers may use AI tools to review contributions, and name a supervision level and accountability holder for that reviewer-side use.
- **Autonomous / agentic use** (no) — The policy would need to state whether autonomous or agentic AI systems may submit contributions or act without a human directly in the loop, and specify supervision level and accountability holder for such use.
- **Environmental Impact** (no) — The policy would need to state a rule addressing energy, water, or carbon footprint concerns tied to AI use, with an associated supervision level and accountability holder, rather than being silent on the topic.
- **Infrastructure strain** (no) — The policy would need to state a rule addressing server load or hardware cost strain caused by AI tool use (e.g. automated bulk PR generation), with a supervision level and accountability holder.
- **Data use for training** (no) — The policy would need to state a rule on whether/how platform user data (issues, PRs, comments, code) may be used to train AI models, with a supervision level and accountability holder.

