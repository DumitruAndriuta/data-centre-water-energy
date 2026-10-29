"""Per-site IT energy estimates from building footprints in the PNNL IM3 Open Source Data Center Atlas
v2026.02.09 (doi 10.57931/3017294, building layer of the GeoPackage).

    IT MW = footprint sq ft x 100 W/sq ft;  IT MWh/yr = IT MW x 8760 x 60% utilisation

Sites with 2 or fewer Google buildings are flagged as likely undercounts. Downloads the GeoPackage on first run.
"""
import geopandas as gpd, pandas as pd
from common import OUT, im3_gpkg

GPKG = im3_gpkg()
b = gpd.read_file(GPKG, layer="building")
g = b[b.operator.fillna("").str.contains("google", case=False)].copy()
g = g.drop_duplicates(subset="id")  # buildings straddling county lines appear once per county with same id

def site_of(r):
    st, co, lat, lon = r.state_abb, r.county, r.lat, r.lon
    if st == "SC" and co == "Berkeley County": return "Berkeley County SC"
    if st == "IA" and co == "Pottawattamie County": return "Council Bluffs IA"
    if st == "NV" and co == "Clark County": return "Henderson NV"
    if st == "AL" and co == "Jackson County": return "Jackson County AL"
    if st == "TN" and co == "Montgomery County": return "Montgomery County TN"
    if st == "NE" and co == "Sarpy County": return "Papillion NE"
    if st == "NE" and co == "Douglas County": return "Omaha NE"
    if st == "OH" and co == "Fairfield County": return "Lancaster OH"
    if st == "OH" and lat > 40.0 and co in ("Franklin County", "Licking County"): return "New Albany OH"
    if st == "OH" and co == "Franklin County" and lat < 39.9: return "Lockbourne/Columbus OH"
    if st == "TX" and co == "Ellis County": return "Red Oak TX" if lon > -96.9 else "Midlothian TX"
    if st == "VA" and co == "Prince William County": return "Bristow VA"
    if st == "VA" and co == "Loudoun County": return "Leesburg VA" if lat > 39.0 else "Ashburn/Sterling VA (Arcola campus)"
    return f"Thornton CO (extra, not in target list)" if co == "Adams County" else f"UNMAPPED {co} {st}"
g["site"] = g.apply(site_of, axis=1)
g["county_st"] = g.county + "|" + g.state_abb

# county label from all rows (pre-dedup) so straddling sites list both counties
allg = b[b.operator.fillna("").str.contains("google", case=False)].copy()
allg = allg.merge(g[["id", "site"]], on="id")
counties = allg.groupby("site").county.apply(lambda s: "/".join(sorted(set(s))))

agg = g.groupby("site").agg(state=("state_abb", "first"), n_buildings=("id", "size"),
                            footprint_sqft=("sqft", "sum"), im3_ids=("id", lambda s: ";".join(sorted(s))))
agg["county"] = counties
order = ["Berkeley County SC","Council Bluffs IA","Douglas County GA","Henderson NV","Jackson County AL","Lenoir NC",
         "Mayes County OK","Midlothian TX","Montgomery County TN","New Albany OH","Papillion NE","Omaha NE","Lancaster OH",
         "Lockbourne/Columbus OH","Storey County NV","The Dalles OR","Ashburn/Sterling VA (Arcola campus)","Leesburg VA",
         "Bristow VA","Red Oak TX","New Haven IN","Mesa AZ"]
absent_meta = {"Douglas County GA":("Douglas County","GA"),"Lenoir NC":("Caldwell County","NC"),"Mayes County OK":("Mayes County","OK"),
               "Storey County NV":("Storey County","NV"),"The Dalles OR":("Wasco County","OR"),"New Haven IN":("Allen County","IN"),
               "Mesa AZ":("Maricopa County","AZ")}
rows = []
for s in order + [s for s in agg.index if s not in order]:
    if s in agg.index:
        r = agg.loc[s]; sq = float(r.footprint_sqft); n = int(r.n_buildings)
        mw = sq * 100 / 1e6
        rows.append(dict(site=s, county=r.county, state=r.state, n_buildings=n, footprint_sqft=round(sq),
                         it_mw_at_100w=round(mw, 1), it_mwh_yr_60pct=round(mw * 8760 * 0.60),
                         coverage_flag="likely_undercount_le2_bldgs" if n <= 2 else "ok", im3_ids=r.im3_ids))
    else:
        c, st = absent_meta[s]
        rows.append(dict(site=s, county=c, state=st, n_buildings=0, footprint_sqft="", it_mw_at_100w="",
                         it_mwh_yr_60pct="", coverage_flag="absent_no_google_building", im3_ids=""))
out = pd.DataFrame(rows)
out.to_csv(OUT / "footprint_energy_estimates.csv", index=False)
print(out.drop(columns="im3_ids").to_string(index=False))
print("raw google building rows:", len(allg), "unique ids:", g.id.nunique())
na = b[(b.operator.fillna("").str.contains("google", case=False)) & (b.lat > 40.0) & b.county.isin(["Franklin County","Licking County"])]
print("New Albany raw sum (with dup):", na.sqft.sum(), " deduped:", na.drop_duplicates("id").sqft.sum())

# side check: untagged buildings inside Google campus polygons
c = gpd.read_file(GPKG, layer="campus")
gc = c[c.operator.fillna("").str.contains("google", case=False) | c.name.fillna("").str.contains("google", case=False)].drop_duplicates("id")
other = b[~b.operator.fillna("").str.contains("google", case=False)].drop_duplicates("id")
j = gpd.sjoin(other.set_geometry(other.geometry.representative_point()), gc[["id","name","geometry"]], predicate="within")
print("non-Google-tagged buildings inside Google campuses:\n", j[["id_left","operator","name_left","sqft","name_right"]].to_string())
