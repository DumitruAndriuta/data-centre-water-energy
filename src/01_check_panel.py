"""Integrity checks on the facility water panel (2022-2025).

Checks
  1. withdrawal - discharge = consumption on every row (tolerance 0.25 Mgal for rounding)
  2. site rows + 'Other data center locations' reconcile to the printed data-centre totals
  3. named-site coverage of printed totals
"""
import pandas as pd
from common import DATA

panel = pd.read_csv(DATA / "panel_water_merged_2022_2025.csv")
agg = pd.read_csv(DATA / "water_aggregates_reconciliation.csv")

# 1. row identity
panel["resid"] = (panel.withdrawal_Mgal - panel.discharge_Mgal - panel.consumption_Mgal).round(2)
bad = panel[panel.resid.abs() > 0.25]
print(f"rows: {len(panel)}; rows failing W - D = C (tol 0.25): {len(bad)}")
assert bad.empty, bad
assert not panel.duplicated(["location", "year"]).any(), "duplicate site-year"

# 2. totals
tot = agg[agg.location == "Data centers total"].set_index("year")
oth = agg[agg.location.str.startswith("Other")].set_index("year")
print("\nconsumption: sum of sites + 'Other' vs printed total (Mgal)")
for y in sorted(panel.year.unique()):
    s = panel.loc[panel.year == y, "consumption_Mgal"].sum()
    o = oth.consumption_Mgal.get(y, float("nan"))
    t = tot.consumption_Mgal.get(y, float("nan"))
    print(f"  {y}: sites {s:8.1f} + other {o:7.1f} = {s + o:8.1f} | printed {t:8.1f} | diff {s + o - t:+.1f}"
          f" | {int((panel.year == y).sum())} sites")
    assert abs(s + o - t) < 1.0, f"{y} does not reconcile"

# 3. coverage
print("\nnamed-site share of printed total")
for y in sorted(panel.year.unique()):
    for col, tcol in [("withdrawal_Mgal", "withdrawal_Mgal"), ("consumption_Mgal", "consumption_Mgal")]:
        share = panel.loc[panel.year == y, col].sum() / tot[tcol].get(y)
        print(f"  {y} {col.split('_')[0]:<11s} {100 * share:5.1f}%")
