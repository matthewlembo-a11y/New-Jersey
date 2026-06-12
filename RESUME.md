# RESUME HERE — Verification Pass instructions for a new session

You are resuming the **Bergen County Fourth Round affordable-housing site
inventory**. Phase 1 (a search-only candidate build) is complete and committed.
Network egress has now been opened, so your job is **Phase 2: verification** —
open the primary documents and upgrade each candidate row to verified,
contract-grade data.

## First, orient yourself
1. Read `README.md`, `reports/SUMMARY.md`, and `NETWORK_ACCESS.md`.
2. Confirm egress is live:
   `curl -sS -o /dev/null -w "%{http_code}\n" https://library.njcourts.gov`
   Expect `200`/`403`-from-server, NOT "Host not in allowlist". Also test WebFetch
   on a courts-library PDF. If still blocked, stop and tell the user.
3. Inspect current state:
   ```bash
   python3 - <<'PY'
   from scripts.db import connect
   c = connect()
   print("munis:", c.execute("SELECT COUNT(*) n FROM municipalities").fetchone()["n"])
   print("sites:", c.execute("SELECT COUNT(*) n FROM sites").fetchone()["n"])
   for r in c.execute("SELECT research_status, COUNT(*) n FROM municipalities GROUP BY research_status"):
       print(r["research_status"], r["n"])
   PY
   ```

## The data model (already built — do not recreate)
- `db/bergen.db` is the single source of truth. Helpers in `scripts/`:
  - `scripts/db.py` — `connect()`, `log()`
  - `scripts/add_site.py` — `set_muni()`, `add_source()`, `add_site()` (upserts;
    site dedupe key = municipality + block + lot + site_name)
  - `scripts/export.py` — regenerate `reports/` (run after each batch)
- Every site currently has `verification_status='needs-human-review'` and
  `confidence` of `low`/`medium`. Sources are in the `sources` table and in each
  site's `source_url`.

## Verification methodology (per municipality)
Work municipality by municipality. For each:
1. Pull its candidate rows and source URLs:
   ```sql
   SELECT s.*, m.name FROM sites s JOIN municipalities m ON m.id=s.municipality_id
   WHERE m.name = ? ;
   ```
2. Fetch the **primary document** (prefer `library.njcourts.gov` adopted HEFSP,
   else the municipal HEFSP/settlement/ordinance). Use WebFetch; if a gov host
   refuses WebFetch, use `curl` to download the PDF then parse with `pdftotext`
   (install via `pip install pypdf` or use `pdftotext` if available).
3. For EACH inclusionary/affordable site in the document, confirm or CORRECT:
   block, lot, acreage, current/proposed zoning, density, total_units,
   affordable_units, set_aside_pct, tenure, mechanism, adoption_status, developer.
   - Use `add_site()` to upsert (it matches on block+lot+site_name).
   - Set `confidence='high'` and `verification_status='verified'` only for values
     you read directly in the primary document.
   - If the document contradicts the candidate row, TRUST THE DOCUMENT and fix it;
     note the correction in `notes`.
   - **Add any sites the search pass missed.** Completeness matters as much as
     accuracy.
4. Update municipality-level fields with `set_muni()`: present_need,
   prospective_need, rdp, unmet_need, total_obligation, compliance_status,
   settlement_party/date, hefsp_status/adopted_date/url; set
   `research_status='done'`.
5. `python3 scripts/export.py`, then commit + push:
   `git add -A && git commit -m "Verify <Muni>: ..." && git push origin claude/bergen-county-fourth-round-inventory-h1d2v6`

## Priority order
1. **The 5 genuine gaps** (0 sites, plan exists but wasn't search-reachable):
   **Carlstadt, Lodi, Lyndhurst, Moonachie, Northvale.** Find their HEFSPs and
   build the site lists from scratch.
2. **High-value leads** (verify block/lot first): Fair Lawn, Mahwah, Oakland,
   Oradell, Hackensack, Maywood, Englewood, Edgewater, Teaneck, Saddle Brook.
3. **All remaining `needs-human-review` rows**, municipality by municipality.
4. Leave the 3 documented exemptions (Cliffside Park QUAM, Garfield zero,
   Teterboro airport) as-is unless a document shows otherwise.

## Scale tip
There are ~67 municipalities with documents to verify. Consider dispatching
parallel sub-agents (general-purpose, model sonnet) in batches — but have them
WRITE FINDINGS TO JSON FILES and let the MAIN session do all DB writes (serialize
writes; avoids sqlite lock contention). Reuse the `findings/` + `scripts/ingest.py`
pattern from Phase 1; the agent prompt template is in the git history.

## Definition of done
Every municipality `research_status='done'`; every site either
`verification_status='verified'` (confirmed against a primary doc) or explicitly
`needs-human-review` with a note saying why it couldn't be confirmed. No invented
parcel data, ever.
