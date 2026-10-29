"""Download the four Google Environmental Report editions and write their text layer (PyMuPDF,
one '=====PAGE n=====' marker per page) for check_water.py and check_pue.py.
Output: data/external/reports/g2023..g2026.pdf and .txt (git-ignored)."""
import sys
from pathlib import Path
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common import CACHE, download

REPORTS = CACHE / "reports"
URLS = {
    "g2023": "https://www.gstatic.com/gumdrop/sustainability/google-2023-environmental-report.pdf",
    "g2024": "https://www.gstatic.com/gumdrop/sustainability/google-2024-environmental-report.pdf",
    "g2025": "https://www.gstatic.com/gumdrop/sustainability/google-2025-environmental-report.pdf",
    "g2026": "https://sustainability.google/files/google-2026-environmental-report.pdf",
}

if __name__ == "__main__":
    REPORTS.mkdir(exist_ok=True)
    for e, url in URLS.items():
        pdf = download(url, REPORTS / f"{e}.pdf")
        txt = REPORTS / f"{e}.txt"
        if not txt.exists():
            doc = pymupdf.open(pdf)
            txt.write_text("".join(f"\n=====PAGE {i + 1}=====\n" + p.get_text() for i, p in enumerate(doc)), encoding="utf8")
        print(e, pdf.stat().st_size, "bytes ->", txt.name)
