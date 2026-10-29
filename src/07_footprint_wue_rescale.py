"""Rescale footprint-based energy (06) to Google's disclosed fleet IT energy.

One multiplicative factor k cannot change ratios between sites, so the test is the SPREAD:
anchor the covered sites' aggregate WUE to the fleet WUE, then ask whether every site lands
in a physically plausible range (Lei & Masanet: ~0 for air/adiabatic up to ~1.8 L/kWh for
water-intensive Case 2). The level is fitted, not validated.
"""
import pandas as pd
from common import DATA, OUT, GAL_TO_L

fp = pd.read_csv(OUT / "footprint_energy_estimates.csv")
w = pd.read_csv(DATA / "panel_water_merged_2022_2025.csv")
w25 = w[w.year == 2025].set_index("location").consumption_Mgal
name = {"Berkeley County SC": "Berkeley County, SC", "Council Bluffs IA": "Council Bluffs, IA",
        "Henderson NV": "Henderson, NV", "Jackson County AL": "Jackson County, AL",
        "Midlothian TX": "Midlothian, TX", "Montgomery County TN": "Montgomery County, TN",
        "New Albany OH": "New Albany, OH", "Papillion NE": "Papillion, NE", "Omaha NE": "Omaha, NE",
        "Lancaster OH": "Lancaster, OH", "Lockbourne/Columbus OH": "Lockbourne, OH",
        "Leesburg VA": "Leesburg, VA", "Bristow VA": "Bristow, VA", "Red Oak TX": "Red Oak, TX"}
fp = fp[fp.site.isin(name)].copy()
fp["water_Mgal_2025"] = fp.site.map(name).map(w25)
fp = fp.dropna(subset=["water_Mgal_2025", "it_mwh_yr_60pct"])
fp["wue_raw"] = fp.water_Mgal_2025 * 1e6 * GAL_TO_L / (fp.it_mwh_yr_60pct * 1000)
FLEET_WUE_2025 = 1.024  # facility-table water / fleet IT energy, 2026 edition (outputs/fleet_wue_rebuilt.csv)
for label, sub in [("all covered", fp), ("ok coverage only", fp[fp.coverage_flag == "ok"])]:
    agg = sub.water_Mgal_2025.sum() * 1e6 * GAL_TO_L / (sub.it_mwh_yr_60pct.sum() * 1000)
    k = agg / FLEET_WUE_2025
    s = sub.assign(wue_rescaled=sub.wue_raw / k)
    print(f"\n== {label} (n={len(s)}): aggregate raw WUE {agg:.2f} L/kWh -> energy scale factor k={k:.2f}"
          f" (implied {100*k:.0f} W/sqft at 60% util)")
    print(s[["site", "coverage_flag", "water_Mgal_2025", "it_mwh_yr_60pct", "wue_raw", "wue_rescaled"]]
          .round(2).sort_values("wue_rescaled").to_string(index=False))
    print(f"spread max/min {s.wue_rescaled.max()/s.wue_rescaled.min():.1f}x;"
          f" sites above 1.8 L/kWh: {(s.wue_rescaled > 1.8).sum()}")
    s.to_csv(OUT / f"footprint_wue_rescaled_{'ok' if 'ok' in label else 'all'}.csv", index=False)
