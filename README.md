# AI use policies in open source

Open source projects set their own rules for AI use. This project collects
those rules and summarizes what they say. It does not rate whether a policy is
good or bad, or argue for or against AI.

## Browse the reports

- [CHAOSS project list](reports/chaoss_list_of_projects/README.md)
- [Critical dependencies with AI policies](reports/critical-dependencies/README.md)

The project list draws on the CHAOSS AI Alignment working group's
[collected projects](https://github.com/chaoss/wg-ai-alignment/blob/main/moderation/README.md)
and Melissa W.'s
[open-source AI contribution policies](https://github.com/melissawm/open-source-ai-contribution-policies).

## What the reports cover

Reports check whether a project's policy addresses nine topics: code
contributions, meeting bots, content and documentation, moderation, review,
autonomous or agent-based use, environmental impact, infrastructure strain,
and use of project data to train AI.

For each topic, the report looks at how clearly the policy explains who
supervises the work, what limits apply, who is responsible, and whether the
rules are proportionate.

The reports use a [CHAOSS metric](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md).
In the tables:

- `X` means the policy gives supervision guidance and at least one other
  detail.
- `~` means the topic is mentioned, but fewer details are given.
- `R` means the policy mentions the topic as a reason for a rule, but does not
  set a rule about it.
- A blank means the reviewed policy did not mention the topic.

Quotes and links in each report let you check the project's own wording.
`discouraged` means the policy advises against AI use but does not explicitly
ban it.

## An extra topic: "slop"

This project added a tenth topic that is not part of the CHAOSS metric. It
records a project's own negative or dismissive wording about AI or its output.
It captures tone, not a rule. The reports mark it as addressed and include a
quote.

The CHAOSS project-list reports were scored before this topic was added, so
they cover nine topics. The critical-dependencies reports include all ten.
