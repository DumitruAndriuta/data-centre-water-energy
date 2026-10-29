"""Verify every row of the water panel against the PDF text of its source edition (run fetch_reports.py first).
A row passes if withdrawal, discharge and consumption all appear as numbers in that site's table block."""
import re, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common import DATA, POTABLE_WITHDRAWAL
from fetch_reports import REPORTS

P = pd.read_csv(DATA / "panel_water_merged_2022_2025.csv")
A = pd.read_csv(DATA / "water_aggregates_reconciliation.csv")
txt = {e: (REPORTS / f"{e}.txt").read_text(encoding="utf8", errors="ignore").splitlines() for e in ["g2023","g2024","g2025","g2026"]}
city = lambda loc: loc.split(",")[0].strip()
cities = sorted({city(l) for l in P.location} | {"Other data center", "Data centers total", "Total"}, key=len, reverse=True)
NUM = re.compile(r"^<?\d[\d,]*\.?\d*$")
def region(lines):
    s = next(i for i, l in enumerate(lines) if l.strip().startswith("Ashburn"))
    e = next(i for i in range(s, len(lines)) if lines[i].strip().startswith("Winschoten") or lines[i].strip().startswith("Wilmer") ) if any(x.strip().startswith(("Winschoten","Wilmer")) for x in lines[s:s+2000]) else s+1500
    return s, min(e + 60, len(lines))
def blocks(lines):
    s, e = region(lines); out = {}; cur = None
    for l in lines[s:e]:
        t = l.strip()
        hit = next((c for c in cities if t.startswith(c)), None)
        if hit and not NUM.match(t):
            cur = hit; out.setdefault(cur, {"nums": [], "labels": []}); continue
        if cur is None: continue
        if NUM.match(t.replace(" ", "")): out[cur]["nums"].append(t.replace(",", "").replace(" ", ""))
        elif re.search(r"(potable|reclaim|seawater|non-potable|wastewater|industrial|canal)", t, re.I): out[cur]["labels"].append(re.sub(r"\s*\d+\s*$", "", t))
    return out
B = {e: blocks(txt[e]) for e in txt}
fmt = lambda v: [f"{v:.1f}", f"{v:.2f}", f"{v:g}", f"{int(v)}" if v == int(v) else None]
bad, ok = [], 0
for _, r in P.iterrows():
    b = B[r.source_report].get(city(r.location))
    if b is None: bad.append((r.location, r.year, r.source_report, "SITE NOT FOUND")); continue
    for col in ["withdrawal_Mgal", "discharge_Mgal", "consumption_Mgal"]:
        v = r[col]
        if not any(f in b["nums"] for f in fmt(v) if f) and not (v < 1 and "<1" in b["nums"]):
            bad.append((r.location, r.year, r.source_report, f"{col}={v} not in {b['nums'][:8]}"))
        else: ok += 1
print(f"checked values OK: {ok}; problems: {len(bad)}")
for x in bad: print("  ", x)
print("\nsource labels by site/edition (non-trivial only):")
for e in B:
    for c, b in sorted(B[e].items()):
        labs = [l for l in b["labels"] if not l.lower().startswith("potable")]
        if labs: print(f"  {e} {c}: {sorted(set(b['labels']))}")

print("\n== potable splits and aggregates ==")
for (loc, y), v in POTABLE_WITHDRAWAL.items():
    c, e = city(loc), f"g{y + 1}"
    print(c, y, e, "potable", v, "OK" if f"{v:.1f}" in B[e][c]["nums"] else f"MISSING {B[e][c]['nums']}")
def find_after(lines, label, n=40):
    s,_ = region(lines)
    for i in range(s, len(lines)):
        if lines[i].strip().startswith(label): return [l.strip().replace(",","") for l in lines[i:i+n] if NUM.match(l.strip().replace(" ",""))][:12]
for e in txt:
    print(e, "Other:", find_after(txt[e], "Other data center"))
    print(e, "Total:", find_after(txt[e], "Data centers total") or find_after(txt[e], "Total"))
print(A.to_string())
