#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/src"
python 01_check_panel.py
python 02_fleet_wue.py
python 03_water_growth.py
python 04_pue_vs_lei_masanet.py      # downloads UE.xlsx on first run
python 05_lei2023_type1_samples.py   # downloads three sample workbooks on first run
