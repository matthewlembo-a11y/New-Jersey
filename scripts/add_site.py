"""
Helpers to record verified research into the database during a research run.

Import and call these from per-municipality research steps. Every insert is
idempotent-ish: sources dedupe on URL; sites dedupe on (municipality, block, lot,
site_name) so re-running a municipality updates rather than duplicates.

Usage (from scripts/ dir):
    from add_site import muni_id, set_muni, add_source, add_site
"""
from db import connect, now, log


def muni_id(conn, name):
    row = conn.execute("SELECT id FROM municipalities WHERE name=?", (name,)).fetchone()
    if not row:
        raise ValueError(f"Unknown municipality: {name!r}")
    return row["id"]


def set_muni(conn, name, **fields):
    """Update municipality-level fields (obligation, compliance, hefsp, status)."""
    if not fields:
        return
    fields["last_researched"] = now()
    cols = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [name]
    conn.execute(f"UPDATE municipalities SET {cols} WHERE name=?", vals)
    conn.commit()


def add_source(conn, name, doc_type, title, url, excerpt="", notes=""):
    mid = muni_id(conn, name)
    conn.execute(
        """INSERT INTO sources(municipality_id, doc_type, title, url, retrieved_at, excerpt, notes)
           VALUES (?,?,?,?,?,?,?)
           ON CONFLICT(url) DO UPDATE SET
             doc_type=excluded.doc_type, title=excluded.title,
             excerpt=excluded.excerpt, notes=excluded.notes""",
        (mid, doc_type, title, url, now(), excerpt, notes),
    )
    conn.commit()
    row = conn.execute("SELECT id FROM sources WHERE url=?", (url,)).fetchone()
    return row["id"] if row else None


def add_site(conn, name, **f):
    """Insert or update a site. Dedupe key: (municipality, block, lot, site_name)."""
    mid = muni_id(conn, name)
    block = f.get("block")
    lot = f.get("lot")
    site_name = f.get("site_name")
    existing = conn.execute(
        """SELECT id FROM sites WHERE municipality_id=?
           AND IFNULL(block,'')=IFNULL(?,'') AND IFNULL(lot,'')=IFNULL(?,'')
           AND IFNULL(site_name,'')=IFNULL(?,'')""",
        (mid, block, lot, site_name),
    ).fetchone()

    allowed = {
        "site_name", "address", "block", "lot", "acreage", "mechanism",
        "current_zoning", "proposed_zoning", "density", "total_units",
        "affordable_units", "set_aside_pct", "tenure", "adoption_status",
        "developer", "source_id", "source_url", "source_page", "source_date",
        "confidence", "verification_status", "notes",
    }
    data = {k: v for k, v in f.items() if k in allowed}

    if existing:
        data["updated_at"] = now()
        cols = ", ".join(f"{k}=?" for k in data)
        conn.execute(f"UPDATE sites SET {cols} WHERE id=?",
                     list(data.values()) + [existing["id"]])
        sid = existing["id"]
    else:
        data["municipality_id"] = mid
        data["created_at"] = now()
        data["updated_at"] = now()
        cols = ", ".join(data.keys())
        ph = ", ".join("?" for _ in data)
        cur = conn.execute(f"INSERT INTO sites({cols}) VALUES ({ph})", list(data.values()))
        sid = cur.lastrowid
    conn.commit()
    # keep the denormalized site count fresh
    conn.execute(
        "UPDATE municipalities SET sites_found=(SELECT COUNT(*) FROM sites WHERE municipality_id=?) WHERE id=?",
        (mid, mid))
    conn.commit()
    return sid
