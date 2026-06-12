"""
Export the current database state to human-readable artifacts in reports/:
  - inventory.csv      : one row per site (the acquisition target list)
  - inventory.md       : grouped-by-municipality site inventory
  - STATUS.md          : per-municipality research progress + obligation summary

Safe to run any time; reflects whatever is currently in db/bergen.db.
"""
import csv
import os
from db import connect, now, ROOT

REPORTS = os.path.join(ROOT, "reports")

SITE_COLS = [
    "municipality", "site_name", "address", "block", "lot", "acreage",
    "mechanism", "current_zoning", "proposed_zoning", "density",
    "total_units", "affordable_units", "set_aside_pct", "tenure",
    "adoption_status", "developer", "confidence", "verification_status",
    "source_url", "source_page", "source_date", "notes",
]


def export_csv(conn):
    rows = conn.execute(f"""
        SELECT m.name AS municipality, s.site_name, s.address, s.block, s.lot,
               s.acreage, s.mechanism, s.current_zoning, s.proposed_zoning,
               s.density, s.total_units, s.affordable_units, s.set_aside_pct,
               s.tenure, s.adoption_status, s.developer, s.confidence,
               s.verification_status, s.source_url, s.source_page,
               s.source_date, s.notes
        FROM sites s JOIN municipalities m ON m.id = s.municipality_id
        ORDER BY m.name, s.block, s.lot
    """).fetchall()
    path = os.path.join(REPORTS, "inventory.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(SITE_COLS)
        for r in rows:
            w.writerow([r[c] for c in SITE_COLS])
    return len(rows), path


def export_status(conn):
    munis = conn.execute("""
        SELECT *, (SELECT COUNT(*) FROM sites s WHERE s.municipality_id=m.id) AS nsites
        FROM municipalities m ORDER BY m.name
    """).fetchall()
    path = os.path.join(REPORTS, "STATUS.md")
    done = sum(1 for m in munis if m["research_status"] == "done")
    inprog = sum(1 for m in munis if m["research_status"] == "in_progress")
    blocked = sum(1 for m in munis if m["research_status"] == "blocked")
    total_sites = conn.execute("SELECT COUNT(*) c FROM sites").fetchone()["c"]
    with open(path, "w") as f:
        f.write("# Bergen County Fourth Round Inventory — Research Status\n\n")
        f.write(f"_Generated {now()}_\n\n")
        f.write(f"- Municipalities: **{len(munis)}/70**  "
                f"(done: {done}, in_progress: {inprog}, blocked: {blocked}, "
                f"not_started: {len(munis)-done-inprog-blocked})\n")
        f.write(f"- Sites catalogued: **{total_sites}**\n\n")
        f.write("| # | Municipality | Status | Sites | Oblig. | Compliance | HEFSP | Last researched |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for i, m in enumerate(munis, 1):
            f.write(f"| {i} | {m['name']} | {m['research_status']} | {m['nsites']} | "
                    f"{m['total_obligation'] if m['total_obligation'] is not None else ''} | "
                    f"{m['compliance_status'] or ''} | {m['hefsp_status'] or ''} | "
                    f"{m['last_researched'] or ''} |\n")
    return path


def export_inventory_md(conn):
    path = os.path.join(REPORTS, "inventory.md")
    munis = conn.execute("""
        SELECT m.* , (SELECT COUNT(*) FROM sites s WHERE s.municipality_id=m.id) AS nsites
        FROM municipalities m
        WHERE EXISTS (SELECT 1 FROM sites s WHERE s.municipality_id=m.id)
        ORDER BY m.name
    """).fetchall()
    with open(path, "w") as f:
        f.write("# Bergen County Fourth Round (2025-2035) Affordable Housing Site Inventory\n\n")
        f.write(f"_Generated {now()}. Contract-and-entitle townhome target list._\n\n")
        f.write("> Every site traces to a cited source. `verification_status` and "
                "`confidence` flag rows needing human review before any contract action.\n\n")
        for m in munis:
            f.write(f"## {m['name']} ({m['muni_type']})\n\n")
            meta = []
            if m["total_obligation"] is not None:
                meta.append(f"Obligation: {m['total_obligation']}")
            if m["compliance_status"]:
                meta.append(f"Compliance: {m['compliance_status']}")
            if m["hefsp_status"]:
                meta.append(f"HEFSP: {m['hefsp_status']} {m['hefsp_adopted_date'] or ''}".strip())
            if meta:
                f.write("_" + " · ".join(meta) + "_\n\n")
            sites = conn.execute(
                "SELECT * FROM sites WHERE municipality_id=? ORDER BY block, lot",
                (m["id"],)).fetchall()
            f.write("| Site | Address | Block | Lot | Acres | Mechanism | Density | Units | Aff. | Set-aside | Tenure | Status | Conf. | Source |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
            for s in sites:
                src = f"[doc]({s['source_url']})" if s["source_url"] else ""
                f.write(f"| {s['site_name'] or ''} | {s['address'] or ''} | "
                        f"{s['block'] or ''} | {s['lot'] or ''} | "
                        f"{s['acreage'] if s['acreage'] is not None else ''} | "
                        f"{s['mechanism'] or ''} | "
                        f"{s['density'] if s['density'] is not None else ''} | "
                        f"{s['total_units'] if s['total_units'] is not None else ''} | "
                        f"{s['affordable_units'] if s['affordable_units'] is not None else ''} | "
                        f"{(str(s['set_aside_pct'])+'%') if s['set_aside_pct'] is not None else ''} | "
                        f"{s['tenure'] or ''} | {s['adoption_status'] or ''} | "
                        f"{s['confidence'] or ''} | {src} |\n")
            f.write("\n")
    return path


def main():
    conn = connect()
    n, csvp = export_csv(conn)
    sp = export_status(conn)
    ip = export_inventory_md(conn)
    print(f"Exported {n} sites -> {csvp}")
    print(f"Status -> {sp}")
    print(f"Inventory -> {ip}")
    conn.close()


if __name__ == "__main__":
    main()
