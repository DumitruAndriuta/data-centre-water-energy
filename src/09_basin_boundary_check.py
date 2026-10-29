"""Near-boundary sites: would a small coordinate error flip the basin category?
Takes every basin within a 3 km buffer of each site less than 3 km from a basin edge and reports the score range."""
import geopandas as gpd, pandas as pd
from shapely.geometry import Point
from common import OUT, aqueduct_gdb

aq = gpd.read_file(aqueduct_gdb(), layer="baseline_annual", columns=["string_id", "bws_score", "bws_label", "bwd_score", "bwd_label"], engine="pyogrio")
j = pd.read_csv(OUT / "aqueduct_join_all.csv")
near = j[j.km_to_basin_edge < 3].copy()
pts = gpd.GeoDataFrame(near, geometry=[Point(x, y) for x, y in zip(near.lon, near.lat)], crs=4326).to_crs(3857)
aqm = aq.to_crs(3857)
rows = []
for _, r in pts.iterrows():
    hits = aqm[aqm.intersects(r.geometry.buffer(3000))].drop_duplicates("string_id")
    rows.append({"site": r.site, "km_to_edge": r.km_to_basin_edge, "n_basins_3km": len(hits),
                 "bws_assigned": round(r.bws_score, 2), "bws_range": f"{hits.bws_score.min():.2f}-{hits.bws_score.max():.2f}",
                 "bws_labels": " | ".join(sorted(set(hits.bws_label))),
                 "bwd_assigned": round(r.bwd_score, 2), "bwd_range": f"{hits.bwd_score.min():.2f}-{hits.bwd_score.max():.2f}",
                 "bwd_labels": " | ".join(sorted(set(hits.bwd_label)))})
out = pd.DataFrame(rows)
out.to_csv(OUT / "boundary_check.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(out.to_string(index=False))
