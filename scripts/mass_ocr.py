"""Pre-OCR each municipality's primary HEFSP to sources/ocr/<slug>.txt.

Reads sources/bergen_hefsp_pick.json (slug -> primary doc url). Skips files that
already exist and are non-trivial. Prints one progress line per muni so a Monitor
can stream completion. Idempotent.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetchpdf import fetch_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR_DIR = os.path.join(ROOT, "sources", "ocr")
os.makedirs(OCR_DIR, exist_ok=True)

pick = json.load(open(os.path.join(ROOT, "sources", "bergen_hefsp_pick.json")))
# slugs handled by hand (gaps) — skip in mass pass
SKIP = {"carlstadt-boro", "lodi-boro", "lyndhurst-twp", "northvale-boro"}

only = set(sys.argv[1:])  # optional: restrict to given slugs

for slug, url in pick.items():
    if slug in SKIP:
        continue
    if only and slug not in only:
        continue
    out = os.path.join(OCR_DIR, slug + ".txt")
    if os.path.exists(out) and os.path.getsize(out) > 1500:
        print(f"SKIP {slug} (cached {os.path.getsize(out)}b)", flush=True)
        continue
    try:
        txt = fetch_text(url)
        with open(out, "w") as f:
            f.write(f"SOURCE_URL: {url}\n")
            f.write(txt)
        print(f"OK   {slug} {len(txt)}b -> {os.path.basename(out)}", flush=True)
    except Exception as e:
        print(f"FAIL {slug} {type(e).__name__}: {e}", flush=True)
print("MASS_OCR_DONE", flush=True)
