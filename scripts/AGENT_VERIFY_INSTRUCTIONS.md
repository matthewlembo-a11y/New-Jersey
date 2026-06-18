# Verification-agent instructions (Bergen County Fourth Round inventory, Phase 2)

You verify affordable-housing **sites** for assigned NJ (Bergen County)
municipalities by reading the **primary documents** (adopted Fourth Round HEFSP,
settlement, consent order, implementing/overlay ordinance) and writing a findings
JSON. **You do NOT touch the database or git.** The main session ingests your JSON.

## Inputs already on disk (read these)
- `sources/bergen_docmap.json` — `{slug: [full PDF urls in that muni's NJ Courts library folder]}`.
- `sources/ocr/<slug>.txt` — pre-OCR'd text of the *best-guess* primary doc (may be
  missing, or may be only a resolution if the guess was wrong). First line is `SOURCE_URL:`.
- `sources/dca_bergen_obligations.json` — `{ "<Muni> borough/township/city": {present_need, prospective_need, quam} }`
  — the **authoritative DCA** obligation. Use to set/cross-check muni numbers.
- `sources/candidate_snapshot.json` — `{Muni: {sites:[...], ...}}` Phase-1 search-only
  candidate rows for the muni. These are UNVERIFIED leads to confirm or CORRECT — not truth.

## Tool for fetching/OCR'ing a PDF
`python3 scripts/fetchpdf.py "<PDF_URL>" sources/ocr/<slug>__<shortlabel>.txt`
- Downloads (cached) + extracts text; auto-OCRs scanned pages (slow: ~3s/page).
- Always wrap the URL in quotes (URLs contain `?VersionId=...`).

## Procedure for EACH assigned municipality
1. Read `sources/ocr/<slug>.txt`. If it is missing, tiny, or clearly just a
   resolution/cover letter (no "Fair Share Plan", no site/zoning detail), pick the
   real plan from `sources/bergen_docmap.json` (prefer filenames containing
   `HEFSP`/`HousingElement`/`FairSharePlan`/`Plan` + `Part1`/`Adopted`/`Final`; avoid
   `reso`, `ordinance`, `cert`, `cover`, `appendix`, `spendingplan`, `marketing`) and
   OCR it yourself. The Fair Share Plan / "Plan for Addressing the Prospective Need"
   section (usually the back third) is where sites live.
2. **OCR implementing/overlay ordinances too when the HEFSP references a rezoning/
   overlay but gives no block/lot** — the ordinance (filename has `ordinance`/`overlay`/
   `zoning`/`Ord`) usually lists the exact Block/Lots, density, and set-aside.
3. For EVERY inclusionary, 100%-affordable, overlay, redevelopment-for-affordable,
   or municipally-sponsored site in the plan, capture: site_name, address, block, lot,
   acreage, mechanism, current_zoning, proposed_zoning, density (du/ac), total_units,
   affordable_units, set_aside_pct, tenure (rental/sale), adoption_status, developer.
   - Include `quote`: a short **verbatim** snippet from the document containing the
     block/lot (or the key fact). This is mandatory for any block/lot you report.
   - Read numbers DIRECTLY from the doc. If a field isn't stated, use `null` — **never
     guess or carry over an unconfirmed candidate value.** Do not invent parcels.
   - If the document contradicts the candidate snapshot, TRUST THE DOCUMENT; note the
     correction in `notes`.
   - `confidence`: `"high"` + `verification_status`:`"verified"` ONLY for values you
     read in the primary doc. If you truly cannot find/confirm a muni's plan, set the
     muni `research_status`:`"blocked"` and explain.
4. Muni-level: set obligation from the doc; if the doc doesn't state it, use the DCA
   JSON (note the source). Capture compliance status, settlement party/date, hefsp
   status/adopted date, and hefsp_url (the actual plan PDF url you used).
5. Watch for legitimately **site-less** outcomes: Qualified Urban Aid (QUAM, rehab-only,
   prospective need 0), or a Vacant Land Adjustment giving RDP 0. Record 0 sites with a
   clear note + the obligation numbers — that's a valid, valuable result.

## Output (one file per muni)
Write `findings/verify/<slug>.json` — a single JSON object:
```json
{
  "municipality": "<exact DB name>",
  "research_status": "done",
  "obligation": {"present_need": int|null, "prospective_need": int|null,
                 "total_obligation": int|null, "rdp": int|null, "unmet_need": int|null,
                 "source_url": "<url>"},
  "compliance": {"status": str|null, "settlement_party": str|null, "settlement_date": str|null,
                 "hefsp_status": str|null, "hefsp_adopted_date": "YYYY-MM-DD"|null, "hefsp_url": "<url>"},
  "notes": "muni-level summary incl. how the obligation is satisfied",
  "sources": [{"doc_type":"HEFSP|ordinance|settlement|resolution|DCA","title":"...","url":"...","excerpt":"..."}],
  "sites": [{
    "site_name": "...", "address": null, "block": "...", "lot": "...", "acreage": null,
    "mechanism": "inclusionary overlay|100% affordable|redevelopment|...",
    "current_zoning": null, "proposed_zoning": null, "density": null,
    "total_units": null, "affordable_units": null, "set_aside_pct": null,
    "tenure": "rental|sale|null", "adoption_status": "...", "developer": null,
    "source_url": "<primary doc url>", "source_page": "<section/page>",
    "source_date": "YYYY-MM-DD", "confidence": "high", "verification_status": "verified",
    "quote": "<verbatim snippet with the block/lot>", "notes": "..."
  }]
}
```
Use the **exact DB municipality name** I give you (e.g. "Ho-Ho-Kus", "Washington
Township"). Keep block/lot as strings exactly as written ("3301.02", "1, 2, 3").
When done, reply with a one-line-per-muni summary: name, #sites, key correction(s).
