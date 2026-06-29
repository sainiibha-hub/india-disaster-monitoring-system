"""
config.py
Central configuration for the India Disaster Monitoring System.

All secrets (DB password, API keys) are read from environment variables.
Copy `.env.example` to `.env` and fill in your own values, or export the
variables in your shell before running the system.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present)
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# MySQL database configuration
# --------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}
DB_NAME = os.getenv("DB_NAME", "india_disaster_monitoring")

# --------------------------------------------------------------------------
# External API configuration
# --------------------------------------------------------------------------

# OpenWeatherMap is used as the live data source for rainfall / temperature /
# humidity per district. Get a free key at https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# USGS Earthquake catalog - free, public, no key required.
USGS_EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Rough bounding box around the Indian subcontinent, used to filter the
# global USGS feed down to events relevant to India and its neighbourhood.
INDIA_BOUNDING_BOX = {
    "minlatitude": 6.0,
    "maxlatitude": 38.0,
    "minlongitude": 68.0,
    "maxlongitude": 98.0,
}
EARTHQUAKE_MIN_MAGNITUDE = float(os.getenv("EARTHQUAKE_MIN_MAGNITUDE", "5.0"))
EARTHQUAKE_LOOKBACK_DAYS = int(os.getenv("EARTHQUAKE_LOOKBACK_DAYS", "30"))

# CWC (Central Water Commission) does not currently expose a simple, stable
# public REST API for real-time river gauge levels, and IMD does not expose
# a public REST API for cyclone advisories either. This system is built so
# real feeds can be dropped in with zero code changes elsewhere:
#   - If FLOOD_API_URL / CYCLONE_API_URL are set, the system will call them.
#   - If they are NOT set, the system simulates realistic readings around
#     each station's known normal/warning/danger levels so that the rest of
#     the pipeline (storage, alerting, dashboard, reports) is fully runnable
#     and testable end-to-end without external credentials.
FLOOD_API_URL = os.getenv("FLOOD_API_URL", "")
CYCLONE_API_URL = os.getenv("CYCLONE_API_URL", "")

# --------------------------------------------------------------------------
# River gauge stations: name, nearest state/district, and threshold levels
# (in metres) used to classify flood severity. These are indicative sample
# values for demo purposes -- replace with the official CWC danger levels
# for each station before using this in any real decision-making context.
# --------------------------------------------------------------------------
RIVER_STATIONS = [
    {"river": "Yamuna", "station": "Delhi", "state": "Delhi",
     "lat": 28.6139, "lon": 77.2090,
     "normal_level": 204.50, "warning_level": 205.33, "danger_level": 207.49},
    {"river": "Ganga", "station": "Varanasi", "state": "Uttar Pradesh",
     "lat": 25.3176, "lon": 82.9739,
     "normal_level": 60.00, "warning_level": 70.26, "danger_level": 71.26},
    {"river": "Brahmaputra", "station": "Guwahati", "state": "Assam",
     "lat": 26.1445, "lon": 91.7362,
     "normal_level": 48.50, "warning_level": 49.68, "danger_level": 50.50},
    {"river": "Godavari", "station": "Bhadrachalam", "state": "Telangana",
     "lat": 17.6688, "lon": 80.8930,
     "normal_level": 36.00, "warning_level": 43.00, "danger_level": 53.00},
    {"river": "Krishna", "station": "Vijayawada", "state": "Andhra Pradesh",
     "lat": 16.5062, "lon": 80.6480,
     "normal_level": 9.00, "warning_level": 12.00, "danger_level": 15.50},
    {"river": "Mahanadi", "station": "Cuttack", "state": "Odisha",
     "lat": 20.4625, "lon": 85.8830,
     "normal_level": 10.50, "warning_level": 13.50, "danger_level": 14.50},
    {"river": "Tapi", "station": "Surat", "state": "Gujarat",
     "lat": 21.1702, "lon": 72.8311,
     "normal_level": 16.00, "warning_level": 26.00, "danger_level": 30.50},
    {"river": "Periyar", "station": "Kochi", "state": "Kerala",
     "lat": 9.9312, "lon": 76.2673,
     "normal_level": 4.50, "warning_level": 7.00, "danger_level": 8.50},
    {"river": "Sutlej", "station": "Ludhiana", "state": "Punjab",
     "lat": 30.9010, "lon": 75.8573,
     "normal_level": 240.00, "warning_level": 244.00, "danger_level": 246.00},
    {"river": "Narmada", "station": "Hoshangabad", "state": "Madhya Pradesh",
     "lat": 22.7500, "lon": 77.7167,
     "normal_level": 280.00, "warning_level": 286.00, "danger_level": 289.00},
]

# Threshold (mm in a single reading window) above which a rainfall reading
# is treated as "extreme" for dashboard highlighting purposes.
HEAVY_RAINFALL_THRESHOLD_MM = float(os.getenv("HEAVY_RAINFALL_THRESHOLD_MM", "65"))

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
DISTRICTS_FILE = os.path.join(BASE_DIR, "data", "india_states_districts.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# Scheduler
# --------------------------------------------------------------------------
DAILY_RUN_TIME = os.getenv("DAILY_RUN_TIME", "06:00")  # 24h HH:MM, local time

# --------------------------------------------------------------------------
# Flask dashboard
# --------------------------------------------------------------------------
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
