#!/usr/bin/env python3
"""Machine gate for the aidog-skills repository (deny-by-default review layer 1).

Run:  python3 tools/lint.py          (exit 0 = every check green)

Two scan passes:

1. STRUCTURE / SPEC  — the open Agent Skills format, nothing invented:
     catalog.json          top level = {"skills": [...]} with exactly the
                           seven catalog fields from the design
                           (slug / name / category / description / version /
                           requires / install_status)
     skills/<cat>/<name>/SKILL.md
                           directory name == frontmatter `name`; `name` <= 64
                           lowercase-hyphen chars; `description` <= 1024 chars
                           and non-empty; optional license / compatibility /
                           metadata (string -> string) / allowed-tools
     cross-checks          catalog <-> frontmatter <-> directory, no orphans,
                           no missing entries, relative markdown links resolve,
                           SKILL.md stays within a sane byte budget

2. LEAK SCAN  — every text file in the repo (except .git and this tool, which
   self-excludes like the product's own publish gate) must score zero hits on:
     machine paths (/mnt/, /root/, /Users|/home, drive letters)
     credential shapes (KEY=<value>, private keys, provider token prefixes)
     personal messaging handle (@my_*_bot)
     e-mail addresses
     internal codenames / cross-repo private names
     the upstream brand token (assembled below so this file stays clean)

REVIEW.md is the human gate on top of this one; both must pass (deny-by-default).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORIES = ("automation-ops", "research", "dev", "content",
              "trading-readonly", "reporting")
ENTRY_FIELDS = ("slug", "name", "category", "description", "version",
                "requires", "install_status")
INSTALL_STATES = ("bundled", "catalog")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
MAX_NAME, MAX_DESC = 64, 1024
MAX_SKILL_BYTES = 100_000
MAX_DESC_WORDS = 60          # a one-liner, not an essay

# Own constants, assembled from fragments so this file never carries the
# contiguous literal and therefore never trips its own scan. This file is part
# of a PUBLIC repository — a detector that spells out what it detects would be
# the leak itself (observed: the codename alternative below was a literal).
BRAND = "her" "mes"
_OWNER = "C" + "\u603b"
_LEGACY = "jav" + "is"
_ASSOC = "msg" + "chain"
# The former product-repo alias needs no alternative of its own: it contains
# _LEGACY as a substring and the scan is case-insensitive.
INTERNAL = re.compile("|".join((_OWNER, _LEGACY, _ASSOC)), re.IGNORECASE)

LEAK_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("machine-path-mnt", re.compile(r"/mnt/")),
    ("machine-path-root", re.compile(r"/root/")),
    ("machine-path-home", re.compile(r"/Users/|/home/[a-z]")),
    ("machine-path-drive", re.compile(r"[A-Za-z]:\\")),
    ("credential-assignment", re.compile(
        r"(?m)^[A-Za-z0-9_]*(?:TOKEN|PAT|SECRET|PASSWORD|API_KEY|API_SECRET|"
        r"PASSPHRASE)[A-Za-z0-9_]*\s*=\s*[A-Za-z0-9_\-/+=]{8,}")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token-shape", re.compile(
        r"\bghp_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|"
        r"\bsk-[A-Za-z0-9]{20,}|\bxox[baprs]-[A-Za-z0-9-]{10,}|"
        r"\bAKIA[0-9A-Z]{16}\b")),
    ("personal-handle", re.compile(r"@my_[a-z0-9_]+_bot\b")),
    ("e-mail", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("internal-codename", INTERNAL),
    ("upstream-brand", re.compile(re.escape(BRAND), re.IGNORECASE)),
]

SKIP_LEAK_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip")
# RFC 2606/6761 reserved documentation names cannot identify anybody — an
# address on one of them is a placeholder, not a leak (keeps third-party
# examples verbatim).
RESERVED_MAIL_DOMAINS = ("example.com", "example.org", "example.net",
                         "test", "invalid", "localhost")
SELF = Path(__file__).resolve().parent.parent / "tools" / "lint.py"

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)


def bad(label: str, detail: str = "") -> None:
    FAIL.append(f"{label}{'  (' + detail + ')' if detail else ''}")


def check(label: str, condition: bool, detail: str = "") -> bool:
    if condition:
        ok(label)
    else:
        bad(label, detail)
    return condition


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal YAML subset: `key: value` scalars + one nested string map.

    Good enough for the open skill format's frontmatter and deliberately
    dependency-free; anything unparseable fails the gate instead of being
    skipped. Nested keys are flattened as `parent.child`.
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end < 0:
        return None
    block = text[4:end]
    data: dict[str, str] = {}
    owner: str | None = None          # current nested block name
    nested: dict[str, str] = {}

    def flush() -> None:
        nonlocal owner, nested
        if owner is not None:
            data[owner] = json.dumps(nested, sort_keys=True)
        owner, nested = None, {}

    for raw in block.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  "):
            if owner is None:
                return None           # indented line without a parent key
            k, sep, v = raw.strip().partition(":")
            if not sep or not v.strip():
                return None
            nested[k.strip()] = v.strip()
            continue
        k, sep, v = raw.partition(":")
        if not sep:
            return None
        key, value = k.strip(), v.strip()
        if value:
            flush()
            data[key] = value
        else:
            flush()
            owner, nested = key, {}
    flush()
    for parent, blob in list(data.items()):
        if blob.startswith("{"):
            try:
                for ck, cv in json.loads(blob).items():
                    data[f"{parent}.{ck}"] = cv
            except json.JSONDecodeError:
                return None
    return data


def iter_text_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] == ".git":
            continue
        if path.suffix.lower() in SKIP_LEAK_SUFFIXES:
            continue
        if path.resolve() == SELF:
            continue          # self-exclusion (brand constant lives here)
        if path.stat().st_size > 2_000_000:
            continue
        yield rel, path


def main() -> int:
    # ---------------------------------------------------- catalog.json ---
    cat_path = ROOT / "catalog.json"
    if not check("catalog.json exists", cat_path.is_file()):
        return report()
    try:
        catalog = json.loads(cat_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        bad("catalog.json parses", str(exc))
        return report()

    check("catalog top level is exactly {skills}",
          isinstance(catalog, dict) and set(catalog) == {"skills"},
          ",".join(catalog.keys()) if isinstance(catalog, dict) else type(catalog).__name__)
    entries = catalog.get("skills") if isinstance(catalog, dict) else None
    if not check("catalog.skills is a non-empty list",
                 isinstance(entries, list) and bool(entries)):
        return report()

    seen: dict[str, dict] = {}
    for i, e in enumerate(entries):
        where = f"entry[{i}]"
        if not check(f"{where} is an object", isinstance(e, dict)):
            continue
        check(f"{where} fields exact",
              set(e) == set(ENTRY_FIELDS),
              "extra:" + ",".join(sorted(set(e) - set(ENTRY_FIELDS))) +
              " missing:" + ",".join(sorted(set(ENTRY_FIELDS) - set(e))))
        slug = e.get("slug", "")
        where = f"entry {slug!r}" if slug else where
        check(f"{where} slug format", isinstance(slug, str) and bool(SLUG_RE.match(slug or "")))
        check(f"{where} unique slug", slug not in seen, "duplicate")
        check(f"{where} name == slug", e.get("name") == slug)
        check(f"{where} name <= {MAX_NAME}",
              isinstance(e.get("name"), str) and len(e.get("name", "")) <= MAX_NAME)
        check(f"{where} category legal",
              e.get("category") in CATEGORIES, str(e.get("category")))
        desc = e.get("description")
        check(f"{where} description 1..{MAX_DESC}",
              isinstance(desc, str) and 0 < len(desc) <= MAX_DESC,
              str(len(desc)) if isinstance(desc, str) else type(desc).__name__)
        if isinstance(desc, str):
            check(f"{where} description is a one-liner",
                  len(desc.split()) <= MAX_DESC_WORDS, str(len(desc.split())))
        check(f"{where} version semver",
              isinstance(e.get("version"), str) and bool(SEMVER_RE.match(e.get("version", ""))),
              str(e.get("version")))
        req = e.get("requires")
        check(f"{where} requires is a list of tool/slot names",
              isinstance(req, list) and all(isinstance(x, str) and x for x in req))
        check(f"{where} install_status enum",
              e.get("install_status") in INSTALL_STATES, str(e.get("install_status")))
        if isinstance(slug, str):
            seen[slug] = e

    # ------------------------------------------------- skills tree -------
    skills_root = ROOT / "skills"
    if not check("skills/ exists", skills_root.is_dir()):
        return report()

    dirs: dict[tuple[str, str], Path] = {}
    for cat_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        check(f"category dir legal: {cat_dir.name}", cat_dir.name in CATEGORIES, cat_dir.name)
        for skill_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if not check(f"{cat_dir.name}/{skill_dir.name} has SKILL.md", skill_md.is_file()):
                continue
            dirs[(cat_dir.name, skill_dir.name)] = skill_dir
            text = skill_md.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            if not check(f"{skill_dir.name} frontmatter parses", fm is not None):
                continue
            name = fm.get("name", "")
            check(f"{skill_dir.name} has name", bool(name))
            check(f"{skill_dir.name} name == directory", name == skill_dir.name,
                  f"{name!r} != {skill_dir.name!r}")
            check(f"{skill_dir.name} name format",
                  bool(SLUG_RE.match(name)) and len(name) <= MAX_NAME)
            d = fm.get("description", "")
            check(f"{skill_dir.name} description 1..{MAX_DESC}",
                  0 < len(d) <= MAX_DESC, str(len(d)))
            # "does it say WHEN to use it" is a human REVIEW.md gate (wording
            # quality), not a machine gate — the machine checks structure.
            check(f"{skill_dir.name} SKILL.md within byte budget",
                  skill_md.stat().st_size <= MAX_SKILL_BYTES,
                  str(skill_md.stat().st_size))
            # catalog cross-check
            entry = seen.get(skill_dir.name)
            if check(f"{skill_dir.name} present in catalog", entry is not None):
                check(f"{skill_dir.name} catalog description == frontmatter",
                      entry.get("description") == d)
                check(f"{skill_dir.name} catalog category == directory",
                      entry.get("category") == cat_dir.name)
                fv = fm.get("metadata.version")
                if fv:
                    check(f"{skill_dir.name} catalog version == frontmatter",
                          entry.get("version") == fv)
                else:
                    # An untouched bundled copy (no frontmatter metadata) is
                    # versioned by the product release; anything else must
                    # carry metadata.version.
                    check(f"{skill_dir.name} unversioned frontmatter is bundled only",
                          entry.get("install_status") == "bundled",
                          "add metadata.version or mark bundled")
            # relative markdown links resolve
            for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
                target = m.group(1)
                if re.match(r"^(https?:|mailto:|#|/)", target):
                    continue
                resolved = (skill_dir / target).resolve()
                check(f"{skill_dir.name} link resolves: {target}",
                      resolved.exists(), "missing")

    # every catalog entry has a directory
    for slug, entry in seen.items():
        check(f"catalog entry {slug} has a directory",
              (entry.get("category"), slug) in dirs, "no skills/<cat>/<slug>/")
    check("no orphan skill directories",
          len(dirs) == len(seen), f"{len(dirs)} dirs vs {len(seen)} catalog entries")

    # ---------------------------------------------------- leak scan ------
    hits: list[str] = []
    scanned = 0
    for rel, path in iter_text_files():
        scanned += 1
        try:
            blob = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            hits.append(f"{rel}: unreadable ({exc})")
            continue
        for label, pat in LEAK_PATTERNS:
            for m in pat.finditer(blob):
                if label == "e-mail":
                    addr = m.group(0)
                    dom = addr.rsplit("@", 1)[-1].lower()
                    if dom in RESERVED_MAIL_DOMAINS:
                        continue
                line = blob.count("\n", 0, m.start()) + 1
                hits.append(f"{rel}:{line} [{label}] {m.group(0)[:40]!r}")
    check(f"leak scan: {scanned} files, 0 hits", not hits, "; ".join(hits[:8]))

    return report()


def report() -> int:
    total = len(PASS) + len(FAIL)
    for f in FAIL:
        print(f"FAIL  {f}")
    print(f"=== {len(PASS)}/{total} PASS ===")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
