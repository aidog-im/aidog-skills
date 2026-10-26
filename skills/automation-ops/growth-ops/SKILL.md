---
name: growth-ops
description: Use when you need free distribution for a site or project — search-engine indexing, directory submissions, verification emails, an overnight unattended submission run, or a judgement call on whether a channel is worth retrying.
metadata:
  version: 1.0.0
  author: aidog
compatibility: Knowledge-first skill; wire the helper commands shown to your project's own scripts and tooling.
---

# growth-ops — free distribution & indexing playbook

> First principle: **check the channel matrix before acting — a dead wall is
> never retried** (the physical reason it is walled does not change).
> Red lines: no paid promotion without an approved budget, no fake engagement
> (bought follows, bot replies), no cold DMs, credentials never echoed, and
> you write only inside your own project's paths.

## 1. Channel matrix (maintain your own, dated)

Record every channel you actually tested, with the date and the observed
behaviour. Two buckets only:

| Bucket | Meaning | Rule |
|---|---|---|
| **Live** | Submission worked, verification completed, listing visible | Reuse; keep the exact working recipe in the row |
| **Dead wall** | Hard anti-bot wall: reCAPTCHA / Turnstile / hCaptcha / forced phone number / invite-only / account creation disabled from your egress | **Never retry.** 2 losses = abandon for good |

Universal lesson from testing: challenges that cannot be solved by a human
reading a form (image CAPTCHA, turnstile, phone gate, invite gates) do not
yield to automation — spend the effort on pure-form, graphic-code-readable,
or e-mail-verification directories instead.

## 2. Free indexing channels

- **Indexing API** (Bing/Yandex/Naver-style push): submit changed URLs,
  idempotently, behind a per-URL cooldown ledger (7 days is a sane window).
  Google-style engines generally do not accept anonymous pushes — do not
  build a plan around them without an owner-approved account.
- **Directory submissions**: manual or scripted form fills, one submission
  per directory ever (ledger), never resubmit to game position.
- **Owned surfaces**: your own repo README/index pages, your own blog — the
  only channel you fully control.
- **Communities**: participate where you already have an account; never
  mass-post.

## 3. E-mail verification loop

Directory and registration flows verify by e-mail. Make that loop scriptable:

1. Use a **catch-all address** on your own domain routed into a queryable
   store, or one dedicated alias per directory (`dir-<host>@`, `<service>@`)
   so a leak is attributable and revocable.
2. Poll the inbox on a short interval; extract the verification link
   (deduplicated, trailing punctuation stripped).
3. GET the link once — idempotently; record the result in a ledger so a
   restart never double-verifies.
4. Never echo the mailbox credentials; report only key names and `len > 0`.

## 4. Directory submission SOP

1. Retrieve candidates, then **verify each submission surface is really
   open first** (pure form / no paywall / no login).
2. One submission per directory: name, URL, and a one-line description taken
   from the site's own meta description — no exaggeration.
3. Poll for the verification e-mail (30–180 s), follow the link, mark done.
4. Keep a ledger per wave (`directory/状态/verification result`), cap each
   wave (e.g. 15) so the run stays reviewable, abandon after 2 consecutive
   hard walls.
5. Next wave prioritises pure-form and e-mail-gated directories; the dead
   wall list is skipped forever.

## 5. Overnight unattended run (the nightshift pattern)

A long-running process that advances the queue while you sleep:

- **Single-instance lock** (lock file) + rolling duration (`--hours N`) or an
  end time (`--until HH:MM`); never start a second copy.
- Per tick: drain the queue → follow pending verification links (idempotent
  ledger) → push to the indexing API → snapshot traffic counters →
  liveness probe of your own services → **self-heal only what you own**
  (restart a crashed local service at most once per cooldown window, e.g.
  900 s, so a crash loop cannot become a storm).
- Persist state to small JSON files so a restart resumes, never repeats.
- Produce a daily summary artifact (log + markdown summary + counter CSV);
  the run's output must be reviewable without reading the raw log.

## 6. Measurement meta-rules

- **Measure every action**: double down on what converts, stop what does
  not — decided by the ledger and the counter CSV, not by vibes.
- **Same denominator or no comparison** (`—` means unavailable, never 0).
- Indexing push → engine pickup typically takes 7–14 days; do not kill a
  channel on day 2.
- Each wave picks the next batch by measurable yield, not by hope.

## 7. Competitor / peer monitoring (read-only)

A scripted chain, one step per process, all against **public read-only
surfaces**:

1. Discover relevant public accounts (search engine, rate-limited).
2. Supplement the id list incrementally with back-off.
3. Fetch posts (public post-detail endpoints), then account profiles.
4. Aggregate into a high-signal list plus a terminal summary.
5. Page sentinels for non-social surfaces (official site / repo / docs):
   keep a baseline hash per page, diff on check, report new hashes or
   keyword hits (release/tag style markers).

**Fixed four-section output**: ① changes (who changed what, with date and
link) → ② signals (followers/likes/stars, same denominator, `—` = n/a) →
③ what to borrow / what to watch (1–3 actionable lines) → ④ sources
`[n] URL (accessed YYYY-MM-DD)`.

**Cadence**: one pass per wave — no hot polling, no hammering rate limits;
if a page walls you, switch to a headed browser only when allowed, never
bypass a login. **Red lines**: never log in as someone else, never touch
private data, credentials zero-echo, findings do not leave the project
without the outbound sanitization pass.

## 8. Iron rules

1. The matrix is evidence, not opinion — dated rows, reproducible recipes.
2. Anything paid (paid directories, newsletter placements) is reported with a
   budget first and never executed without approval.
3. Account-gated consoles (webmaster tools, site verification) are used only
   with an owner-provided account; do not procure one yourself.
4. Every artifact lands inside the project's own directories.
