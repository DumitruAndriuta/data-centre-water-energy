"""Water scarcity analysis on the 2022-2025 facility panel joined to Aqueduct (08).

Numerators: Water Stress (withdrawal-based) x withdrawal; Water Depletion (consumption-based) x consumption.
  Q1  share of water from stressed / depleted basins
  Q2  growth 2022 -> 2025, raw vs scarcity-weighted
  Q3  stated cooling method vs water stress
  A   within-site PUE and consumption change 2022 -> 2025 (descriptive)
No 2021: Google publishes no 2021 facility water table.
"""
import pandas as pd
from common import DATA, OUT

pd.set_option("display.width", 200)
w = pd.read_csv(DATA / "panel_water_merged_2022_2025.csv")
aq = pd.read_csv(OUT / "aqueduct_join_all.csv")
agg = pd.read_csv(DATA / "water_aggregates_reconciliation.csv")
aq = aq[(aq.bws_score >= 0) & (aq.bwd_score >= 0)]          # drop -9999 No Data
d = w.merge(aq[["site", "status", "bws_score", "bwd_score"]], left_on="location", right_on="site", how="left")
assert d.bws_score.notna().all(), d[d.bws_score.isna()].location.unique()
d["W"], d["C"] = d.withdrawal_Mgal, d.consumption_Mgal
d["W_stress"], d["C_depl"] = d.W * d.bws_score, d.C * d.bwd_score
d.to_csv(OUT / "scarcity_weighted_panel.csv", index=False)
out = []
def p(s=""): print(s); out.append(s)

p("=== Coverage: named sites as share of printed data-centre total ===")
for y in range(2022, 2026):
    t = agg[(agg.year == y) & agg.location.str.startswith("Data")]
    p(f"{y}: withdrawal {d[d.year==y].W.sum()/t.withdrawal_Mgal.iloc[0]*100:4.1f}%  consumption {d[d.year==y].C.sum()/t.consumption_Mgal.iloc[0]*100:4.1f}%")

p("\n=== Q1: share of water from stressed / depleted basins (all named sites) ===")
for y in range(2022, 2026):
    s = d[d.year == y]
    p(f"{y}: withdrawal from High+ stress (bws>=3) {s[s.bws_score>=3].W.sum()/s.W.sum()*100:5.1f}%   "
      f"consumption from depletion >=2 {s[s.bwd_score>=2].C.sum()/s.C.sum()*100:5.1f}%   "
      f"withdrawal from depletion >=2 {s[s.bwd_score>=2].W.sum()/s.W.sum()*100:5.1f}%")
p("Google self-reported (freshwater withdrawal, high risk of depletion or scarcity): 15% (2023), 14% (2024), 13% (2025).")

p("\n=== Q2: growth 2022 -> 2025, raw vs scarcity-weighted (sites present both years) ===")
both = set(d[d.year == 2022].location) & set(d[d.year == 2025].location)
b = d[d.location.isin(both)]
g = b.groupby("year")[["W", "W_stress", "C", "C_depl"]].sum()
for c in g: p(f"{c:9s} {g.loc[2022,c]:9,.0f} -> {g.loc[2025,c]:9,.0f}  x{g.loc[2025,c]/g.loc[2022,c]:.2f}")
p(f"(n={len(both)} sites)")
p("By stress band (withdrawal growth):")
for lo, hi, lab in [(0, 1, "Low <1"), (1, 3, "Medium 1-3"), (3, 99, "High 3+")]:
    s = b[(b.bws_score >= lo) & (b.bws_score < hi)]
    a22, a25 = s[s.year == 2022].W.sum(), s[s.year == 2025].W.sum()
    p(f"  {lab:11s} n={s.location.nunique():2d}  {a22:7,.0f} -> {a25:7,.0f}  x{a25/a22:.2f}")
p("New sites entering after 2022 (2025 withdrawal, stress score):")
new = d[(d.year == 2025) & ~d.location.isin(both)].sort_values("W", ascending=False)
for _, r in new.iterrows(): p(f"  {r.location:24s} {r.W:7.1f}  bws {r.bws_score:.2f}")
s25 = d[d.year == 2025]; s22 = d[d.year == 2022]
p(f"Withdrawal-weighted mean stress, all named sites: 2022 {(s22.W_stress.sum()/s22.W.sum()):.2f} -> 2025 {(s25.W_stress.sum()/s25.W.sum()):.2f}")

p("\n=== Q3: stated cooling method vs water stress (one row per site) ===")
cool = {"Dublin, Ireland": "air", "Storey County, NV": "air", "Montreal, Canada": "air", "Pflugerville, TX": "air",
        "Phoenix, AZ": "air", "San Bernardo, Chile": "air", "Sydney, Australia": "air", "Wilmer, TX": "air",
        "Mesa, AZ": "air (planned)", "Hamina, Finland": "seawater", "St. Ghislain, Belgium": "industrial/canal",
        "Eemshaven, Netherlands": "industrial/canal", "Douglas County, GA": "reclaimed wastewater"}
sites = d.drop_duplicates("location")[["location", "bws_score"]].copy()
sites["cooling"] = sites.location.map(cool).fillna("unstated")
sites["group"] = sites.cooling.map(lambda c: "air-cooled" if c.startswith("air") else ("unstated" if c == "unstated" else "non-potable source"))
for gname, s in sites.groupby("group"):
    p(f"  {gname:18s} n={len(s):2d}  mean stress {s.bws_score.mean():.2f}  median {s.bws_score.median():.2f}  share in High+ (>=3) {(s.bws_score>=3).mean()*100:3.0f}%")
air = sites[sites.group == "air-cooled"].sort_values("bws_score", ascending=False)
strict = sites[sites.location != "Mesa, AZ"]
for gname, s in strict.groupby("group"):
    p(f"  STRICT (Mesa excluded: not footnoted air-cooled in g2026) {gname:18s} n={len(s):2d}  mean stress {s.bws_score.mean():.2f}  share High+ {(s.bws_score>=3).mean()*100:3.0f}%") if gname != "air-cooled" else p(f"  STRICT air-cooled (8 footnoted) n={(strict.cooling=='air').sum()}  mean stress {strict[strict.cooling=='air'].bws_score.mean():.2f}  share High+ {(strict[strict.cooling=='air'].bws_score>=3).mean()*100:3.0f}%")
p("  air-cooled sites: " + "; ".join(f"{r.location} {r.bws_score:.2f}" for _, r in air.iterrows()))
big = d[(d.year == 2025)].groupby("location").W.sum()
p("  Caveat: every air-cooled site is small. 2025 withdrawal, air-cooled total "
  f"{big[air.location].sum():.1f} Mgal vs {big.sum():,.0f} Mgal all named sites.")

p("\n=== Question A: within-site change 2022 -> 2025 (sites with PUE both years) ===")
pue = {"Berkeley County, SC": (1.10, 1.09), "Council Bluffs, IA": None, "Douglas County, GA": (1.09, 1.09), "Dublin, Ireland": (1.09, 1.08),
       "Eemshaven, Netherlands": (1.07, 1.07), "Fredericia, Denmark": (1.12, 1.07), "Hamina, Finland": (1.09, 1.10),
       "Henderson, NV": (1.11, 1.09), "Jackson County, AL": (1.12, 1.10), "Lenoir, NC": (1.09, 1.10), "Mayes County, OK": (1.10, 1.12),
       "Midlothian, TX": (1.16, 1.10), "Montgomery County, TN": (1.11, 1.09), "New Albany, OH": (1.14, 1.06),
       "Papillion, NE": (1.13, 1.09), "Quilicura, Chile": (1.09, 1.08), "St. Ghislain, Belgium": (1.09, 1.08), "The Dalles, OR": None}
rows = []
for loc, v in pue.items():
    if v is None or loc not in both: continue
    c22 = d[(d.location == loc) & (d.year == 2022)].C.iloc[0]; c25 = d[(d.location == loc) & (d.year == 2025)].C.iloc[0]
    rows.append((loc, v[0], v[1], c22, c25, c25 / c22))
qa = pd.DataFrame(rows, columns=["site", "pue22", "pue25", "C22", "C25", "growth"]).sort_values("growth", ascending=False)
p(qa.round(2).to_string(index=False))
core = qa[~qa.site.isin(["Dublin, Ireland", "Hamina, Finland"])]
p(f"PUE improved {(qa.pue25<qa.pue22).sum()}/{len(qa)}, flat {(qa.pue25==qa.pue22).sum()}, worse {(qa.pue25>qa.pue22).sum()}; "
  f"water rose at {(qa.growth>1).sum()}/{len(qa)}; median growth {qa.growth.median():.2f}x "
  f"(excl. Dublin/Hamina tiny bases: {core.growth.median():.2f}x)")
p("Council Bluffs and The Dalles excluded here: two PUE campuses, one water row (see aggregation rule).")
(OUT / "scarcity_results.txt").write_text("\n".join(out))
