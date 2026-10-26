---
name: site-ops
description: Use when operating a static site on an edge platform — DNS changes, custom-domain binding, scoped API tokens, cache purge, a locked deploy chain — or when diagnosing a deploy, header, or ghost-path failure.
metadata:
  version: 1.0.0
  author: aidog
compatibility: Knowledge-first skill; wire the helper commands shown to your project's own scripts and tooling.
---

# site-ops — site operations quick reference

> Positioning: operations knowledge scatters across notebooks and daily logs
> and is unreachable on a cold start — collect it on this one page.
> Red lines: writes stay inside your own project; **credentials zero-echo**
> (report key names and `len > 0` only); scheduled/night jobs are never
> killed without approval; default is no force-push; paid actions are
> reported with a budget first.

## 1. Scoped token role table — check this table before touching anything

One job, one token. Least privilege means a token that can deploy usually
must **not** also be able to change DNS, and vice versa.

| Key | Typical powers | Typical blind spots |
|---|---|---|
| `DEPLOY_TOKEN` | Pages/hosting deploy, key-value store writes, domain management, API-token minting (can spawn scoped children) | **No zone DNS write** — DNS changes through it fail |
| `ZONE_TOKEN` | Zone DNS read/write (SPF/DMARC records), worker routes, cache purge | **Hosting API rejects it** (error `10000`-class); read-only or 401 on unrelated stores |
| `SINK_TOKEN` | Self-minted narrow token: worker scripts write + KV write + e-mail routing rules — for the inbound-mail worker only | No zone DNS, no hosting |
| `ACCOUNT_ID` | The account segment every bare REST call needs | — |

Rules learned the hard way:

- **Mint narrow tokens** with the API (`POST /client/v4/user/tokens`) and an
  explicit resource scope; a wrong resource key is rejected `400/1001`.
  New values go only into the project's secret store; stdout prints key
  names, never values.
- **Key-value REST paths must include the namespace segment**
  (`/accounts/{acct}/storage/kv/namespaces/{ns}/values/{key}`) — dropping it
  yields `400`/namespace-not-found; a `401` means the token lacks that
  resource, so switch the key, do not rewrite the URL.
- Never inject a raw secret into a child deploy process — **rename-inject**
  it under the variable the tool actually reads, so a leaked child env shows
  only the name.

## 2. DNS operations (the `www` / parked-record cleanup)

- Use the **zone token** for DNS writes; the deploy token has none.
- Typical `www` fix: delete the parked A record for `www`, add a `CNAME` to
  the hosting subdomain, then bind the custom domain on the hosting project
  itself (hosting/domain APIs often require the *deploy* token while DNS
  requires the *zone* token — using the other way round returns a
  `10000`-class error).
- **Proxied vs DNS-only is a security-header switch**: DNS-only points
  straight at the host and **does not receive the platform's header file or
  any edge WAF**; proxied goes through the edge and does. Decide
  deliberately, then verify header parity (expect 6/6 identical on both
  hosts) and re-check TLS CN + redirect behaviour (https 0 hops, http 1 hop).
  Roll back by PATCHing the record back — under a minute.

## 3. Platform API gotchas

- Missing paths on a SPA host return **200 + HTML fallback** — a ghost path.
  Data paths (`.json`, images) that answer `200 text/html` are fallback
  masquerading as real files: they feed crawlers wrong content and poison
  indexing. Make the router answer a real 404 for non-HTML leaves instead of
  falling back, and keep a regression assertion for both directions
  (ghost → 404, real file → 200 with the right type).
- Static asset caching: HTML tends to be revalidated, images cached for
  hours — so **raising TTL and purging after deploy are two halves of the
  same fix; never do only one**.

## 4. Deploy chain (single entry point — never race a bare CLI)

```bash
deploy --check     # refresh static content + run verification + summary; no publish
deploy --deploy    # verification and gates pass, then publish
deploy --deploy --force   # skips only the "date/contents unchanged" gate
deploy --deploy --dry-run # print the plan and gate states only
```

- **Exclusive lock** (`flock`) around the publish step: wait up to a
  timeout, fail with a clear exit code, never barge in. The lock excludes
  "at the same time", **not** "half-finished work" — check `git status` of
  the site and script directories for someone else's in-progress edits
  before a cross-session deploy.
- **Layer order**: verification (including a headless worker regression) →
  ready marker → lock → publish + live 200 **with an expected feature string**
  → targeted edge purge → per-image byte comparison (DIFF auto-purges and
  re-checks) → mobile render count → visual regression count → timestamp
  write → header parity.
- Reporting-only layers (purge, byte audit, mobile, visual, headers) report
  but do not block; exit codes still distinguish "verify refused" /
  "not ready" / "sanitization hit" (fail-closed).
- **Only the last line of the log plus the live feature string count** —
  piping through `tail` swallows the exit code, so never swallow it.
- The chain auto-snapshots (`git add -A && commit`) at the end — do not add
  a second manual commit; and **push only after confirming the configured
  committer address is the project's noreply identity**.
- Changed content file? Run its build step first — the deploy only injects
  the newest entries; anything derived is rebuilt by its own script.

## 5. Common pitfalls

1. **Wrong token for the job** → `10000`-class or 401: hosting = deploy
   token, DNS/purge = zone token, mail worker = minted sink token.
2. **Stale edge copy during a deploy window** — an asset fetched mid-deploy
   can be cached for hours: purge + byte audit together.
3. **Verification assertions only grow**: new capability ships with a new
   assertion; a FAIL may just mean a parallel content line is mid-write —
   wait for it to land and re-run instead of reverting green work.
4. **Ghost paths** (see §3) — data routes must 404, not fall back to HTML.
5. **Key-value REST missing the namespace segment** → 400/7000-class.
6. **Never kill scheduled/night jobs** (`*.lock`, `*.pid`): a pattern-based
   kill takes your own shell with it; ask before stopping one.
7. **Credential zero-echo**: verify presence by length only; some CLI auth
   commands print a token prefix into logs — avoid them; receipts and logs
   carry key names and paths only, and failures must surface the real
   status/body.

## 6. Acceptance

```bash
verify_skill_pack.py    # structure + keyword + zero-credential scan
node verify_worker.mjs   # worker function regression (assertions only grow)
deploy --check           # rc 0, full verification suite green
```
