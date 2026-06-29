"""
core/alerts.py

Implements generate_alerts(): inspects the latest river water-level
readings and creates flood_alerts rows whenever a level crosses the
warning or danger threshold for its station.
"""

from core.database import insert_data
from logger_config import get_logger

logger = get_logger(__name__)


def _classify_severity(water_level: float, warning_level: float, danger_level: float):
    """Return (severity, message) for a reading, or (None, None) if the
    reading is below the warning level (no alert needed)."""
    if water_level >= danger_level + (danger_level - warning_level):
        return "Severe", (
            f"SEVERE FLOOD RISK: water level {water_level:.2f}m is well above the "
            f"danger level of {danger_level:.2f}m. Immediate evacuation precautions advised."
        )
    if water_level >= danger_level:
        return "Danger", (
            f"FLOOD ALERT: water level {water_level:.2f}m has crossed the danger "
            f"level of {danger_level:.2f}m."
        )
    if water_level >= warning_level:
        return "Warning", (
            f"Water level {water_level:.2f}m has crossed the warning level of "
            f"{warning_level:.2f}m. Monitor closely."
        )
    return None, None


def generate_alerts(river_readings: list) -> list:
    """Given the list of readings returned by fetch_flood_data(), create a
    flood_alerts row for every station at or above its warning level.

    Returns the list of alerts that were generated (as dicts), for use in
    the daily report / dashboard.
    """
    if not river_readings:
        logger.info("generate_alerts(): no river readings supplied, nothing to evaluate.")
        return []

    generated = []

    for reading in river_readings:
        severity, message = _classify_severity(
            reading["water_level"], reading["warning_level"], reading["danger_level"]
        )
        if severity is None:
            continue

        try:
            row_id = insert_data(
                "flood_alerts",
                {
                    "river_id": reading["river_id"],
                    "water_level": reading["water_level"],
                    "danger_level": reading["danger_level"],
                    "severity": severity,
                    "alert_message": message,
                },
            )
            if row_id:
                alert = {
                    "id": row_id,
                    "river": reading["river"],
                    "station": reading["station"],
                    "state": reading.get("state"),
                    "lat": reading.get("lat"),
                    "lon": reading.get("lon"),
                    "water_level": reading["water_level"],
                    "danger_level": reading["danger_level"],
                    "severity": severity,
                    "message": message,
                }
                generated.append(alert)

                log_fn = logger.warning if severity != "Severe" else logger.critical
                log_fn(
                    "[%s] %s at %s (%s): %s",
                    severity, reading["river"], reading["station"], reading.get("state"), message,
                )
        except Exception as exc:
            logger.exception(
                "Failed to record flood alert for %s at %s: %s",
                reading["river"], reading["station"], exc,
            )

    logger.info("generate_alerts(): %d flood alert(s) generated.", len(generated))
    return generated
