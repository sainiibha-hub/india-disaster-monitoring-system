"""
core/cyclone.py

Fetches cyclone advisories for the North Indian Ocean basin and stores them
in cyclone_alerts.

IMD / RSMC New Delhi (the official source for Indian Ocean cyclone
advisories) does not publish a simple public REST API. If you have access
to a real feed (e.g. an institutional CAP/XML advisory feed, or a
third-party aggregator), set CYCLONE_API_URL in your .env and adapt
_fetch_from_api() below to its schema.

Without that, fetch_cyclone_data() simulates a small number of plausible
advisories so the storage, alerting and dashboard layers are fully
exercised end-to-end. During months with no active system it is normal
and expected for this to return 0.
"""

import random
from datetime import datetime

import requests

from config import CYCLONE_API_URL
from core.database import insert_data
from logger_config import get_logger

logger = get_logger(__name__)

REQUEST_TIMEOUT = 10

# Active-cyclone simulation is seasonal: the North Indian Ocean cyclone
# season runs roughly April-June and October-December.
CYCLONE_SEASON_MONTHS = {4, 5, 6, 10, 11, 12}

_SAMPLE_NAMES = ["Mocha", "Biparjoy", "Remal", "Dana", "Fengal", "Asna"]
_BASIN_REGIONS = [
    {"name": "Bay of Bengal", "lat_range": (10, 20), "lon_range": (82, 92)},
    {"name": "Arabian Sea", "lat_range": (10, 22), "lon_range": (62, 72)},
]


def _fetch_from_api() -> list:
    response = requests.get(CYCLONE_API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    # Expecting a list of advisory dicts; adapt to the real feed's schema.
    return payload if isinstance(payload, list) else payload.get("advisories", [])


def _simulate_advisories() -> list:
    """Return zero or more simulated cyclone advisories, more likely during
    the historical North Indian Ocean cyclone season."""
    now = datetime.utcnow()
    in_season = now.month in CYCLONE_SEASON_MONTHS
    chance_of_active_system = 0.35 if in_season else 0.05

    if random.random() > chance_of_active_system:
        return []

    basin = random.choice(_BASIN_REGIONS)
    wind_speed = random.uniform(65, 180)

    if wind_speed >= 165:
        category, alert_level = "Super Cyclonic Storm", "Severe"
    elif wind_speed >= 120:
        category, alert_level = "Very Severe Cyclonic Storm", "Severe"
    elif wind_speed >= 90:
        category, alert_level = "Severe Cyclonic Storm", "Warning"
    else:
        category, alert_level = "Cyclonic Storm", "Watch"

    return [{
        "cyclone_name": random.choice(_SAMPLE_NAMES),
        "basin": basin["name"],
        "latitude": round(random.uniform(*basin["lat_range"]), 2),
        "longitude": round(random.uniform(*basin["lon_range"]), 2),
        "wind_speed_kmph": round(wind_speed, 1),
        "pressure_hpa": round(1010 - wind_speed * 1.4, 1),
        "category": category,
        "alert_level": alert_level,
        "advisory": f"{category} expected to intensify; coastal districts advised caution.",
        "issued_at": now,
    }]


def fetch_cyclone_data() -> int:
    """Fetch (or simulate) current cyclone advisories and store them in
    cyclone_alerts. Returns the number of advisories inserted."""
    use_real_api = bool(CYCLONE_API_URL)

    try:
        advisories = _fetch_from_api() if use_real_api else _simulate_advisories()
    except requests.exceptions.RequestException as exc:
        logger.error("Cyclone API fetch failed: %s. Falling back to simulation.", exc)
        advisories = _simulate_advisories()
    except (ValueError, KeyError) as exc:
        logger.error("Unexpected cyclone API payload: %s", exc)
        advisories = []

    inserted = 0
    for advisory in advisories:
        try:
            row_id = insert_data("cyclone_alerts", advisory)
            if row_id:
                inserted += 1
                logger.info(
                    "Cyclone advisory stored: %s (%s) - %s",
                    advisory.get("cyclone_name"), advisory.get("category"),
                    advisory.get("alert_level"),
                )
        except Exception as exc:
            logger.exception("Failed to store cyclone advisory: %s", exc)

    if not advisories:
        logger.info("fetch_cyclone_data(): no active cyclone systems detected.")
    return inserted
