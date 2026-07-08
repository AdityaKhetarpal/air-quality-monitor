##extraction is done here

import pathlib

BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

LIVE_READINGS_CSV = DATA_DIR / "readings_live.csv"

CITIES = [
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Mumbai",   "lat": 19.0760, "lon": 72.8777},
    {"name": "Bengaluru","lat": 12.9716, "lon": 77.5946},
    {"name": "Kolkata",  "lat": 22.5726, "lon": 88.3639},
    {"name": "Chennai",  "lat": 13.0827, "lon": 80.2707},
]

#api config

api = "https://air-quality-api.open-meteo.com/v1/air-quality"
timeout = 10
max_retries = 3

#risk threshold number

breach = 15.0
