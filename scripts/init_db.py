"""
Initialize (idempotently) the SQLite schema for the Bergen County Fourth Round
(2025-2035) Mount Laurel affordable-housing site inventory, and seed the canonical
list of all 70 Bergen County municipalities.

Re-running this script is safe: tables use IF NOT EXISTS and municipality seeding
uses INSERT OR IGNORE on the unique name, so existing research is never clobbered.
"""
from db import connect, now

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS municipalities (
    id                   INTEGER PRIMARY KEY,
    name                 TEXT NOT NULL UNIQUE,
    muni_type            TEXT,            -- Borough / Township / City / Village
    county               TEXT DEFAULT 'Bergen',
    -- Fourth Round obligation (DCA methodology / court-adopted)
    present_need         INTEGER,         -- rehabilitation share
    prospective_need     INTEGER,         -- new-construction fair share (10yr)
    rdp                  INTEGER,         -- Realistic Development Potential
    unmet_need           INTEGER,
    total_obligation     INTEGER,
    obligation_source_url TEXT,
    -- Compliance pathway
    compliance_status    TEXT,            -- settled / litigating / immune / builders-remedy / vacant-land-adj / JOC / unknown
    settlement_date      TEXT,
    settlement_party     TEXT,            -- FSHC / named intervenor(s)
    hefsp_status         TEXT,            -- none / draft / adopted / amended
    hefsp_adopted_date   TEXT,
    hefsp_url            TEXT,
    -- Research workflow (resumability)
    research_status      TEXT DEFAULT 'not_started',  -- not_started / in_progress / done / blocked
    sites_found          INTEGER DEFAULT 0,
    last_researched      TEXT,
    notes                TEXT
);

CREATE TABLE IF NOT EXISTS sources (
    id               INTEGER PRIMARY KEY,
    municipality_id  INTEGER REFERENCES municipalities(id),
    doc_type         TEXT,   -- HEFSP / settlement / consent-order / mediation / ordinance / redevelopment-plan / news / DCA / FSHC / other
    title            TEXT,
    url              TEXT UNIQUE,
    retrieved_at     TEXT,
    excerpt          TEXT,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS sites (
    id               INTEGER PRIMARY KEY,
    municipality_id  INTEGER NOT NULL REFERENCES municipalities(id),
    site_name        TEXT,
    address          TEXT,
    block            TEXT,
    lot              TEXT,
    acreage          REAL,
    -- Zoning / compliance mechanism
    mechanism        TEXT,   -- inclusionary-rezoning / overlay / redevelopment-area / RDP-site / 100pct-affordable / municipal / group-home / accessory-apt / other
    current_zoning   TEXT,
    proposed_zoning  TEXT,
    density          REAL,   -- units per acre
    total_units      INTEGER,
    affordable_units INTEGER,
    set_aside_pct    REAL,
    tenure           TEXT,   -- rental / for-sale / mixed
    -- Status
    adoption_status  TEXT,   -- proposed / draft-plan / adopted-ordinance / approved / under-construction / built
    developer        TEXT,
    -- Provenance (load-bearing: every site must trace to a source)
    source_id        INTEGER REFERENCES sources(id),
    source_url       TEXT,
    source_page      TEXT,
    source_date      TEXT,
    confidence       TEXT DEFAULT 'medium',     -- high / medium / low
    verification_status TEXT DEFAULT 'unverified', -- verified / unverified / needs-human-review
    notes            TEXT,
    created_at       TEXT,
    updated_at       TEXT
);

CREATE TABLE IF NOT EXISTS research_log (
    id            INTEGER PRIMARY KEY,
    ts            TEXT,
    municipality  TEXT,
    action        TEXT,
    detail        TEXT
);

CREATE INDEX IF NOT EXISTS idx_sites_muni ON sites(municipality_id);
CREATE INDEX IF NOT EXISTS idx_sources_muni ON sources(municipality_id);
CREATE INDEX IF NOT EXISTS idx_muni_status ON municipalities(research_status);
"""

# All 70 Bergen County, NJ municipalities (stable public record).
# (name, type)
BERGEN_MUNIS = [
    ("Allendale", "Borough"), ("Alpine", "Borough"), ("Bergenfield", "Borough"),
    ("Bogota", "Borough"), ("Carlstadt", "Borough"), ("Cliffside Park", "Borough"),
    ("Closter", "Borough"), ("Cresskill", "Borough"), ("Demarest", "Borough"),
    ("Dumont", "Borough"), ("East Rutherford", "Borough"), ("Edgewater", "Borough"),
    ("Elmwood Park", "Borough"), ("Emerson", "Borough"), ("Englewood", "City"),
    ("Englewood Cliffs", "Borough"), ("Fair Lawn", "Borough"), ("Fairview", "Borough"),
    ("Fort Lee", "Borough"), ("Franklin Lakes", "Borough"), ("Garfield", "City"),
    ("Glen Rock", "Borough"), ("Hackensack", "City"), ("Harrington Park", "Borough"),
    ("Hasbrouck Heights", "Borough"), ("Haworth", "Borough"), ("Hillsdale", "Borough"),
    ("Ho-Ho-Kus", "Borough"), ("Leonia", "Borough"), ("Little Ferry", "Borough"),
    ("Lodi", "Borough"), ("Lyndhurst", "Township"), ("Mahwah", "Township"),
    ("Maywood", "Borough"), ("Midland Park", "Borough"), ("Montvale", "Borough"),
    ("Moonachie", "Borough"), ("New Milford", "Borough"), ("North Arlington", "Borough"),
    ("Northvale", "Borough"), ("Norwood", "Borough"), ("Oakland", "Borough"),
    ("Old Tappan", "Borough"), ("Oradell", "Borough"), ("Palisades Park", "Borough"),
    ("Paramus", "Borough"), ("Park Ridge", "Borough"), ("Ramsey", "Borough"),
    ("Ridgefield", "Borough"), ("Ridgefield Park", "Village"), ("Ridgewood", "Village"),
    ("River Edge", "Borough"), ("River Vale", "Township"), ("Rochelle Park", "Township"),
    ("Rockleigh", "Borough"), ("Rutherford", "Borough"), ("Saddle Brook", "Township"),
    ("Saddle River", "Borough"), ("South Hackensack", "Township"), ("Teaneck", "Township"),
    ("Tenafly", "Borough"), ("Teterboro", "Borough"), ("Upper Saddle River", "Borough"),
    ("Waldwick", "Borough"), ("Wallington", "Borough"), ("Washington Township", "Township"),
    ("Westwood", "Borough"), ("Wood-Ridge", "Borough"), ("Woodcliff Lake", "Borough"),
    ("Wyckoff", "Township"),
]


def main():
    conn = connect()
    conn.executescript(SCHEMA)
    for name, mtype in BERGEN_MUNIS:
        conn.execute(
            "INSERT OR IGNORE INTO municipalities(name, muni_type) VALUES (?,?)",
            (name, mtype),
        )
    conn.commit()
    conn.execute(
        "INSERT INTO meta(key,value) VALUES ('initialized_at', ?) "
        "ON CONFLICT(key) DO NOTHING",
        (now(),),
    )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) c FROM municipalities").fetchone()["c"]
    print(f"Schema ready. Municipalities seeded: {n} (expected 70)")
    assert n == 70, f"Expected 70 Bergen municipalities, got {n}"
    conn.close()


if __name__ == "__main__":
    main()
