"""Print report pages as reconstructed table rows (words grouped into 3 pt bands), for reading the tables
whose text layer comes out one cell per line.

    python pdf_rows.py g2025 110,111
"""
import sys
import pymupdf
from fetch_reports import REPORTS

f = sys.argv[1]; pages = [int(x) for x in sys.argv[2].split(",")]
d = pymupdf.open(REPORTS / f"{f}.pdf")
for p in pages:
    print("#### ", f, "PAGE", p)
    words = d[p - 1].get_text("words")
    rows = {}
    for w in words:
        y = round((w[1] + w[3]) / 2 / 3)  # 3pt buckets
        rows.setdefault(y, []).append(w)
    for y in sorted(rows):
        ws = sorted(rows[y], key=lambda w: w[0])
        print(" ".join(w[4] for w in ws))
