"""Exploratory: distribution of PUE and site WUE in the Lei et al. (2023) physical-model samples.

The three workbooks in the authors' repo are quasi-random (Sobol) draws over facility parameters and
weather (outdoor temperature and humidity sampled across a wide range), NOT location-specific
and not climate-weighted. The percentiles below therefore describe the design space, not any site.
Type 1 = airside economiser + direct evaporative cooling + air-cooled chiller;
Type 2 = same economiser with water-cooled chiller; Type 3 = waterside economiser, water-cooled chiller.
Not used as evidence about Google's sites: there is no per-site energy, and Google's air-cooled sites
use no water for cooling whereas type 1 still humidifies ('negligible', not zero).
"""
import pandas as pd
from common import CACHE, LEI2023_BASE, download

files = {"type 1": "us_Adiabatic_AirChiller.xlsx",
         "type 2": "us_Adiabatic_WaterChiller.xlsx",
         "type 3": "us_WaterEconomizer_WaterChiller.xlsx"}
rows = []
for name, fn in files.items():
    d = pd.read_excel(download(LEI2023_BASE + fn, CACHE / fn))
    w, p = d["WUE"], d["PUE"]
    q = w.quantile([0.05, 0.5, 0.95])
    rows.append({"design": name, "n": len(d),
                 "WUE_p5": q[0.05], "WUE_median": q[0.5], "WUE_p95": q[0.95], "WUE_max": w.max(),
                 "share_WUE_zero": (w == 0).mean(), "PUE_median": p.median()})
out = pd.DataFrame(rows).set_index("design").round(3)
print(out.to_string())
