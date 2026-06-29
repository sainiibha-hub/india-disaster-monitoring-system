"""
core/flood.py

Fetches river water-level readings for the gauge stations defined in
config.RIVER_STATIONS and stores them in river_water_levels.

If config.FLOOD_API_URL is set, readings are pulled from that endpoint
(expected to return JSON shaped as {"river": ..., "station": ...,
"water_level": ...} per station, or a list thereof -- adapt
_fetch_from_api() to match whatever real feed you plug in, e.g. the
Central Water Commission's flood forecasting service).

If FLOOD_API_URL is NOT set, realistic readings are simulated around each
station's known normal level, with an occasional excursion above the
warning/danger level so the alerting pipeline has something to detect.
This keeps the whole system runnable end-to-end without external
credentials, while making the "plug in a real feed" path explicit.
"""

import random
from datetime import datetime

import requests

from config import FLOOD_API_URL, RIVER_STATIONS
from core.database import get_or_create_river, insert_data
from logger_config import get_logger

logger = get_logger(__name__)

REQUEST_TIMEOUT = 10


def _fetch_from_api(station: dict) -> float:
    """Fetch a single station's current water level from a real flood API.

    This is intentionally generic since CWC does not publish one fixed
    public schema -- adapt the params/parsing below to match the real feed
    you have access to.
    """
    params = {"river": station["river"], "station": station["station"]}
    response = requests.get(FLOOD_API_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    return float(payload["water_level"])


def _simulate_water_level(station: dict) -> float:
    """Generate a plausible water level reading for demo/testing purposes.

    Mostly fluctuates near the normal level; occasionally spikes towards or
    past the danger level to exercise the flood-alert pipeline.
    """
    normal = station["normal_level"]
    danger = station["danger_level"]
    spread = max(danger - normal, 0.5)

    if random.random() < 0.12:  # ~12% chance of a flood-risk excursion
        level = random.uniform(station["warning_level"], danger + spread * 0.3)
    else:
        level = normal + random.uniform(-spread * 0.15, spread * 0.25)

    return round(level, 2)


def fetch_flood_data() -> list:
    """Fetch/simulate water levels for every configured river station and
    store them in river_water_levels.

    Returns a list of dicts: [{"river_id", "river", "station", "water_level",
    "danger_level", "warning_level"}], used downstream by generate_alerts().
    """
    readings = []
    now = datetime.utcnow()
    use_real_api = bool(FLOOD_API_URL)

    for station in RIVER_STATIONS:
        try:
            if use_real_api:
                water_level = _fetch_from_api(station)
            else:
                water_level = _simulate_water_level(station)
        except requests.exceptions.RequestException as exc:
            logger.error(
                "Flood API fetch failed for %s at %s: %s. Falling back to simulation.",
                station["river"], station["station"], exc,
            )
            water_level = _simulate_water_level(station)
        except (ValueError, KeyError) as exc:
            logger.error(
                "Unexpected flood API payload for %s at %s: %s",
                station["river"], station["station"], exc,
            )
            continue

        try:
            river_id = get_or_create_river(station)
            insert_data(
                "river_water_levels",
                {
                    "river_id": river_id,
                    "water_level": water_level,
                    "recorded_at": now,
                },
            )
            readings.append({
                "river_id": river_id,
                "river": station["river"],
                "station": station["station"],
                "state": station["state"],
                "lat": station["lat"],
                "lon": station["lon"],
                "water_level": water_level,
                "warning_level": station["warning_level"],
                "danger_level": station["danger_level"],
            })
            logger.debug(
                "%s at %s: water level %.2fm (danger %.2fm)",
                station["river"], station["station"], water_level, station["danger_level"],
            )
        except Exception as exc:
            logger.exception(
                "Failed to store water level for %s at %s: %s",
                station["river"], station["station"], exc,
            )

    logger.info("fetch_flood_data(): collected %d river readings.", len(readings))
    return readings
