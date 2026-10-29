#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/src"
python 01_check_panel.py
python 02_fleet_wue.py
python 03_water_growth.py
python 04_pue_vs_lei_masanet.py      # downloads UE.xlsx on first run
python 05_lei2023_type1_samples.py   # downloads three sample workbooks on first run
python 06_im3_footprint_energy.py    # downloads the IM3 atlas GeoPackage on first run
python 07_footprint_wue_rescale.py
python 08_aqueduct_join.py           # downloads Aqueduct 4.0 (261 MB) on first run
python 09_basin_boundary_check.py
python 10_scarcity_analysis.py
python 11_q1_freshwater.py
python 12_ashburn_sensitivity.py
