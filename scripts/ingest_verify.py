"""Review + ingest a Phase-2 verification findings file (findings/verify/<slug>.json).

- Resolves the correct DB municipality name from the FILENAME slug (agents sometimes
  label the muni with a slug-derived name like "Hackensack city"); the slug is the
  source of truth.
- Folds each site's verbatim `quote` into its notes (provenance).
- When research_status == "done", REPLACES the muni's stale Phase-1 candidate rows
  (verification_status='needs-human-review') with the agent's verified set, so we
  don't leave duplicates. For "blocked" munis, existing rows are left untouched.

Usage: python3 scripts/ingest_verify.py findings/verify/<slug>.json [more...] [--quiet]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import connect
from add_site import muni_id
from ingest import ingest_one

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> DB municipality name (invert verify_assignments.json; add any extras)
_assign = json.load(open(os.path.join(ROOT, "sources", "verify_assignments.json")))
SLUG2NAME = {v["slug"]: name for name, v in _assign.items()}


def resolve_name(path, rec, conn):
    slug = os.path.splitext(os.path.basename(path))[0]
    name = SLUG2NAME.get(slug) or rec.get("municipality")
    # validate against DB
    try:
        muni_id(conn, name)
    except ValueError:
        raise SystemExit(f"!! cannot resolve DB muni for {path} (slug={slug}, "
                         f"rec={rec.get('municipality')!r})")
    return name


def prep(rec):
    for s in rec.get("sites") or []:
        q = s.pop("quote", None)
        if q:
            note = (s.get("notes") or "").rstrip()
            s["notes"] = (note + " " if note else "") + f'[src quote: "{q.strip()}"]'
        for k in ("block", "lot"):
            if isinstance(s.get(k), str) and s[k].strip().lower() in ("", "n/a", "tbd", "none", "unknown"):
                s[k] = None
    return rec


def summary(rec):
    ob = rec.get("obligation") or {}
    comp = rec.get("compliance") or {}
    print(f"\n=== {rec['municipality']} === status={rec.get('research_status')}")
    print(f"  oblig: PN={ob.get('present_need')} Prosp={ob.get('prospective_need')} "
          f"RDP={ob.get('rdp')} unmet={ob.get('unmet_need')} total={ob.get('total_obligation')}")
    print(f"  compliance={comp.get('status')} hefsp={comp.get('hefsp_status')} adopted={comp.get('hefsp_adopted_date')}")
    for s in rec.get("sites") or []:
        print(f"   - {s.get('site_name')!r} blk={s.get('block')} lot={s.get('lot')} "
              f"| {s.get('total_units')}u/{s.get('affordable_units')}aff "
              f"| sa={s.get('set_aside_pct')} dens={s.get('density')} | {s.get('mechanism')} "
              f"| {s.get('confidence')}/{s.get('verification_status')}")


def main():
    args = [a for a in sys.argv[1:] if a != "--quiet"]
    quiet = "--quiet" in sys.argv
    conn = connect()
    for path in args:
        rec = json.load(open(path))
        recs = rec if isinstance(rec, list) else [rec]
        for r in recs:
            name = resolve_name(path, r, conn)
            r["municipality"] = name
            prep(r)
            # replace stale Phase-1 candidate rows when we have a verified result
            if (r.get("research_status") == "done") and (r.get("sites")):
                mid = muni_id(conn, name)
                conn.execute("DELETE FROM sites WHERE municipality_id=? AND "
                             "verification_status='needs-human-review'", (mid,))
                conn.commit()
            if not quiet:
                summary(r)
            n = ingest_one(conn, r)
            if not quiet:
                print(f"  -> ingested {n} sites for {name}")
    conn.close()


if __name__ == "__main__":
    main()
