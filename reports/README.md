# Scan index

3 scans against the CHAOSS [Consent Policy Specificity](https://github.com/chaoss/wg-ai-alignment/blob/main/metrics/ai-alignment-community-governed-use/ai-use-consent-policy-specificity.md) metric. Each row links to the full report, which carries the evidence quotes and line numbers behind every cell.

`✓` addressed · `~` partial · `·` not addressed, out of nine domains. **Leans** counts domains with no rule where the policy still shows a direction.

| Project | Scanned | ✓ | ~ | · | Leans | Summary | | |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `servo/book` ᶠ | 2026-08-29 ⚠ | 2 | 1 | 6 | 2 | Servo's getting-started guide is highly specific and restrictive about AI in code, documentation, issues, and comments (banned,… | [report](servo-book/2026-08-29.md) | [improve](https://github.com/emmairwin/ai-oss-use-specificity/issues/new?title=Report%20correction%3A%20servo%2Fbook&body=Report%3A%20servo-book/2026-08-29.md%0ADomain%3A%0AReported%20as%3A%0AShould%20be%3A%0AQuote%20from%20the%20policy%3A%0A) |
| `go-gitea/gitea` ᶠ | 2026-08-29 | 1 | 0 | 8 | – | CONTRIBUTING.md contains one specific, named AI policy — for code contributions (PRs/issues), requiring disclosure and human review/testing with… | [report](go-gitea-gitea/2026-08-29.md) | [improve](https://github.com/emmairwin/ai-oss-use-specificity/issues/new?title=Report%20correction%3A%20go-gitea%2Fgitea&body=Report%3A%20go-gitea-gitea/2026-08-29.md%0ADomain%3A%0AReported%20as%3A%0AShould%20be%3A%0AQuote%20from%20the%20policy%3A%0A) |
| `astropy/astropy-project` ᶠ | 2026-08-29 | 2 | 1 | 6 | – | Astropy's AI policy is narrowly and specifically scoped to code/documentation contributions and pull requests - requiring disclosure, human… | [report](astropy-astropy-project/2026-08-29.md) | [improve](https://github.com/emmairwin/ai-oss-use-specificity/issues/new?title=Report%20correction%3A%20astropy%2Fastropy-project&body=Report%3A%20astropy-astropy-project/2026-08-29.md%0ADomain%3A%0AReported%20as%3A%0AShould%20be%3A%0AQuote%20from%20the%20policy%3A%0A) |

ᶠ scope was limited to named files, so `·` means *not addressed in those files* rather than repository-wide.

⚠ the scan cited a quote that could not be found in the file it named. Read that report's *Validation problems* section before trusting its grid.

*The improve links are a stub — they point at an issue tracker that may not exist yet. Change `IMPROVE_BASE` in `chaoss_agent.py` once there is somewhere for corrections to go.*
