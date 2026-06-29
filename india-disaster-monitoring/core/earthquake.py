"""
core/earthquake.py

Fetches earthquakes of magnitude >= EARTHQUAKE_MIN_MAGNITUDE from the last
EARTHQUAKE_LOOKBACK_DAYS days, in/around India, from the public USGS
earthquake catalog (no API key required):
https://earthquake.usgs.gov/fdsnws/event/1/query
"""

from datetime import datetime, timedelta

import requests

from config import (
    USGS_EARTHQUAKE_URL,
    INDIA_BOUNDING_BOX,
    EARTHQUAKE_MIN_MAGNITUDE,
    EARTHQUAKE_LOOKBACK_DAYS,
)
from core.database import insert_data
from logger_config import get_logger

logger = get_logger(__name__)

REQUEST_TIMEOUT = 15


def fetch_earthquake_data() -> int:
    """Fetch recent significant earthquakes near India from USGS and store
    them in the `earthquakes` table.

    Returns the number of new rows inserted (duplicates, identified by the
    USGS event id, are skipped via INSERT IGNORE).
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=EARTHQUAKE_LOOKBACK_DAYS)

    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%d"),
        "endtime": end_time.strftime("%Y-%m-%d"),
        "minmagnitude": EARTHQUAKE_MIN_MAGNITUDE,
        **INDIA_BOUNDING_BOX,
        "orderby": "time",
    }

    try:
        response = requests.get(USGS_EARTHQUAKE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException as exc:
        logger.error("USGS earthquake fetch failed: %s", exc)
        return 0
    except ValueError as exc:
        logger.error("USGS earthquake response was not valid JSON: %s", exc)
        return 0

    features = payload.get("features", [])
    inserted = 0

    for feature in features:
        try:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]  # [lon, lat, depth_km]
            usgs_id = feature["id"]
            magnitude = props.get("mag")
            place = props.get("place", "Unknown location")
            event_time_ms = props.get("time")

            if magnitude is None or event_time_ms is None:
                continue

            event_time = datetime.utcfromtimestamp(event_time_ms / 1000.0)
            longitude, latitude = coords[0], coords[1]
            depth_km = coords[2] if len(coords) > 2 else None

            row_id = insert_data(
                "earthquakes",
                {
                    "usgs_id": usgs_id,
                    "place": place,
                    "magnitude": round(float(magnitude), 2),
                    "depth_km": round(float(depth_km), 2) if depth_km is not None else None,
                    "latitude": latitude,
                    "longitude": longitude,
                    "event_time": event_time,
                    "source": "USGS",
                },
                ignore_duplicates=True,
            )
            if row_id:
                inserted += 1
                logger.debug("New earthquake M%.1f near %s", magnitude, place)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.warning("Skipping malformed earthquake feature: %s", exc)
            continue

    logger.info(
        "fetch_earthquake_data(): %d new earthquakes (>= M%.1f) inserted, %d total fetched.",
        inserted, EARTHQUAKE_MIN_MAGNITUDE, len(features),
    )
    return inserted
