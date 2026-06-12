# Network egress required for the verification pass

This environment runs under a **network egress allowlist**. During the initial
build only **GitHub** and the WebSearch endpoint were reachable; every primary
affordable-housing source returned `403 Host not in allowlist`. As a result, the
current inventory is a **search-only candidate build**: site names, approximate
units, set-asides, mechanisms, and source URLs are captured, but **block/lot and
other contract-grade fields are NOT verified** (rows are flagged
`confidence=low`, `verification_status=needs-human-review`).

To let me read the primary documents and produce verified, block/lot-accurate
records, widen the environment's network policy. Easiest is an **open / broad
egress** policy. If you prefer a tight allowlist, these hosts cover the spine:

## Must-have hosts
- `library.njcourts.gov` — adopted Fourth Round HEFSPs, consent orders, settlement docs (by county/municipality)
- `www.njcourts.gov` / `njcourts.gov` — affordable-housing portal / dockets
- `www.nj.gov` / `nj.gov` — DCA Fourth Round obligation numbers & methodology
- `www.fairsharehousing.org` / `fairsharehousing.org` — settlement tracking

## Common municipal-document hosts (HEFSPs, ordinances, redevelopment plans)
- `ecode360.com` — codified municipal zoning ordinances
- `*.revize.com` / `cms*.revize.com` — many Bergen municipal websites
- `*.civicplus.com` / `DocumentCenter` paths on muni domains
- `clerkbase.com`, `municode.com`, `granicus.com` — minutes / ordinances
- Individual municipal domains (e.g. `oakland-nj.org`, `mahwahtwp.org`, etc.)

> Because municipal documents are spread across dozens of domains, an open egress
> policy is the most reliable choice for full coverage. After widening the policy,
> resume this session (or start a new one on the same branch) and tell me to run
> the verification pass — the SQLite state makes it fully resumable.

## How to change it
Network policy is chosen per-environment in Claude Code on the web. See
https://code.claude.com/docs/en/claude-code-on-the-web for the available policies
and how to edit egress settings.
