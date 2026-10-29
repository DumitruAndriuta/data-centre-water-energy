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

# WRI Aqueduct 4.0 (261 MB zip; only the GDB is extracted)
AQUEDUCT_URL = "https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip"
AQUEDUCT_GDB = CACHE / "Aqueduct40_waterrisk_download_Y2023M07D05" / "GDB" / "Aq40_Y2023D07M05.gdb"
# PNNL IM3 Open Source Data Center Atlas v2026.02.09, doi 10.57931/3017294 (ODbL), MSD-LIVE S3 access point
IM3_RECORD = "p147s-4h760"
IM3_GPKG_KEY = "p147s-4h760/im3_open_source_data_center_atlas_v2026.02.09/im3_open_source_data_center_atlas_v2026.02.09.gpkg"

# Potable withdrawal (Mgal) where a report itemises non-potable / reclaimed water; everything else counts as fresh
POTABLE_WITHDRAWAL = {
    ("Douglas County, GA", 2022): 72.4, ("Douglas County, GA", 2023): 34.5, ("Douglas County, GA", 2024): 7.4, ("Douglas County, GA", 2025): 46.3,
    ("Eemshaven, Netherlands", 2022): 2.0, ("Eemshaven, Netherlands", 2023): 2.1, ("Eemshaven, Netherlands", 2024): 2.9, ("Eemshaven, Netherlands", 2025): 3.6,
    ("St. Ghislain, Belgium", 2022): 14.2, ("St. Ghislain, Belgium", 2023): 22.3, ("St. Ghislain, Belgium", 2024): 13.7, ("St. Ghislain, Belgium", 2025): 27.6}


def download(url: str, dest: Path) -> Path:
    """Download url to dest if not already cached."""
    import urllib.request
    if not dest.exists():
        print(f"downloading {url}")
        urllib.request.urlretrieve(url, dest)
    return dest


def aqueduct_gdb() -> Path:
    """Path to the Aqueduct 4.0 GDB, downloading and extracting it on first use."""
    import zipfile
    if not AQUEDUCT_GDB.exists():
        z = zipfile.ZipFile(download(AQUEDUCT_URL, CACHE / "aqueduct-4-0-water-risk-data.zip"))
        z.extractall(CACHE, members=[n for n in z.namelist() if ".gdb" in n])
    return AQUEDUCT_GDB


def im3_gpkg() -> Path:
    """Path to the IM3 atlas GeoPackage, downloading it from MSD-LIVE on first use."""
    from im3_s3 import get
    dest = CACHE / Path(IM3_GPKG_KEY).name
    if not dest.exists():
        print(f"downloading {IM3_GPKG_KEY} from MSD-LIVE")
        get(IM3_RECORD, IM3_GPKG_KEY, dest)
    return dest
