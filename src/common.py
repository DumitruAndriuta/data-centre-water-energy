"""Shared paths and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE = ROOT / "data" / "external"  # downloaded third-party files (git-ignored)
OUT.mkdir(exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

GAL_TO_L = 3.78541

# Third-party reference values used for comparison (see README for sources)
SIDDIK_DIRECT_WATER_L_PER_KWH_FACILITY = 1.8   # Siddik et al. 2021, per total facility electricity
SIDDIK_COOLING_CYCLES = 5                      # cycles of concentration C in Siddik et al. 2021
EED_2024 = {"sites": 770, "PUE": 1.36, "WUE_L_per_kWh_IT": 0.58}  # COM(2026) 500, 2024 data

UE_URL = ("https://raw.githubusercontent.com/nuoaleon/Data-Center-Water-footprint/"
          "main/Simulation%20Results/UE.xlsx")
LEI2023_BASE = ("https://raw.githubusercontent.com/nuoaleon/"
                "Geospatial-assessment-of-water-footprints-for-hyperscale-data-centers-in-the-United-States/"
                "main/UE_samples/")


def download(url: str, dest: Path) -> Path:
    """Download url to dest if not already cached."""
    import urllib.request
    if not dest.exists():
        print(f"downloading {url}")
        urllib.request.urlretrieve(url, dest)
    return dest
