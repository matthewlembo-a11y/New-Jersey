"""
Ingest research findings (JSON) into the database.

Input: a JSON file containing a list of municipality-finding objects. Each object:
{
  "municipality": "Oakland",
  "research_status": "done" | "in_progress" | "blocked",
  "obligation": {"present_need": int|null, "prospective_need": int|null,
                 "total_obligation": int|null, "rdp": int|null, "unmet_need": int|null,
                 "source_url": str|null},
  "compliance": {"status": str|null, "settlement_party": str|null, "settlement_date": str|null,
                 "hefsp_status": str|null, "hefsp_adopted_date": str|null, "hefsp_url": str|null},
  "notes": str|null,
  "sources": [{"doc_type": str, "title": str, "url": str, "excerpt": str|null}],
  "sites": [{"site_name","address","block","lot","acreage","mechanism","current_zoning",
             "proposed_zoning","density","total_units","affordable_units","set_aside_pct",
             "tenure","adoption_status","developer","source_url","source_page","source_date",
             "confidence","verification_status","notes"}]
}

Block/lot and numeric fields are written exactly as provided (null stays null — we
never invent parcel data). Default confidence is 'low' and verification_status is
'needs-human-review' for search-only findings unless explicitly overridden.
"""
import json
import sys
from db import connect, log
from add_site import set_muni, add_source, add_site


def ingest_one(conn, rec):
    name = rec["municipality"]
    muni_fields = {}
    ob = rec.get("obligation") or {}
    for k_src, k_db in [("present_need", "present_need"), ("prospective_need", "prospective_need"),
                        ("total_obligation", "total_obligation"), ("rdp", "rdp"),
                        ("unmet_need", "unmet_need"), ("source_url", "obligation_source_url")]:
        if ob.get(k_src) is not None:
            muni_fields[k_db] = ob[k_src]
    comp = rec.get("compliance") or {}
    for k_src, k_db in [("status", "compliance_status"), ("settlement_party", "settlement_party"),
                        ("settlement_date", "settlement_date"), ("hefsp_status", "hefsp_status"),
                        ("hefsp_adopted_date", "hefsp_adopted_date"), ("hefsp_url", "hefsp_url")]:
        if comp.get(k_src) is not None:
            muni_fields[k_db] = comp[k_src]
    if rec.get("notes"):
        muni_fields["notes"] = rec["notes"]
    if rec.get("research_status"):
        muni_fields["research_status"] = rec["research_status"]
    set_muni(conn, name, **muni_fields)

    for s in rec.get("sources") or []:
        if s.get("url"):
            add_source(conn, name, s.get("doc_type", "other"), s.get("title", ""),
                       s["url"], s.get("excerpt", "") or "")

    nsites = 0
    for site in rec.get("sites") or []:
        site = dict(site)
        site.setdefault("confidence", "low")
        site.setdefault("verification_status", "needs-human-review")
        # never let empty strings masquerade as parcel data
        for k in ("block", "lot"):
            if site.get(k) in ("", "N/A", "TBD", "unknown", "Unknown"):
                site[k] = None
        add_site(conn, name, **site)
        nsites += 1

    log(conn, name, "ingest", f"{nsites} sites, status={rec.get('research_status')}")
    return nsites


def main():
    if len(sys.argv) < 2:
        print("usage: python3 ingest.py findings.json")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    conn = connect()
    total = 0
    for rec in data:
        n = ingest_one(conn, rec)
        total += n
        print(f"  {rec['municipality']:24s} {n} sites")
    conn.close()
    print(f"Ingested {total} sites across {len(data)} municipalities.")


if __name__ == "__main__":
    main()
