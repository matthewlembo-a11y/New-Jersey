# Bergen County Fourth Round Inventory — Executive Summary

_**Phase 2: primary-document verification — COMPLETE.** Generated June 2026.
Branch: `claude/funny-newton-ihn59l`._

## Headline numbers

| Metric | Value |
|---|---|
| Municipalities covered (`research_status = done`) | **70 / 70** |
| Municipalities with verified development sites | **64** |
| Documented site-less municipalities (legitimate) | **6** |
| Total catalogued sites | **374** |
| **Sites verified against a primary document** (`confidence = high`) | **359** |
| Sites still `needs-human-review` (flagged, with notes) | 15 |
| Sites with block captured | **309** |
| Sites with affordable-unit count | 285 |
| Sites with set-aside % | 256 |
| Primary sources recorded | **428** |

## What changed from Phase 1

Phase 1 was a **search-only candidate build** (egress to every primary-source
host was blocked, so nothing was confirmed against the underlying documents; all
186 rows were `needs-human-review`). In Phase 2, **network egress was opened** and
every municipality was re-built or re-verified by reading the **primary documents
themselves** — adopted Fourth Round HEFSPs, settlement/consent orders, mediation
agreements, and implementing/overlay ordinances, almost all from the NJ Courts
affordable-housing library (`library.njcourts.gov`).

Because the court filings are **scanned images**, a fetch + OCR pipeline was built
(`scripts/fetchpdf.py`, PyMuPDF + Tesseract). The **authoritative NJ DCA Fourth
Round Calculation Workbook** was downloaded and parsed (`sources/dca_bergen_obligations.json`)
to lock each municipality's official Present/Prospective Need and cross-check
every plan's numbers. Block/lot, density, units, and set-asides were read directly
out of the plans and ordinances; every verified site carries a verbatim source
quote in its `notes` for provenance.

## Coverage

- **64 municipalities with verified inclusionary/affordable sites** — inclusionary
  overlays, affordable-housing overlay zones, redevelopment areas, 100%-affordable
  and municipally-sponsored sites, group homes, and RDP-compliance parcels, each
  with block/lot read from the adopted plan or ordinance where the document states it.
- **6 documented site-less municipalities (legitimate, each confirmed against a
  primary source):**
  - **Cliffside Park**, **Garfield**, **Lodi** — Qualified Urban Aid Municipalities
    (QUAM): rehabilitation-only, Prospective (new-construction) Need = 0, no
    inclusionary sites. (Garfield's prior "recalculated to zero" note was corrected:
    its 322-unit rehab obligation stands; only new construction is zero.)
  - **Lyndhurst** — claims a Vacant Land Adjustment yielding RDP 0; HEFSP challenged
    by Fair Share Housing Center; full Fair Share Plan not in the court-library upload.
  - **Teterboro** — Prospective Need 92 is satisfied by existing deed-restricted
    units under DCA's 20%-of-stock cap; no new construction required.
  - **Moonachie** — ⚠️ **OPEN ITEM:** DCA Present 102 / Prospective 301, but NO
    adopted HEFSP could be located (no court-library folder; municipal 2026
    ordinances are non-housing). Flagged `REVISIT` — a potential missed deal.

## High-value leads — now verified (block/lot confirmed)

- **Fair Lawn** — Fair Lawn Avenue Site = **Block 4702, Lot 1** (≤352 units, 17.65
  du/ac, 20% set-aside) + two overlay districts. (HEFSP not filed with the court;
  verified from the codified zoning ordinance, eCode360 Ch. 49.)
- **Mahwah** — 457 Ridge Road = **Block 139, Lot 41** (~74 affordable), plus
  MF-1/2/3 overlays and Block 70/82 redevelopment.
- **Oakland** — McBride RA-6AH (**Block 3301 L2 + Block 3401** multi-lot, 240u/48aff),
  Leone RA-7AH (**Block 4004 L4-5**, 85u/17aff), DT-1/DT-2 AH overlays (22/15 du/ac, 20%).
- **Oradell** — 445-447 Kinderkamack rezone (22 du/ac, 15u/3aff), Reis Ave Habitat
  (**Block 107 L29**), CBD overlay extension.
- **Hackensack** — QUAM (rehab-only) but actively redeveloping: 7 sites incl. Meridia
  (Block 305 L2), Essex Street Redevelopment (Block 66 multi-lot, 250u/25aff), HABC.
- **Maywood** — West Passaic (**Block 87 L2-4**), Brook Ave (**Block 107 L51-55**),
  AH-1 (**Block 3 L1**), all 20% set-aside.
- **East Rutherford** (11 sites: Tomu/Meadows 420u, Monarch 316u, AHO/AHO-B/AHO-C),
  **Saddle Brook**, **Teaneck** (822 Palisade 60 du/ac), **Englewood**, **Edgewater**.

## Largest verified opportunities (by affordable capacity)

Paramus HCC overlay (~2,683 aff capacity), Ridgewood Downtown B1/B2 (313),
Leonia Fort Lee Road redevelopment (243, 40-60 du/ac), Englewood Cliffs Overlay
Zone D (166), Franklin Lakes Parsons Pond (133, Cigna/IBM site), Palisades Park
14th & Edsall (118, 100% municipally-sponsored). _Overlay-zone figures are
maximum zoned capacity, not committed units._

## Remaining caveats (the 15 `needs-human-review` rows + notes)

These are sites the verification agents recorded but flagged as not fully
confirmable from the primary document (e.g., block/lot from a zoning-ordinance
snippet rather than clean plan text, or Fourth-Round vs prior-round status
ambiguous): clustered in **Tenafly, Upper Saddle River, Waldwick, Wallington,
South Hackensack**. Each carries a note describing exactly what could not be
confirmed. Also flagged for follow-up: **Moonachie** (no plan located),
**Montvale** (Fair Share Plan section not in the court-library upload — sites
known but block/lot pending), and **Fair Lawn** (verified from codified zoning,
not an adopted HEFSP).

## Integrity

No block/lot, unit count, density, or set-aside was invented. Verified rows were
read directly from the cited primary document (URL + section recorded, with a
verbatim quote in `notes`); where a value was not stated it is left null. All
state is in `db/bergen.db`; `python3 scripts/export.py` regenerates `reports/`.
