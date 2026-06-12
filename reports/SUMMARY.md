# Bergen County Fourth Round Inventory — Executive Summary

_Search-only candidate build. Generated June 2026. Branch:
`claude/bergen-county-fourth-round-inventory-h1d2v6`._

## Headline numbers

| Metric | Value |
|---|---|
| Municipalities covered | **70 / 70** |
| Candidate sites catalogued | **186** |
| Primary sources recorded | **353** |
| Municipalities resolved (`done`) | 43 |
| Municipalities pending verification (`in_progress`) | 27 |
| Sites with block captured | ~82 |
| Sites with lot captured | ~78 |
| Sites with set-aside % | ~112 |
| Sites with unit counts | ~93 |

## What this is — and what it is NOT

This inventory was built **search-only**: the environment's network egress
allowlist blocked every primary-source host (NJ Courts library, nj.gov/DCA,
Fair Share Housing Center, municipal sites), so site data was mined from
WebSearch result synthesis rather than read out of the HEFSPs themselves.

**Every site row is flagged `verification_status = needs-human-review`.**
Block/lot, density, unit counts, and set-asides that did come through are
captured with their source URL and a `confidence` rating (`medium` = from an
official municipal/court snippet; `low` = from a news/summary paraphrase), but
**none has been confirmed against the underlying primary document.** Do not
treat any parcel identifier here as contract-ready until the verification pass.

No block/lot, unit count, density, or set-aside was ever invented. Where a value
was not stated in a reliable search result, it is left null with a note.

## Coverage classes

- **Sites found & sourced (most municipalities):** inclusionary rezonings,
  affordable-housing overlays, redevelopment areas, 100%-affordable sites,
  group homes, and accessory-apartment programs — each tied to a source URL.
- **Documented zero-obligation / exempt (no inclusionary sites — legitimate):**
  - **Cliffside Park** — Qualified Urban Aid Municipality (QUAM); prospective
    need = 0; rehabilitation share only.
  - **Garfield** — present and prospective need recalculated to **zero** by
    court order (May 5, 2025); fully built-out urban city.
  - **Teterboro** — ~827 acres of airport, near-zero residential land; zero
    rehab obligation confirmed; no development sites.
- **Genuine gaps — HEFSP exists but not search-accessible (verification-pass
  targets):** Carlstadt, Lodi, Lyndhurst, Moonachie, Northvale. Each has an
  adopted plan, ongoing litigation, or DCA numbers that could not be confirmed
  from search snippets. These are the highest-priority items for the egress-
  enabled pass — potential missed deals.

## Notable high-value leads (verify first)

- **Fair Lawn** — large obligation (Present 224 / Prospective 650), settled with
  FSHC (Apr 2025); Fair Lawn Avenue site referenced at up to 352 units, 20%
  set-aside (block/lot unconfirmed).
- **Mahwah** — 457 Ridge Road, ~74 affordable rental units.
- **Oakland** — Leone (85 u / 17 aff), McBride (240 u), Downtown-1/-2 overlays
  (20% set-aside, density raised to 22 du/ac).
- **Oradell** — six Kinderkamack Road corridor sites.
- **Hackensack** — multiple downtown redevelopment / 100%-affordable sites.
- **Maywood** — Brook Ave & West Passaic St stacked-townhome overlays (Block 87),
  20% set-aside.

## Next step — verification pass (resumable)

1. Widen the environment's network egress (hosts in `../NETWORK_ACCESS.md`).
2. Resume on this branch and run the verification pass: for each
   `in_progress` / `needs-human-review` row, open the HEFSP / settlement /
   ordinance and confirm or correct block, lot, acreage, density, units,
   set-aside, and adoption status; flip `verification_status` to `verified`.
3. Prioritize the 5 genuine gaps (Carlstadt, Lodi, Lyndhurst, Moonachie,
   Northvale) and the high-value leads above.

All state is in `../db/bergen.db`; re-running ingestion/export is idempotent.
