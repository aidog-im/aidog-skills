# aidog-skills — official recommended skills

**PRIVATE repository.** This is the single source of truth for the skills the
product officially recommends; it stays private until the owner rules
otherwise, exactly like the product repository it feeds. Do not export,
mirror, or open it without an explicit, case-by-case decision from the owner.

```
aidog-skills/
├── catalog.json                    # machine-readable master catalog — the
│                                   # website and the product read THIS file
├── skills/<category>/<name>/
│   └── SKILL.md                    # open Agent Skills format (frontmatter +
│       [scripts/ references/ assets/ examples/]  markdown body)
├── tools/lint.py                   # machine gate  (structure + leak scan)
├── REVIEW.md                       # human gate     (sanitization + quality + license)
├── THIRD_PARTY.md                  # attribution list for vendored upstream skills
└── README.md
```

## Format

Skills follow the open Agent Skills specification — nothing invented:

- a skill is a directory containing at least `SKILL.md`;
- `SKILL.md` = YAML frontmatter + markdown body;
- required frontmatter: `name` (≤64, lowercase/hyphen, **must equal the
  directory name**) and `description` (≤1024, says what it does **and when to
  use it**);
- optional: `license`, `compatibility` (≤500), `metadata` (string→string,
  conventionally `version` / `author`), `allowed-tools`;
- discovery is progressive: only `name` + `description` are read until a task
  actually matches, so descriptions — not bodies — carry the routing load.

## Catalog fields (`catalog.json`)

Top level is exactly `{"skills": [ … ]}`. Every entry carries exactly these
seven fields — no more, no less:

| Field | Type | Meaning |
|---|---|---|
| `slug` | string | lowercase-hyphen id, equals the directory and frontmatter `name` |
| `name` | string | display name (identical to `slug` today) |
| `category` | enum | `automation-ops` · `research` · `dev` · `content` · `trading-readonly` · `reporting` |
| `description` | string | ≤1024, one line, verbatim the frontmatter description |
| `version` | semver | skill revision (mirrors `metadata.version` in the frontmatter) |
| `requires` | string[] | tools or credential slots the skill needs to do anything |
| `install_status` | enum | `bundled` (ships inside the product's own skill layer) or `catalog` (install from this catalog) |

## Two gates — deny-by-default

A skill is listed only after **both** pass:

1. **Machine gate** — `python3 tools/lint.py` → `=== N/N PASS ===`:
   catalog/frontmatter/directory agreement, format limits, resolving
   relative links, and a leak scan over **every file in the repo**
   (machine paths, credential shapes, personal handles, e-mail addresses,
   internal codenames, upstream brand token — zero hits).
2. **Human gate** — the checklist in [`REVIEW.md`](REVIEW.md): sanitization,
   description quality ("when to use" + trigger negatives), license, and the
   read-only / files-not-execution red line.

## Sources

| Source | Count | Rule |
|---|---|---|
| Product's bundled skill layer | 5 | copied verbatim (trading read-only ×3, systematic debugging, writing plans) |
| De-identified replications of a sister project's operating skills | 6 | rewritten in generic first person: no machine paths, no personal profile, no real handles, no credentials, no internal codenames, no cross-repo private links; identity/persona skills are **excluded by policy** |
| Vendored upstream public skills | 1 | only with an explicit license file; see [`THIRD_PARTY.md`](THIRD_PARTY.md) |

## Website catalog

The product website renders a committed copy of this file at
`site/skills/catalog.json`, and its directory page (`site/skills.html`)
groups the same entries by category. **`catalog.json` here is the master**;
the website copy is refreshed from it whenever this repository changes
(see `docs/features/skills_ecosystem.md` in the product repository for the
sync procedure).

## Review & change discipline

- New or changed skill → run `tools/lint.py` → walk `REVIEW.md` → commit.
- `metadata.version` bumps on every content change; note it in the catalog
  in the same commit.
- Red lines carried over from the product: **skills land as files, never as
  execution** (no marketplace, no community MCP, no auto-run), **trusted
  source is read-only**, and **credentials are never echoed** anywhere —
  not in a skill, not in a log, not in a catalog entry.
