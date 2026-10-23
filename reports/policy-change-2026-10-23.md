# Policy change history: pilot

This pilot tracks AI-policy changes using source revision dates. Each entry describes a policy change, not a judgment of a project. “Added” and “removed” are change types; “tightened” and “loosened” describe direction. A revision can include more than one direction.

The sample is purposive, not exhaustive, and includes revisions checked through 2026-10-22. Each entry links to its source diff. New policies are shown as baselines, not automatically as tightening. No later change to curl’s AI policy is confirmed.

![Timeline of 28 policy revisions across 21 projects from May 2025 to October 2026 on one central date axis. Dot color identifies the project and dotted lines connect revisions from the same project. Dots above the line indicate tightening, below indicate loosening, and on the line indicate a new policy baseline, mixed change, clarification, or no established AI-policy direction. Numbered markers correspond to source-linked descriptions below. Vertical distance is qualitative, not a measured score.](../images/2026-10-23/policy-change.svg)

The chart shows the timeline and project colors. The numbered list below gives the change descriptions and clickable source links.

Domain labels use the Consent Policy Specificity taxonomy. A revision can affect multiple domains. “Outside taxonomy” is a note, not a domain, and is excluded from domain comparisons.

1. **2025-05-15 · curl** — Added AI-use guidance for code and content; AI-assisted security findings must be disclosed and verified. **Domains:** Code; Content. **Change:** first-observed baseline. [Source diff](https://github.com/curl/curl/commit/a9aafbea952643753d87262619ed310640748be4)
2. **2025-06-13 · Apache CouchDB** — Prohibited AI-generated code, documentation, commit messages, and other project materials. **Domains:** Code; Content. **Change:** restrictive baseline. [Source diff](https://github.com/apache/couchdb/pull/5562/files)
3. **2025-12-01 · scikit-learn** — Added disclosure to contribution policy and PR template for AI use in code, tests, docs, examples, and research. **Domains:** Code; Content. **Change:** added disclosure requirement. [Source diff](https://github.com/scikit-learn/scikit-learn/pull/32566/files)
4. **2026-01-06 · Linux kernel** — Added assistant guidance, human DCO sign-off and accountability, and `Assisted-by` attribution. **Domain:** Code. **Change:** first-observed baseline. [Source diff](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/Documentation/process/coding-assistants.rst?id=78d979db6cef557c171d6059cbce06c3db89c7ee)
5. **2026-01-08 · Django** — Required contributors to disclose AI use in PRs and confirm they reviewed and verified its output. **Domain:** Code. **Change:** added disclosure and verification. [Source diff](https://github.com/django/django/pull/19594/files)
6. **2026-03-04 · NumPy** — Added a policy covering responsibility, disclosure, quality, copyright, communication, and agent submissions. **Domains:** Code; Content; Autonomous / agentic use. **Change:** first-observed baseline. [Source diff](https://github.com/numpy/numpy/commit/ca46bafdef4f6b993f560b64ec7cd2da33198c05)
7. **2026-03-05 · LLVM** — Allowed an exception for the approved Bazel build-fixer bot, with future exceptions considered individually. **Domains:** Code; Autonomous / agentic use. **Change:** loosened for the approved bot. [Source diff](https://github.com/llvm/llvm-project/pull/183408/files)
8. **2026-03-07 · NumPy** — Clarified that the existing ban covers AI-written comments, PR descriptions, and issue descriptions. **Domain:** Code. **Change:** clarification; no direction established. [Source diff](https://github.com/numpy/numpy/commit/15497f5a4bd7ca4ac728e4cc8437ed4843a70619)
9. **2026-04-21 · Godot** — Required AI agents to identify themselves in issues and PRs; undisclosed agents may be banned. **Domains:** Code; Content; Autonomous / agentic use; Moderation actions. **Change:** added disclosure and enforcement. [Source diff](https://github.com/godotengine/godot/pull/118688/files)
10. **2026-05-26 · Cilium** — Linked the organization-wide policy in the PR template and asked contributors what they personally checked. **Domain:** Code. **Change:** clarified disclosure; no new use restriction established. [Source diff](https://github.com/cilium/cilium/pull/46126/files)
11. **2026-06-17 · Rust** — Added exceptions to the “non-critical” condition for organization members and earlier PRs. **Domain:** Code. **Change:** loosened. [Source diff](https://github.com/rust-lang/rust-forge/commit/419f96a19b3b53f6160e371e8b83a8d6cf34ded0)
12. **2026-06-22 · Rust** — Removed restrictions on meeting use and processes requiring an LLM. **Domain:** Outside taxonomy; meeting-bot mapping is unclear. **Change:** removed and loosened. [Source diff](https://github.com/rust-lang/rust-forge/commit/ab6f5c68e2f5a1e72fcd45f6b02c5ebf9f9a854b)
13. **2026-07-15 · PyTorch** — Moved contribution guidance to `AI_POLICY.md` and linked contribution templates to it. **Domain:** Code. **Change:** reorganized; no direction established. [Source diff](https://github.com/pytorch/pytorch/commit/ffc572d6aba76129928e0caaa96a93bd0585f903)
14. **2026-07-29 · Homebrew** — Prohibited AI authorship and required contributors to answer maintainer questions and review comments themselves. **Domains:** Code; Review; Content. **Change:** tightened authorship and human accountability. [Source diff](https://github.com/Homebrew/brew/pull/23317/files)
15. **2026-08-03 · Linux kernel** — Changed required attribution from naming the assistant and model to `Assisted-by: LLM`. **Domain:** Code. **Change:** loosened. [Source diff](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/Documentation/process/coding-assistants.rst?id=816d9992d9ed434ec52cfbd63080d518e535a41b)
16. **2026-08-04 · Linux kernel** — Added steps to reproduce, fix, and test AI-assisted bug findings. **Domain:** Code. **Change:** added provision. [Source diff](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/Documentation/process/coding-assistants.rst?id=3d7c44f73765d98665fb97a4fb89c002c88ba1b9)
17. **2026-08-04 · Bevy** — Replaced a blanket ban with limited human-driven code assistance while restricting AI-generated media, prose, and communications. **Domains:** Code; Content; Review; Moderation actions. **Change:** mixed; some code use loosened, restrictions and accountability added. [Source diff](https://github.com/bevyengine/bevy-website/pull/2551/files)
18. **2026-08-14 · pandas** — Restricted AI-written contributor communications, with language-assistance exceptions and disclosure requirements. **Domains:** Code; Content; Review. **Change:** tightened communication and disclosure. [Source diff](https://github.com/pandas-dev/pandas/pull/66767/files)
19. **2026-10-02 · mise** — Limited AI-assisted support replies to eligible participants; violations may lead to a ban. **Domains:** Code; Moderation actions. **Change:** tightened. [Source diff](https://github.com/jdx/mise/pull/13886/files)
20. **2026-10-07 · PyTorch** — Allowed a heading to label AI-generated content instead of requiring a code or quote block; disclosure remains required. **Domain:** Code. **Change:** loosened format requirement. [Source diff](https://github.com/pytorch/pytorch/commit/5df8cd4b1e7ca1ca2a8a97aeb732ce6a021d3632)
21. **2026-10-08 · Apache DataFusion** — Welcomed reviewed AI assistance, rejected unreviewed dumps, and required reviewers to edit AI-generated review output. **Domains:** Code; Review; Content; Moderation actions. **Change:** revised guidance and added safeguards. [Source diff](https://github.com/apache/datafusion/pull/24510/files)
22. **2026-10-13 · Nominatim** — Added contributor review and accountability requirements and a maintainer refusal option; removed a proof requirement. **Domains:** Code; Moderation actions. **Change:** mixed. [Source diff](https://github.com/osm-search/Nominatim/pull/4220/files)
23. **2026-10-14 · Linux kernel** — Removed `Assisted-by` attribution; human DCO and responsibility requirements remain. **Domain:** Code. **Change:** removed provision. [Source diff](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/Documentation/process/coding-assistants.rst?id=1e035297ffdadf2184c3c773b8c098e372324aaf)
24. **2026-10-15 · Meilisearch** — Changed from requiring disclosure to excluding AI-generated contribution content. **Domains:** Code; Content. **Change:** tightened. [Source diff](https://github.com/meilisearch/meilisearch/pull/6684/files)
25. **2026-10-15 · XMTP** — Replaced a ban on mostly AI-generated PRs with review, testing, explanation, disclosure, and human-authored discussion requirements. **Domain:** Code. **Change:** loosened with accountability requirements. [Source diff](https://github.com/xmtp/libxmtp/pull/4574/files)
26. **2026-10-16 · Cilium** — Added an AI-influence declaration and policy agreement to the bug-report form. **Domains:** Content; Moderation actions. **Change:** added disclosure step. [Source diff](https://github.com/cilium/cilium/pull/49098/files)
27. **2026-10-19 · Python-Markdown** — Required disclosure of AI use, tools, and generated content; requires templates and allows immediate closure when they are ignored. **Domains:** Code; Content; Moderation actions. **Change:** tightened disclosure and enforcement. [Source diff](https://github.com/Python-Markdown/markdown/pull/1658/files)
28. **2026-10-21 · Seerr** — Clarified that AI-driven contributions are disallowed; assistance is limited to work the contributor writes. **Domain:** Code. **Change:** tightened. [Source diff](https://github.com/seerr-team/seerr/pull/3636/files)

## Not yet classified

- **CPython:** Removed from this directional pilot because the sampled revisions did not establish a tightening or loosening of its AI-specific guidance.
- **Apache Airflow:** Its Gen-AI guidance was added in January 2026, but a later directional revision has not been confirmed in the history sampled so far.
- **Linux kernel:** The existing August 30 report predates the October 14 removal of the attribution requirement; it is a dated snapshot, not a description of the current policy.
- **curl:** The AI-use guidance was added on 2025-05-15. Later edits to the contributing document were checked; the May 2026 wording fix was outside the AI-guidance section. No later AI-policy change is established here.

## What the expanded sample suggests

The 28 revisions across 21 projects include tightening, loosening, baselines, clarifications, and mixed changes. This sample is not representative and cannot show an ecosystem-wide trend. The Linux kernel changes on August 3 and 4 concern different provisions.

## Method notes

- Dates are commit or merge dates from the linked source; they may differ from the policy’s effective date.
- File moves are recorded separately from rule changes.
- Direction compares the revised rule with its prior wording. A new policy is a baseline unless earlier evidence supports a comparison.
- Inaccessible history is not evidence of no change.
