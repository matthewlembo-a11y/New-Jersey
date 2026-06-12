"""Review + ingest a Phase-2 verification findings file (findings/verify/<slug>.json).

Folds each site's verbatim `quote` into its notes (provenance), then upserts via
the existing ingest path. Prints a human-readable summary for review.

Usage: python3 scripts/ingest_verify.py findings/verify/<slug>.json [--quiet]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import connect
from ingest import ingest_one


def prep(rec):
    for s in rec.get("sites") or []:
        q = s.pop("quote", None)
        if q:
            note = (s.get("notes") or "").rstrip()
            s["notes"] = (note + " " if note else "") + f'[src quote: "{q.strip()}"]'
        # guard: clean obvious non-parcel placeholders
        for k in ("block", "lot"):
            if isinstance(s.get(k), str) and s[k].strip().lower() in ("", "n/a", "tbd", "none", "unknown"):
                s[k] = None
    return rec


def summary(rec):
    m = rec["municipality"]
    ob = rec.get("obligation") or {}
    comp = rec.get("compliance") or {}
    print(f"\n=== {m} === status={rec.get('research_status')}")
    print(f"  oblig: PN={ob.get('present_need')} Prosp={ob.get('prospective_need')} "
          f"RDP={ob.get('rdp')} unmet={ob.get('unmet_need')} total={ob.get('total_obligation')}")
    print(f"  compliance={comp.get('status')} hefsp={comp.get('hefsp_status')} "
          f"adopted={comp.get('hefsp_adopted_date')}")
    sites = rec.get("sites") or []
    print(f"  sites: {len(sites)}")
    for s in sites:
        print(f"   - {s.get('site_name')!r} blk={s.get('block')} lot={s.get('lot')} "
              f"| {s.get('total_units')}u/{s.get('affordable_units')}aff "
              f"| set-aside={s.get('set_aside_pct')} dens={s.get('density')} "
              f"| {s.get('mechanism')} | conf={s.get('confidence')}/{s.get('verification_status')}")


def main():
    path = sys.argv[1]
    quiet = "--quiet" in sys.argv
    rec = json.load(open(path))
    if isinstance(rec, list):
        recs = rec
    else:
        recs = [rec]
    conn = connect()
    for r in recs:
        prep(r)
        if not quiet:
            summary(r)
        n = ingest_one(conn, r)
        if not quiet:
            print(f"  -> ingested {n} sites")
    conn.close()


if __name__ == "__main__":
    main()
