# Bergen County Fourth Round (2025–2035) Affordable Housing Site Inventory

A complete, verified, **database-backed** inventory of every Fourth Round Mount
Laurel affordable-housing site across all **70 Bergen County, NJ** municipalities —
every parcel rezoned, overlay-zoned, or designated for inclusionary residential
development under **P.L. 2024, c.2 (A4)** and the associated HEFSPs, settlement
agreements, mediation agreements, and consent orders.

Built for a contract-and-entitle townhome acquisition strategy. The two failure
modes this system is designed against:
1. **Missing sites/municipalities** (missed deals) — every one of the 70 munis is
   tracked to completion.
2. **Inaccurate transcription** of block/lot, density, set-aside, or adoption
   status (bad contracts) — every site row carries a `source_url`, `source_date`,
   `confidence`, and `verification_status`. Nothing is recorded without a source;
   uncertain rows are flagged `needs-human-review`.

## State lives in SQLite (fully resumable)

All findings persist in `db/bergen.db`. No result is ever held only in conversation
memory. Each municipality has a `research_status` (`not_started` → `in_progress` →
`done` / `blocked`) so any run can pick up exactly where the last left off.

## Layout

```
db/bergen.db        SQLite — single source of truth
scripts/
  db.py             connection + logging helpers
  init_db.py        idempotent schema + seed of all 70 municipalities
  export.py         regenerate reports/ artifacts from the DB
  add_site.py       insert/update a verified site (used during research)
sources/            cached excerpts / notes from fetched primary documents
reports/
  inventory.csv     one row per site — the acquisition target list
  inventory.md      site inventory grouped by municipality
  STATUS.md         per-municipality research progress
```

## Schema (tables)

- **municipalities** — the 70 Bergen munis, their Fourth Round obligation
  (present/prospective need, RDP, unmet), compliance pathway, HEFSP status, and
  research workflow fields.
- **sites** — individual inclusionary/affordable sites with block, lot, acreage,
  mechanism, zoning, density, units, affordable count, set-aside %, tenure,
  adoption status, developer, and full provenance.
- **sources** — every primary document consulted (HEFSP, settlement, consent
  order, mediation agreement, ordinance, redevelopment plan), with URL + excerpt.
- **research_log** — append-only audit trail of research actions.

## Primary source hierarchy (authoritative → supplemental)

1. **NJ Courts affordable-housing library** (`library.njcourts.gov`) — adopted
   Fourth Round HEFSPs, settlement/consent orders by county/municipality.
2. **NJ DCA** Fourth Round obligation methodology — per-municipality numbers.
3. **Fair Share Housing Center** (`fairsharehousing.org`) — settlement tracking.
4. **Municipal websites** — adopted HEFSPs, zoning ordinances, redevelopment plans.
5. News / planner reports — corroboration only, never sole basis for a site.

## Usage

```bash
cd scripts
python3 init_db.py     # idempotent; safe to re-run
python3 export.py      # regenerate reports/ from current DB
```
