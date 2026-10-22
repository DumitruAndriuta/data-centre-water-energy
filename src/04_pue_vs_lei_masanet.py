"""Google's 2025 facility PUE vs Lei & Masanet (2022) best-practice PUE by climate zone.

Model output: UE.xlsx from github.com/nuoaleon/Data-Center-Water-footprint (5th-percentile PUE =
'best practice'). Case 1 = airside economiser + adiabatic cooling (low water); Case 2 = waterside
economiser, water-cooled chiller (water intensive). Both are the large-data-centre archetypes.

Council Bluffs and The Dalles have two PUE campuses. Primary rule: simple mean (no capacity weights
exist); sensitivity: each campus separately. Climate zones: pre-2021 map and IECC 2021 (Midlothian
3A -> 2A, New Albany 5A -> 4A).
"""
import pandas as pd
from common import DATA, OUT, CACHE, UE_URL, download

ue = pd.read_excel(download(UE_URL, CACHE / "UE.xlsx"))
ue.columns = ["PUE", "WUE", "zone", "case", "quantile"]
best = ue[ue["quantile"] == "5th"].pivot(index="zone", columns="case", values="PUE")

g = pd.read_csv(DATA / "google_pue_2025_by_campus.csv").fillna({"campus": ""})


def compare(g, zone_col, label):
    g = g.copy()
    g["case1_best"] = g[zone_col].map(best[1]).round(3)
    g["case2_best"] = g[zone_col].map(best[2]).round(3)
    g["beats_case1"] = g.pue_2025 < g.case1_best
    g["beats_case2"] = g.pue_2025 < g.case2_best
    # site level, simple mean over campuses
    site = (g.groupby("site", as_index=False)
              .agg(pue_2025=("pue_2025", "mean"), zone=(zone_col, "first")))
    site["case1_best"] = site.zone.map(best[1])
    site["case2_best"] = site.zone.map(best[2])
    site["beats_case1"] = site.pue_2025 < site.case1_best
    site["beats_case2"] = site.pue_2025 < site.case2_best
    print(f"\n== {label}")
    print(f"site level (simple mean over campuses): beat Case 1 {site.beats_case1.sum()} of {len(site)}; "
          f"beat Case 2 {site.beats_case2.sum()} ({', '.join(site[site.beats_case2].site)})")
    print(f"campus level (each campus separately):  beat Case 1 {g.beats_case1.sum()} of {len(g)}; "
          f"beat Case 2 {g.beats_case2.sum()}")
    print("misses Case 1:", "; ".join(f"{r.site} {r.campus} ({r.pue_2025} vs {r.case1_best})".replace('  ', ' ')
                                      for r in g[~g.beats_case1].itertuples()))
    return g


a = compare(g, "climate_zone_pre2021", "pre-2021 climate zones")
b = compare(g, "climate_zone_iecc2021", "IECC 2021 climate zones")
a.to_csv(OUT / "pue_vs_model_campus_level_pre2021.csv", index=False)
b.to_csv(OUT / "pue_vs_model_campus_level_iecc2021.csv", index=False)
print("\nbest-practice PUE by zone (Case 1 / Case 2):")
print(best[[1, 2]].round(3).T.to_string())
