# THIRD_PARTY — vendored upstream skills and their licenses

Only skills with an **explicit license file shipped alongside them** are
vendored here. Anything without a clean, checkable license is skipped, not
paraphrased — this list is the complete set of third-party content in the
repository.

| Skill | Directory | Upstream | License | Accessed | Modifications |
|---|---|---|---|---|---|
| `webapp-testing` | `skills/dev/webapp-testing/` | `github.com/anthropics/skills` (`skills/webapp-testing/`) | **Apache License 2.0** — full text in `skills/dev/webapp-testing/LICENSE.txt`, shipped with the skill as `license: Complete terms in LICENSE.txt` | 2026-10-26 | see below |

## webapp-testing — Apache-2.0

- **Origin**: fetched from the upstream public repository's default branch on
  2026-10-26 (`SKILL.md`, `LICENSE.txt`, `scripts/with_server.py`, and the
  three `examples/*.py` files), vendored whole rather than adapted.
- **Why it is in scope**: it matches this product's actual tool surface —
  local browser automation and script execution are already product tools, so
  the skill does not advertise capability we do not have.
- **License handling**: the Apache License 2.0 text is retained verbatim in
  the skill directory; the frontmatter keeps the upstream's own
  `license:` line. Attribution is this file.
- **Modifications (Apache-2.0 §4 permits them; they are listed here as
  required)**:
  1. `examples/console_logging.py` and `examples/static_html_automation.py`:
     three hard-coded absolute sandbox output paths were changed to relative
     `./…` paths so the examples run anywhere. No logic changed.
  2. `SKILL.md` frontmatter: a `metadata` block (`version: 1.0.0`,
     `author: anthropic (upstream)`) was added so the repository's catalog
     gate has a version to agree with. Body text is untouched.

## Not vendored (for the record)

- Upstream skills whose license could not be confirmed file-by-file were not
  copied, adapted, or summarised into this repository.
- Identity / persona skills from any source are excluded by policy: they are
  personal assets, not portable capability.
- Community marketplaces and community-hosted MCP-style packages stay
  disabled — the product installs files from a trusted, reviewed source only.
