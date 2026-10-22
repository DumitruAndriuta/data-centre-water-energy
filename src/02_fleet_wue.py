"""Rebuild Google's fleet-level WUE from printed facility-table totals.

WUE here is per IT kWh (the standard definition and the EU EED basis):
    WUE = water (L) / IT energy (kWh),  IT energy = data-centre electricity / PUE

The earlier (v1) series used global water x 0.968 for 2021-2024 instead of the facility sums.
0.968 is the 2025 data-centre share (10,523 / 10,869). This script tests that and rebuilds the series.
Also compares against Siddik et al. (2021) and the EU EED, and checks Google's discharge share
against Siddik's cooling-tower blowdown assumption.
"""
import pandas as pd
from common import (DATA, OUT, GAL_TO_L, SIDDIK_DIRECT_WATER_L_PER_KWH_FACILITY,
                    SIDDIK_COOLING_CYCLES, EED_2024)

f = pd.read_csv(DATA / "fleet_inputs.csv").set_index("year")
SHARE_2025 = f.loc[2025, "dc_consumption_printed_Mgal"] / f.loc[2025, "global_water_consumption_Mgal"]
print(f"2025 data-centre share of global consumption: {SHARE_2025:.4f}")

# 1. does v1 equal global x 0.968?
f["global_x_share2025"] = (f.global_water_consumption_Mgal * round(SHARE_2025, 3)).round(0)
print("\nv1 water vs global x 0.968 (Mgal)")
print(f[["v1_dc_water_Mgal", "global_x_share2025"]].to_string())

# 2. rebuild
f["dc_water_Mgal"] = f.dc_consumption_printed_Mgal.fillna(f.global_x_share2025)
f["basis"] = f.dc_consumption_printed_Mgal.notna().map({True: "printed facility-table total",
                                                         False: "ESTIMATE global x 0.968"})
it_kwh_M = f.dc_electricity_MWh_g2026 / f.fleet_PUE / 1000          # million kWh of IT energy
f["WUE_L_per_kWh_IT"] = f.dc_water_Mgal * GAL_TO_L / it_kwh_M
f["WUE_L_per_kWh_facility"] = f.dc_water_Mgal * GAL_TO_L / (f.dc_electricity_MWh_g2026 / 1000)
f["share_of_global"] = f.dc_water_Mgal / f.global_water_consumption_Mgal

# 3. comparisons
f["frac_of_Siddik_1.8_(facility_basis)"] = f.WUE_L_per_kWh_facility / SIDDIK_DIRECT_WATER_L_PER_KWH_FACILITY
f["discharge_share_of_withdrawal"] = f.dc_discharge_printed_Mgal / f.dc_withdrawal_printed_Mgal
blowdown_share = (1 / (SIDDIK_COOLING_CYCLES - 1)) / (1 + 1 / (SIDDIK_COOLING_CYCLES - 1))
print(f"\nSiddik blowdown (C={SIDDIK_COOLING_CYCLES}) implies discharge = {100 * blowdown_share:.0f}% of withdrawal")

show = ["dc_water_Mgal", "v1_WUE_L_per_kWh_IT", "WUE_L_per_kWh_IT", "WUE_L_per_kWh_facility",
        "frac_of_Siddik_1.8_(facility_basis)", "discharge_share_of_withdrawal", "basis"]
print("\n", f[show].round(3).to_string())
eed = EED_2024["WUE_L_per_kWh_IT"]
print(f"\n2024 Google WUE / EU EED 2024 average ({eed}): {f.loc[2024, 'WUE_L_per_kWh_IT'] / eed:.2f}x")
print(f"2022-2025 change in WUE (printed-total years): "
      f"{100 * (f.loc[2025, 'WUE_L_per_kWh_IT'] / f.loc[2022, 'WUE_L_per_kWh_IT'] - 1):+.1f}% "
      f"(v1 series: {100 * (f.loc[2025, 'v1_WUE_L_per_kWh_IT'] / f.loc[2022, 'v1_WUE_L_per_kWh_IT'] - 1):+.1f}%)")

f.round(4).to_csv(OUT / "fleet_wue_rebuilt.csv")
print(f"\nwrote {OUT / 'fleet_wue_rebuilt.csv'}")
