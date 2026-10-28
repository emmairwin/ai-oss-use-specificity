---
description: "Use when selecting, researching, reporting, or charting project cohorts for AI-policy coverage, including ecosyste.ms Critical dependencies."
applyTo: "reports/**"
---
# Project cohort policy analysis

- Keep each cohort separate, with its own landing page, project reports, and visual summaries. A cohort index should explain its selection method and link to source reports and charts.
- If the requested cohort is the top N projects **with AI policies**, continue down the stated ranking until N projects with an explicit AI-related policy are verified. Do not equate the top N ranked repositories with the top N that have policies, and do not count a generic contribution guide as an AI policy.
- Search beyond README files. Inspect repository trees and policy-bearing document types represented in the CHAOSS cohort summaries: policy documents, contribution guides, codes of conduct, `AGENTS.md`/agent guidance, pull-request templates, READMEs, FAQs, and other relevant official project documents. Check root, `docs/`, and hidden `.github/` paths. Use social posts only when explicitly in scope and no more authoritative source is available.
- Treat a project as having a qualifying AI policy only when an official source contains an explicit AI-related rule, requirement, permission, restriction, or guidance. Record exactly which documents were reviewed; a missing rule in one document is not evidence that the whole project has no policy.
- Cite each finding to the source document, preferably a stable line link or revision. Preserve scope and qualifications; do not turn a restriction on one submission type, workflow, contributor group, or security-report process into a project-wide code-contribution ban.
- Put source wording in quotation marks only when it is a verified direct quote, preserving its wording. Link the quote to its source and line. Label interpretations as summaries, use neutral language, and do not present invented labels or paraphrases as source terminology. In particular, phrases such as “AI slop” must be quoted only if those exact words occur in the linked source.
- Follow the existing CHAOSS report format and terminology (nine CHAOSS domains plus the project's tenth domain, slop, which records negative or dismissive wording about AI as the project's own words). Use `reports/chaoss_list_of_projects/` for the established CHAOSS cohort and keep new cohorts in their own `reports/<cohort>/` folders.
- For ranked cohorts, record the feed endpoint, ranking field and order, retrieval date, package-to-repository mapping, rank, and source count. Keep index, report, and chart values in agreement.
- Before finishing, validate cohort size and qualification, report-to-index links, all relative Markdown links, SVG XML, chart labels against source data, and `git diff --check`.
