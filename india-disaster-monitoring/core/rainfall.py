"""
core/rainfall.py

Fetches live rainfall / temperature / humidity for every district listed in
data/india_states_districts.json using the OpenWeatherMap "current weather"
endpoint, and stores the results via core.database.insert_data().

Requires OPENWEATHER_API_KEY to be set (see .env.example). Without a key,
fetch_rainfall_data() logs a clear error and returns 0 rather than crashing
the whole pipeline, so the rest of the system can still run.
"""

import json
import time
from datetime import datetime

import requests

from config import DISTRICTS_FILE, OPENWEATHER_API_KEY, OPENWEATHER_URL
from core.database import get_or_create_state, get_or_create_district, insert_data
from logger_config import get_logger

logger = get_logger(__name__)

REQUEST_TIMEOUT = 10        # seconds
THROTTLE_SECONDS = 1.0      # be polite to the free-tier rate limit


def load_districts():
    """Load the states/districts reference list from disk."""
    try:
        with open(DISTRICTS_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("states", [])
    except (OSError, json.JSONDecodeError) as exc:
        logger.exception("Could not load districts file '%s': %s", DISTRICTS_FILE, exc)
        return []


def _fetch_weather_for_point(lat: float, lon: float) -> dict:
    """Call OpenWeatherMap for one coordinate. Returns a dict with
    rainfall_mm, temperature_c, humidity_percent. Raises requests exceptions
    on network/HTTP failure."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(OPENWEATHER_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    rain = payload.get("rain", {})
    rainfall_mm = rain.get("1h", rain.get("3h", 0.0)) or 0.0

    main = payload.get("main", {})
    return {
        "rainfall_mm": round(float(rainfall_mm), 2),
        "temperature_c": round(float(main.get("temp", 0.0)), 2),
        "humidity_percent": round(float(main.get("humidity", 0.0)), 2),
    }


def fetch_rainfall_data() -> int:
    """Fetch current rainfall/weather data for every configured district
    and store it in the `rainfall_data` table.

    Returns the number of rows successfully inserted.
    """
    if not OPENWEATHER_API_KEY:
        logger.error(
            "OPENWEATHER_API_KEY is not set. Skipping fetch_rainfall_data(). "
            "Set it in your .env file to enable live rainfall collection."
        )
        return 0

    states = load_districts()
    if not states:
        logger.warning("No districts loaded; fetch_rainfall_data() has nothing to do.")
        return 0

    inserted = 0
    now = datetime.utcnow()

    for state_entry in states:
        state_name = state_entry["state"]
        try:
            state_id = get_or_create_state(state_name)
        except Exception as exc:
            logger.exception("Could not resolve state '%s': %s", state_name, exc)
            continue

        for district_entry in state_entry.get("districts", []):
            district_name = district_entry["district"]
            lat, lon = district_entry["lat"], district_entry["lon"]

            try:
                weather = _fetch_weather_for_point(lat, lon)
            except requests.exceptions.RequestException as exc:
                logger.error(
                    "Weather fetch failed for %s, %s: %s", district_name, state_name, exc
                )
                continue
            except (ValueError, KeyError) as exc:
                logger.error(
                    "Unexpected weather payload for %s, %s: %s", district_name, state_name, exc
                )
                continue

            try:
                district_id = get_or_create_district(state_id, district_name, lat, lon)
                row_id = insert_data(
                    "rainfall_data",
                    {
                        "district_id": district_id,
                        "rainfall_mm": weather["rainfall_mm"],
                        "temperature_c": weather["temperature_c"],
                        "humidity_percent": weather["humidity_percent"],
                        "latitude": lat,
                        "longitude": lon,
                        "recorded_at": now,
                    },
                )
                if row_id:
                    inserted += 1
                    logger.debug(
                        "Stored rainfall for %s, %s: %.1fmm",
                        district_name, state_name, weather["rainfall_mm"],
                    )
            except Exception as exc:
                logger.exception(
                    "Failed to store rainfall for %s, %s: %s", district_name, state_name, exc
                )

            time.sleep(THROTTLE_SECONDS)

    logger.info("fetch_rainfall_data(): inserted %d rainfall records.", inserted)
    return inserted
