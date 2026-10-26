# REVIEW — human gate for aidog-skills

`tools/lint.py` is the machine gate. This file is the human gate that runs
**on top of it**. Both must pass before a skill is merged or listed —
deny-by-default: an unchecked skill is not a listed skill.

Reviewer walks the four sections in order and ticks every line. A single
unticked line blocks the merge; blocking is the expected outcome, not a
failure of the process.

## A. Sanitization gate (leak — fail closed)

- [ ] No machine-local path anywhere in the skill: machine mount points
      (`/mnt…`), root-home paths (`/root…`), home directories, drive
      letters — machine lint proves 0 hits, reviewer confirms the intent (a path obfuscated into a string still counts).
- [ ] No credential of any kind: values, prefixes, `KEY=value` lines,
      private keys, token-shaped strings. Key **names** may appear only when
      they are genuinely needed to say which slot to fill, and never next to
      a value.
- [ ] No personal identity: real names, handles, e-mail addresses (RFC 2606
      reserved `example.*` placeholders are fine), phone numbers, chat ids,
      avatars, biographies, personality/profile descriptions.
- [ ] No internal codenames, project codenames, cross-repo private links, or
      anything that maps an online artifact to a real person.
- [ ] No upstream-brand wording in our own prose (third-party vendored files
      are exempt only inside `THIRD_PARTY.md`-listed content).
- [ ] Outbound text would survive the product's own sanitization scan if it
      were published today.

## B. Quality gate (description quality decides routing quality)

- [ ] `description` says **when to use the skill**, in the imperative
      ("Use when …" / "当……时使用"), not just what it is — the deterministic
      router pre-filters on this string alone.
- [ ] Description carries realistic trigger scenarios **and** at least one
      negative (what it must NOT be used for), so near-miss queries do not
      route here.
- [ ] Body follows progressive disclosure: short `SKILL.md`, long detail in
      `scripts/` / `references/` / `assets/`, nothing loaded before it is hit.
- [ ] Helper commands shown are either real and runnable in the integrating
      product or clearly generic placeholders — no dead script names
      presented as if they ship here.
- [ ] Statements are dated or dated-able where they are empirical
      ("as measured on YYYY-MM-DD"); no evergreen claim that will rot.
- [ ] Body is written in generic first person for a reader who has never
      seen the authoring project.

## C. License gate

- [ ] Our own skill: no third-party text copied or adapted.
- [ ] Vendored upstream skill: an explicit license file is present **in the
      skill directory**, the license terms are satisfied (attribution,
      notices, license text kept intact), and the entry appears in
      `THIRD_PARTY.md` with source URL + access date + any modification.
- [ ] No license field left ambiguous: either a real license name/reference
      or an honest statement of provenance.

## D. Safety gate (product red lines)

- [ ] **Files, not execution**: the skill only lands files and instructions;
      it never asks for auto-run, community MCP installation, or any
      unattended privilege escalation.
- [ ] **Trusted source is read-only**: nothing in the skill writes outside
      the project's own paths, and nothing fetches-and-executes remote code.
- [ ] **Approval boundaries preserved**: money, publishing, external
      messages and credential changes stay behind the human approval gate
      the product already enforces.
- [ ] `requires` honestly lists what the skill needs — a skill that needs a
      tool the product does not have must not be listed as usable.

## Review record

| Skill | Date | Reviewer | Machine gate | Outcome |
|---|---|---|---|---|
| (one row per skill, appended on each review) | | | `=== N/N PASS ===` | approved / rejected + reason |
