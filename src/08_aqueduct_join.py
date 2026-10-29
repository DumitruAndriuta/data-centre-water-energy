"""Join every named Google water site to WRI Aqueduct 4.0 basins (baseline annual).

Uses *_score fields only (raw fields carry 9999 sentinels; scores can carry -9999 for No Data basins,
filtered downstream). Also records the distance to the basin edge for the boundary check (09).
Downloads Aqueduct on first run (261 MB).
"""
import geopandas as gpd, pandas as pd
from shapely.geometry import Point
from common import DATA, OUT, aqueduct_gdb

COLS = ["string_id", "name_0", "name_1", "bws_score", "bws_label", "bwd_score", "bwd_label",
        "w_awr_def_tot_score", "w_awr_def_tot_label"]
aq = gpd.read_file(aqueduct_gdb(), layer="baseline_annual", columns=COLS, engine="pyogrio")
aq = aq.dissolve(by="string_id", as_index=False, aggfunc="first") if aq.string_id.duplicated().any() else aq

sites = pd.read_csv(DATA / "site_coordinates_all.csv")
pts = gpd.GeoDataFrame(sites, geometry=[Point(xy) for xy in zip(sites.lon, sites.lat)], crs=4326)
j = gpd.sjoin(pts, aq, how="left", predicate="within").drop(columns="index_right")
aq_m = aq.set_index("string_id").to_crs(3857)
pts_m = pts.to_crs(3857)
j["km_to_basin_edge"] = [round(pts_m.geometry.iloc[i].distance(aq_m.loc[sid].geometry.boundary) / 1000, 1)
                         if isinstance(sid, str) else None for i, sid in enumerate(j.string_id)]
out = j.drop(columns="geometry")
out.to_csv(OUT / "aqueduct_join_all.csv", index=False)
print(out[["site", "status", "bws_score", "bwd_score", "km_to_basin_edge"]].round(2).to_string())
