"""Within-site change 2022 -> 2025: PUE vs water consumption (Question A, descriptive).

Sites with PUE in both years and one water row (Council Bluffs and The Dalles have two PUE
campuses and one water row, so they are excluded). Fredericia/Hamina/Dublin have tiny or
ramping bases; the median is reported with and without Dublin and Hamina.
This is a description, not an efficiency claim: site load growth is not observed.
"""
import pandas as pd
from common import DATA, OUT

w = pd.read_csv(DATA / "panel_water_merged_2022_2025.csv")
c = w.pivot_table(index="location", columns="year", values="consumption_Mgal")
pue = pd.read_csv(DATA / "google_pue_2022_2025_selected.csv").set_index("water_location")

d = pue.join(c[[2022, 2025]].rename(columns={2022: "C22", 2025: "C25"}))
d["growth"] = d.C25 / d.C22
d["pue_change"] = (d.pue_2025 - d.pue_2022).round(2)
d["pue_direction"] = d.pue_change.apply(lambda x: "improved" if x < 0 else ("worse" if x > 0 else "flat"))
print(d.sort_values("growth", ascending=False).round(2).to_string())

print("\nPUE:", d.pue_direction.value_counts().to_dict())
print(f"water rose at {(d.growth > 1.0).sum()} of {len(d)} sites (flat: "
      f"{', '.join(d.index[d.growth == 1.0])})")
print(f"median growth: {d.growth.median():.2f}x; "
      f"excluding Dublin and Hamina: {d.drop(['Dublin, Ireland', 'Hamina, Finland']).growth.median():.2f}x")

# fixed-weight growth for all continuing sites (no PUE needed)
both = c.dropna(subset=[2022, 2025])
print(f"\nall {len(both)} continuing sites: total consumption "
      f"{both[2022].sum():.0f} -> {both[2025].sum():.0f} Mgal ({both[2025].sum() / both[2022].sum():.2f}x)")
d.round(3).to_csv(OUT / "question_a_within_site.csv")
