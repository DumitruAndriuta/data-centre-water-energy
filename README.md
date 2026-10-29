# Google data centres: water, PUE and published models

Code and data behind a project testing published models of data centre water and energy use
(Lei & Masanet 2022; Siddik et al. 2021; Lei et al. 2023) against what Google discloses at facility level
in its Environmental Reports (2023-2026 editions).

Research question: *how well do published models of data centre water and energy performance match
disclosed facility data, and where do they systematically diverge?*

## What is in this repository

| Path | What it does |
|---|---|
| `data/panel_water_merged_2022_2025.csv` | Facility water (withdrawal, discharge, consumption, million gallons), 2022-2025 |
| `data/water_aggregates_reconciliation.csv` | Printed data-centre totals and the "Other data center locations" rows |
| `data/fleet_inputs.csv` | Fleet electricity, PUE, global water and printed totals, by year |
| `data/google_pue_2025_by_campus.csv` | 2025 PUE by campus for 15 US sites, with climate zones (pre-2021 map and IECC 2021) |
| `data/google_pue_2022_2025_selected.csv` | PUE in 2022 and 2025 for the 16 sites used in the within-site comparison |
| `src/01_check_panel.py` | Integrity checks on the water panel |
| `src/02_fleet_wue.py` | Rebuilds fleet WUE and compares it with Siddik (2021) and the EU EED |
| `src/03_water_growth.py` | Within-site PUE and water change, 2022 to 2025 (descriptive) |
| `src/04_pue_vs_lei_masanet.py` | Google PUE against Lei & Masanet's best-practice PUE, with a campus-level sensitivity |
| `src/05_lei2023_type1_samples.py` | Exploratory summary of the Lei et al. (2023) simulation samples |
| `data/site_coordinates_all.csv` | Coordinates for all 40 named water sites, with verification status and source |
| `src/06_im3_footprint_energy.py` | IT energy per US site from PNNL IM3 building footprints (100 W/sq ft, 60% utilisation) |
| `src/07_footprint_wue_rescale.py` | Rescales footprint energy to fleet IT energy and tests the spread of site-level WUE |
| `src/08_aqueduct_join.py` | Joins every site to WRI Aqueduct 4.0 basins (water stress, depletion), with distance to basin edge |
| `src/09_basin_boundary_check.py` | Score range of every basin within 3 km of near-boundary sites |
| `src/10_scarcity_analysis.py` | Q1 share from stressed basins, Q2 scarcity-weighted growth, Q3 cooling method vs stress |
| `src/11_q1_freshwater.py` | Q1 on Google's freshwater-withdrawal basis |
| `src/12_ashburn_sensitivity.py` | Ashburn location sensitivity for Q1 and Q2 |
| `verify/` | Source audit: `fetch_reports.py` downloads the four report PDFs and writes their text; `check_water.py` and `check_pue.py` look up every panel value in it; `pdf_rows.py` prints a page as table rows |
| `posters/` | Poster summarising the results (`data_centre_water_energy_poster.pdf`, with its PowerPoint source) |

## Data provenance

- All water and PUE values come from the public Google Environmental Reports (editions 2023, 2024, 2025, 2026).
  Each edition gives five years of facility PUE and one year of facility water; the 2023 report covers 2022,
  the 2024 report 2023, the 2025 report 2024 and the 2026 report 2025. Google publishes no 2021 facility water table.
- The 2022 and 2023 water values were transcribed from the report tables with AI assistance (no automated parser;
  the PDF text layer for those tables is broken). They were checked by reconciliation (below) and by the co-author's
  independent comparison of every panel value against the PDFs.
- Two 2024 consumption values were originally corrupted by footnote digits (Douglas County GA 2366.9 and
  Quilicura 2121.8). The printed values are 366.9 and 121.8.
- Data-centre electricity uses the 2026 edition throughout. Google restated 2021-2024 electricity downward by
  0.6-1.3% between editions (`dc_electricity_MWh_as_first_printed` in `fleet_inputs.csv`).
- Third-party reference values are set in `src/common.py`: Siddik et al. (2021) 1.8 m3/MWh (per total facility
  electricity) and C = 5 cooling cycles; EU EED 2024 data (COM(2026) 500): 770 sites, PUE 1.36, WUE 0.58 L/kWh per IT energy.
- `04` and `05` download the model files from the authors' GitHub repositories on first run.
- `06` downloads the IM3 Open Source Data Center Atlas v2026.02.09 (doi 10.57931/3017294, ODbL) from MSD-LIVE's
  anonymous S3 access point; `08`, `09` and `12` download WRI Aqueduct 4.0 (261 MB). Both go to `data/external/`.
- Aqueduct `*_raw` fields carry 9999 sentinels and `*_score` fields can carry -9999 for No Data basins, so only
  scores >= 0 are used. Aqueduct does not model interbasin transfers, which matters for canal- or utility-supplied sites.
- Site coordinates: "Columbus, Ohio" in the PUE table is Lockbourne, OH; "Bristol, Virginia" in the 2026 PDF is
  Google's typo for Bristow, VA; Sterling is the Arcola campus. Every candidate Ashburn location falls in the same
  Low-stress basin (`12`).

## Results reproduced by the scripts

| Result | Value |
|---|---|
| Water panel | 128 site-years; withdrawal - discharge = consumption on every row |
| Reconciliation | Sites plus "Other" match printed totals for 2022, 2023, 2025 and within 0.4 Mgal (rounding) for 2024 |
| Fleet WUE (L/kWh, per IT kWh), 2022-2025 | 1.054, 1.059, 1.049, 1.024 (2021 is an estimate only) |
| Earlier series | 2021-2024 used global water x 0.968 (2025 data-centre share), not facility totals; 2022 was 1.088 |
| Versus Siddik (2021) | About 52-54% of 1.8 on a per-facility-kWh basis |
| Versus EU EED (2024) | Google 2024 WUE is about 1.8x the EU average of 0.58 |
| Discharge share of withdrawal | 20-22% (Siddik's cooling-tower assumption implies 20%) |
| Within-site, 16 sites, 2022-2025 | PUE improved at 11, flat at 2, worse at 3; water rose at 14 of 16; median 1.69x |
| PUE vs Lei & Masanet Case 1 | Google beats best-practice PUE at 14 of 15 sites (simple mean) and 14 of 17 campuses |
| PUE vs Lei & Masanet Case 2 | 3 sites on the mean (New Albany, Omaha, Lancaster); 5 campuses at campus level |
| Q1, freshwater withdrawal from High+ stress basins | 12.2% (2023), 12.6% (2024), 13.9% (2025), vs Google's own 15%, 14%, 13% |
| Q2, growth 2022-2025, 23 continuing sites | Neutral: withdrawal x1.83, stress-weighted x1.86, consumption x1.84, depletion-weighted x1.81 |
| Q3, cooling vs stress | 9 air-cooled sites, mean stress 3.05 (56% High+), vs 1.62 for unstated; all small, under 1% of 2025 withdrawal. Strict (8 footnoted, no Mesa): 2.80, 50% |
| Basin boundaries | The 10 sites within 3 km of a basin edge keep their category for every basin within 3 km |
| Ashburn forced to High stress | Q1 moves by under 1 point, Q2 not at all |
| Facility WUE, footprint energy rescaled | 8 well-covered US sites span 0.49-1.44 L/kWh (3.0x), all under Case 2; matching fleet WUE needs about 3.1x the 100 W/sq ft assumption, so only the spread is tested |
| Source audit | All 384 panel water values and the 42 PUE values used found in the PDFs; no PUE restated across editions |

## Run

```bash
pip install -r requirements.txt
./run_all.sh
```

Outputs are written to `outputs/`. For the source audit:

```bash
cd verify
python fetch_reports.py   # about 66 MB of PDFs, first run only
python check_water.py
python check_pue.py
```

## Limitations

- One firm's voluntary disclosure, so selection bias towards efficient operators.
- Site water only; indirect water is about three-quarters of the footprint (Siddik et al. 2021).
- No facility-level energy is published, so facility-level WUE cannot be computed directly.
- Lei & Masanet validated their model partly on Google 2020 data. The panel here is 2021-2025, so it is out of sample.
- The within-site comparison is descriptive: site load growth is not observed, so it is not an efficiency claim.
- About 10% of Google's data-centre water is in unlocated "Other" sites.
- Gross consumption is used; Google's water replenishment is not netted off.

## References

- Lei, N. & Masanet, E. (2022). Climate- and technology-specific PUE and WUE estimations for U.S. data centers
  using a hybrid statistical and thermodynamics-based approach. *Resources, Conservation and Recycling* 182.
- Siddik, M. A. B., Shehabi, A. & Marston, L. (2021). The environmental footprint of data centers in the United
  States. *Environmental Research Letters* 16, 064017.
- Lei, N. et al. (2023). Geospatial assessment of water footprints for hyperscale data centers in the United
  States. *J. Phys.: Conf. Ser.* 2600, 172003.
- Google Environmental Reports 2023-2026.
