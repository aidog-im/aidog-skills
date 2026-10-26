---
name: research-brief
description: Use when asked to verify a claim, compare options, shortlist or select a tool, summarise a topic, or draft a reply from research — a three-tier report pipeline with multi-source verification, mandatory citations and three-colour annotation.
metadata:
  version: 1.0.0
  author: aidog
compatibility: Knowledge-first skill; wire the helper commands shown to your project's own scripts and tooling.
---

# research-brief — verification & reporting pipeline

> Positioning: the highest-frequency request is "check / compare / summarise
> / draft an answer". This skill fixes it as one reusable pipeline instead of
> improvising channels every time.

## 1. Three tiers — pick the tier before starting (never ask what you can find out yourself)

| Tier | Trigger phrasing | Output | Search budget |
|---|---|---|---|
| **TL;DR ≤300 words** | "is it true / latest / one line / quick answer" | Template A: conclusion + 2–3 sourced facts | 1 round |
| **Standard** | "look up / compare / turn into a list / write a report" | Template B (conclusion + evidence table + contrast + open questions + sources) | 2–4 rounds |
| **Deep** | "full report / material to publish / decision input" | Template C: everything in B + archived evidence + cross-checking across pages | multi-source + archiving |

- Default = **standard**; when unsure, lead with a TL;DR conclusion and add
  "say the word for the full version" — never block waiting for instructions.
- Anything the requester must **decide** (selection, partnership, publishing)
  is at least standard; anything **going out publicly** is deep plus the
  sanitization pass.

## 2. Search channel strategy (a degrading chain, not a single dependency)

- Prefer an **aggregated multi-provider search** (batch related queries into
  one call, use time filters for time-sensitive facts) and then **fetch the
  full page** for anything you will quote — snippets are not sources.
- Keep a fallback chain behind it: a direct web-fetch proxy → a
  local search-engine HTML endpoint through a browser user agent → a
  server-side fetch service. Each hop has a timeout; if a provider returns
  401/403, **do not fight it — step down the chain and keep delivering**.
- Fetching your **own** site may be walled by user-agent rules; use a
  browser user agent or the fallback fetcher.
- Running a pre-flight keyword check for known pitfalls before starting
  saves a whole research round.

## 3. Verification rules (the no-fabrication red line, executable)

1. **≥2 independent sources** before writing "confirmed"; a single source is
   marked 🟡 "single source, needs re-check"; not findable → write
   "**could not verify**". Never invent, never treat memory as fact.
2. **Every number carries its unit and date**: conflicting figures are
   printed side by side and flagged as disputed, not averaged.
3. **Falsify before confirming**: try to disprove first (a fabricated id
   hitting an API returns 404; an odd claim is checked against an official
   source that can overrule it).
4. **Timeliness**: funding, pricing, policy and quota facts must be re-fetched
   (filter recent); old news is labelled with its date explicitly.
5. Platform or algorithm data quotes its **version date**.
6. **Self-serve before asking**: anything you can verify yourself gets
   verified; questions are reserved for decisions only the requester can make.

## 4. Three-colour annotation + sources (all tiers)

- 🟢 **Fact** — reproducible, inline `[n]` marker
- 🟡 **Inference** — your own assembly, labelled as such
- 🔴 **Opinion** — a recommendation, labelled as such

**Source list** at the end: `[n] Title — URL (accessed YYYY-MM-DD)`; every
factual assertion carries a marker. **Deep tier archives evidence**:
snapshots into a dated folder with a manifest holding sha256 per file plus
source URL and fetch channel, so a later correction can be traced.

## 5. Templates

### A · TL;DR (≤300 words)
```
[CONCLUSION] one or two sentences — say it flat if certain, name the missing
             evidence if not
[BASIS]      🟢 fact…[1]  |  🟢 fact…[2]  |  🟡 single source…[3]
SOURCES: [1] URL  [2] URL  [3] URL (accessed YYYY-MM-DD)
```

### B · Standard report
1. **Conclusion** (≤5 lines, answer first)
2. **Evidence table**: fact | unit/date | colour | source[n]
3. **Comparison** when relevant: dimension | A | B | what actually differs;
   every cell sourced, missing data written as "no public data found"
4. **Open questions**: disputed figures and unverifiable items, one per line
5. **Sources**: `[n] Title — URL (accessed date)`

### C · Deep report (decision / publishable material)
Everything in B + quoted key passages + multi-page cross-checks + evidence
archive + a **public-facing sanitization self-check**.

## 6. Comparison / selection deliverable (fixed six steps, no improvisation)

1. **Fix the objects and dimensions**: ≤5 objects; dimensions by purpose
   (budget / compliance / ecosystem / onboarding / cost); default six when
   unsure: capability, price, ecosystem & integrations, compliance & risk,
   onboarding cost, regional availability.
2. **Same-denominator data**: same date, same unit across cells (`—` =
   unavailable, never 0); every cell carries `[n]`.
3. **Fixed table shape**: dimension | A | B | … | what differs and why; a
   `unit/date` row under the table; empty cells say "no public data found".
4. **Three colours**: 🟢 measured/official docs | 🟡 single source |
   🔴 disputed (🔴 must also appear in open questions).
5. **Conclusion first**: ≤5 lines with the recommendation, one reason not to
   pick the runner-up, and the trigger that would re-open the call (price or
   version change).
6. **Delivery**: standard tier by default (table + sources + open
   questions); anything going out publicly gets the deep tier and the
   sanitization gate; the draft stays in the project's reports folder.

## 7. Outbound sanitization gate (only for material leaving the project)

Internal reports may carry internal context. Anything that leaves — public
replies, published lists, forwarded drafts — must drop: personal names,
handles, accounts, project codenames, machine paths, geography, contact
details and any credential. **Anything that could map an online account to a
real person is left out; when unsure, leave it out.** Public text also avoids
shell fragments (backticked commands trip edge WAFs) and respects per-channel
link rules.

## 8. Iron rules

1. No fabrication, no impersonation — "cannot verify" is a valid answer.
2. Self-serve first; the requester's attention is reserved for decisions.
3. Free channels first; **any paid action is reported with a budget first**.
4. Deliver in the requester's language, as numbered options and
   add/remove lists.
5. Credentials zero-echo (key names and lengths only).
6. Write only inside the project's own paths.

## 9. Smoke / acceptance

```bash
verify_skill_pack.py    # structure + red-line keywords + zero credential values
```
Real micro-smoke: a live factual query → aggregated search (recent-window
filter, batched queries) → fetch 1–2 full pages → Template A answer with
`[n]` markers and three-colour annotation.
