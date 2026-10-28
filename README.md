# AI policy specificity

Reports on how specifically open source projects' AI policies cover each of
nine domains, using the CHAOSS metric
[Consent Policy Specificity](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md),
plus a tenth, slop, added by this project.

Project and policy origins are curated from the CHAOSS AI Alignment working
group's [collected list](https://github.com/chaoss/wg-ai-alignment/blob/main/moderation/README.md)
and Melissa W.'s
[open-source-ai-contribution-policies](https://github.com/melissawm/open-source-ai-contribution-policies).

**[Reports](reports/)** — reports for the [CHAOSS list of projects](reports/chaoss_list_of_projects/README.md)
and the [critical dependencies with AI policies](reports/critical-dependencies/README.md).

## The ten domains

Code contributions, notetaker and meeting bots, content, moderation, review,
autonomous and agentic use, environmental impact, infrastructure strain, data
use for training, and slop.

Slop is not in the CHAOSS metric text. It records wording in a project's own
policy that is negative or dismissive of AI as a technology or its output in
general (for example "No AI slop will be accepted"). It captures attitude, not
a rule, so only the addressed mark and a quote are recorded.

Reports in `reports/chaoss_list_of_projects/` were scored before slop was
added and cover nine domains. Re-running them with the updated agent will add
the tenth.

The other nine are each checked for four attributes: supervision level, scope or volume limit,
who holds accountability, proportionality.

## Reading a report

`X` addressed, `~` coverage below the X specificity threshold, `R` raised in the policy's rationale but not
governed, blank not mentioned. `discouraged` marks advisory language against AI
use rather than an explicit prohibition. Footnotes give the policy's own words
and a link to the line.

Scores describe what a policy says, not whether it is any good. A permissive
policy stating its position precisely scores the same as a restrictive one.

Most grids are sparse. Most projects cover code contributions, many cover
documentation, few cover anything else.
