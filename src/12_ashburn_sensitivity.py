"""Ashburn, VA cannot be pinned to one facility. Check that every candidate location falls in the same basin,
then force Ashburn to High stress and report how far Q1 (freshwater basis) and Q2 move."""
import geopandas as gpd, pandas as pd
from shapely.geometry import Point
from common import OUT, POTABLE_WITHDRAWAL, aqueduct_gdb

aq = gpd.read_file(aqueduct_gdb(), layer="baseline_annual", columns=["string_id", "bws_score", "bws_label", "bwd_score"], engine="pyogrio")
pts = {"Arcola Bldg 1 (24400 Howling Rooster Ln, Sterling)": (38.9432045, -77.5243301),
       "Arcola Bldg 2 (24550 Howling Rooster Ln, Sterling)": (38.9418116, -77.5274514),
       "Ashburn town centre": (39.0437, -77.4875), "Ashburn east (Loudoun Tech Center area)": (39.03, -77.46)}
g = gpd.GeoDataFrame({"name": list(pts)}, geometry=[Point(lon, lat) for lat, lon in pts.values()], crs=4326)
j = gpd.sjoin(g, aq, predicate="within")
print(j[["name", "string_id", "bws_score", "bws_label", "bwd_score"]].round(2).to_string(index=False))
d = pd.read_csv(OUT / "scarcity_weighted_panel.csv")
d["W_fresh"] = [POTABLE_WITHDRAWAL.get((l, y), w) for l, y, w in zip(d.location, d.year, d.W)]   # Hamina kept: reported water excludes seawater
for label, ash in [("Ashburn Low (0.16)", 0.16), ("Ashburn High (3.59)", 3.59)]:
    x = d.copy(); x.loc[x.location == "Ashburn, VA", "bws_score"] = ash
    sh = {y: x[(x.year == y) & (x.bws_score >= 3)].W_fresh.sum() / x[x.year == y].W_fresh.sum() * 100 for y in range(2022, 2026)}
    both = set(x[x.year == 2022].location) & set(x[x.year == 2025].location); b = x[x.location.isin(both)]
    gs = (b[b.year == 2025].W * b[b.year == 2025].bws_score).sum() / (b[b.year == 2022].W * b[b.year == 2022].bws_score).sum()
    print(f"{label}: Q1 freshwater High+ share " + " ".join(f"{y}:{v:.1f}%" for y, v in sh.items()) + f" | Q2 stress-weighted growth x{gs:.2f}")
