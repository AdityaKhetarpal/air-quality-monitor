## extraction is done here
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DIRTY_READINGS_CSV = DATA_DIR / "readings_dirty.csv"       # path to messy file
CLEAN_READINGS_CSV = DATA_DIR / "readings_dirty_cleaned.csv"  # path to cleaned version of data
LIVE_READINGS_CSV = DATA_DIR / "readings_live.csv"
DB_PATH = DATA_DIR / "readings.db"

RANDOM_SEED = 42

CITIES = [
    {"name": "Delhi",     "lat": 28.6139, "lon": 77.2090},
    {"name": "Mumbai",    "lat": 19.0760, "lon": 72.8777},
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    {"name": "Kolkata",   "lat": 22.5726, "lon": 88.3639},
    {"name": "Chennai",   "lat": 13.0827, "lon": 80.2707},
]

# api config
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
REQUEST_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3

# risk threshold numbers
PM25_BREACH_THRESHOLD = 15.0
PM25_OUTLIER_THRESHOLD = 500.0

REFERENCE_DATE = "2026-07-08"