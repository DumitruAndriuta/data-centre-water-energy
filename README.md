# Google data centres: water, PUE and published models

> **Status: unpublished research in progress. Do not make this repository public, or cite results from it,
> without the agreement of all project members.**

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

Not in this repository: the WRI Aqueduct scarcity join, the PNNL IM3 footprint-energy estimates and the
footprint rescaling test, and the PDF PUE extraction. Those scripts belong to the co-author's project folder.

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

## Run

```bash
pip install -r requirements.txt
./run_all.sh
```

Outputs are written to `outputs/`.

## Limitations

- One firm's voluntary disclosure, so selection bias towards efficient operators.
- Site water only; indirect water is about three-quarters of the footprint (Siddik et al. 2021).
- No facility-level energy is published, so facility-level WUE cannot be computed directly.
- Lei & Masanet validated their model partly on Google 2020 data. The panel here is 2021-2025, so it is out of sample.
- The within-site comparison is descriptive: site load growth is not observed, so it is not an efficiency claim.
- About 10% of Google's data-centre water is in unlocated "Other" sites.
- Gross consumption is used; Google's water replenishment is not netted off.

## AI assistance

Data transcription, validation scripts and analysis were developed with Claude (Anthropic). Key values were
checked against the source PDFs.

## References

- Lei, N. & Masanet, E. (2022). Climate- and technology-specific PUE and WUE estimations for U.S. data centers
  using a hybrid statistical and thermodynamics-based approach. *Resources, Conservation and Recycling* 182.
- Siddik, M. A. B., Shehabi, A. & Marston, L. (2021). The environmental footprint of data centers in the United
  States. *Environmental Research Letters* 16, 064017.
- Lei, N. et al. (2023). Geospatial assessment of water footprints for hyperscale data centers in the United
  States. *J. Phys.: Conf. Ser.* 2600, 172003.
- Google Environmental Reports 2023-2026.
