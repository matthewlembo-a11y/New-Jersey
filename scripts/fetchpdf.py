"""Download a PDF (with browser-like headers) and extract text via pypdf.

Usage:
    python3 scripts/fetchpdf.py <url> [out_txt_path]
If out_txt_path omitted, prints text to stdout.
Caches the raw PDF under sources/cache/<sha1>.pdf.
"""
import hashlib
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "sources", "cache")
os.makedirs(CACHE, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
}


def download(url):
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(CACHE, key + ".pdf")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return path


os.environ.setdefault("TESSDATA_PREFIX", "/usr/share/tesseract-ocr/5/tessdata")

import re
# court e-filing stamp lines (header/footer burned onto each page) — ignore when
# deciding whether a page has a real text layer vs. is a scanned image
_STAMP = re.compile(r"(?:BER-[A-Z]?-?\d|Trans ID:|Pg \d+ of \d+|LCV\d+)", re.I)


def _meaningful(text):
    keep = [ln for ln in text.splitlines() if ln.strip() and not _STAMP.search(ln)]
    return " ".join(keep).strip()


def extract_text(path, ocr=True, ocr_threshold=40, dpi=200):
    """Extract text. If a page's embedded text is shorter than ocr_threshold
    chars (scanned image page), fall back to Tesseract OCR for that page."""
    import fitz  # PyMuPDF
    doc = fitz.open(path)
    out = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        try:
            t = page.get_text("text") or ""
        except Exception as e:
            t = f"[page {i} extract error: {e}]"
        if ocr and len(_meaningful(t)) < ocr_threshold:
            try:
                tp = page.get_textpage_ocr(flags=0, dpi=dpi, full=True)
                t = page.get_text("text", textpage=tp) or t
            except Exception as e:
                t = t + f"\n[ocr error: {e}]"
        out.append(f"\n===== PAGE {i+1} =====\n{t}")
    doc.close()
    return "".join(out)


def fetch_text(url):
    return extract_text(download(url))


if __name__ == "__main__":
    url = sys.argv[1]
    txt = fetch_text(url)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            f.write(txt)
        print(f"wrote {len(txt)} chars to {sys.argv[2]}")
    else:
        sys.stdout.write(txt)
