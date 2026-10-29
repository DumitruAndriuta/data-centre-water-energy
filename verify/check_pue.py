"""Parse facility PUE tables from all four editions (run fetch_reports.py first); check every PUE used in
the analysis and look for cross-edition restatements."""
import re
from fetch_reports import REPORTS

NUM = re.compile(r"^(\d\.\d\d?|-)$")
def parse(e):
    L = [l.strip() for l in (REPORTS / f"{e}.txt").read_text(encoding="utf8", errors="ignore").splitlines()]
    out = {}
    for i, l in enumerate(L):
        if l == "PUE" and i + 5 < len(L) and all(NUM.match(L[i + k]) for k in range(1, 6)):
            name = " ".join(x for x in L[max(0, i - 2):i] if x and not NUM.match(x) and x != "PUE")
            out[name] = [None if L[i + k] == "-" else float(L[i + k]) for k in range(1, 6)]
    return out
first_year = {"g2023": 2018, "g2024": 2019, "g2025": 2020, "g2026": 2021}
T = {e: parse(e) for e in first_year}
for e in T: print(e, len(T[e]), "rows")
def get(e, key, y):
    hits = [v for k, v in T[e].items() if key.lower() in k.lower()]
    if len(hits) != 1: return f"?{len(hits)} matches"
    return hits[0][y - first_year[e]]
used = {  # values used in analysis: (key, year): value
 ("Berkeley County", 2025): 1.09, ("Council Bluffs, Iowa (1st", 2025): 1.11, ("Council Bluffs, Iowa (2nd", 2025): 1.08,
 ("The Dalles, Oregon (1st", 2025): 1.10, ("The Dalles, Oregon (2nd", 2025): 1.06, ("Douglas County", 2025): 1.09,
 ("Henderson", 2025): 1.09, ("Jackson County", 2025): 1.10, ("Lenoir", 2025): 1.10, ("Mayes County", 2025): 1.12,
 ("Midlothian", 2025): 1.10, ("Montgomery County", 2025): 1.09, ("New Albany", 2025): 1.06, ("Papillion", 2025): 1.09,
 ("Storey County", 2025): 1.14, ("Omaha", 2025): 1.05, ("Lancaster", 2025): 1.04, ("Columbus", 2025): 1.06, ("Bristol", 2025): 1.09,
 ("Storey County", 2023): 1.19,
 ("Berkeley County", 2022): 1.10, ("Douglas County", 2022): 1.09, ("Dublin", 2022): 1.09, ("Eemshaven", 2022): 1.07,
 ("Fredericia", 2022): 1.12, ("Hamina", 2022): 1.09, ("Henderson", 2022): 1.11, ("Jackson County", 2022): 1.12,
 ("Lenoir", 2022): 1.09, ("Mayes County", 2022): 1.10, ("Midlothian", 2022): 1.16, ("Montgomery County", 2022): 1.11,
 ("New Albany", 2022): 1.14, ("Papillion", 2022): 1.13, ("Quilicura", 2022): 1.09, ("St. Ghislain", 2022): 1.09,
 ("Dublin", 2025): 1.08, ("Eemshaven", 2025): 1.07, ("Fredericia", 2025): 1.07, ("Hamina", 2025): 1.10, ("Quilicura", 2025): 1.08, ("St. Ghislain", 2025): 1.08,
}
bad = 0
for (k, y), v in used.items():
    got = {e: get(e, k, y) for e in T if first_year[e] <= y <= first_year[e] + 4}
    vals = {g for g in got.values() if isinstance(g, float)}
    status = "OK" if vals == {v} else "CHECK"
    if status != "OK": bad += 1
    print(f"{status:5s} {k:30s} {y} used {v}  pdf {got}")
print("mismatches:", bad)
print("Fredericia 2021 / New Albany 2021 in g2026:", get("g2026", "Fredericia", 2021), get("g2026", "New Albany", 2021))
fleet = [k for k in T["g2026"] if "fleet" in k.lower() or "campuses" in k.lower()]
print("fleet rows g2026:", {k: T["g2026"][k] for k in fleet})
# restatements: any site-year differing across editions
diffs = []
for e1 in T:
    for e2 in T:
        if e1 >= e2: continue
        for k in T[e1]:
            if k in T[e2]:
                for y in range(first_year[e2], first_year[e1] + 5):
                    a, b = T[e1][k][y - first_year[e1]], T[e2][k][y - first_year[e2]]
                    if a is not None and b is not None and a != b: diffs.append((k, y, e1, a, e2, b))
print("cross-edition PUE restatements:", diffs or "none")
