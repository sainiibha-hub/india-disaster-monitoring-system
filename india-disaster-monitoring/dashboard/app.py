"""
dashboard/app.py

Flask dashboard for the India Disaster Monitoring System.

Routes:
    GET /                       -> renders the dashboard page
    GET /api/summary            -> today's headline numbers
    GET /api/rainfall/latest    -> latest rainfall reading per district (for map + table)
    GET /api/rainfall/trend     -> daily avg rainfall, last 30 days (for chart)
    GET /api/rainfall/top-states-> states with highest rainfall today
    GET /api/floods             -> recent flood alerts with station coordinates
    GET /api/earthquakes        -> recent earthquakes (M >= 5.0, last 30 days)
    GET /api/cyclones           -> recent cyclone advisories

Run with:  python dashboard/app.py
Then open: http://localhost:5000
"""

import os
import sys

# Allow running this file directly (python dashboard/app.py) by ensuring the
# project root is on sys.path so `import config` / `core....` resolve.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, render_template

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from core.database import fetch_all
from logger_config import get_logger

logger = get_logger(__name__)

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/summary")
def api_summary():
    try:
        rainfall = fetch_all(
            "SELECT COUNT(*) AS cnt, AVG(rainfall_mm) AS avg_mm "
            "FROM rainfall_data WHERE DATE(recorded_at) = CURDATE()"
        )
        floods = fetch_all(
            "SELECT COUNT(*) AS cnt FROM flood_alerts WHERE DATE(created_at) = CURDATE()"
        )
        quakes = fetch_all(
            "SELECT COUNT(*) AS cnt FROM earthquakes "
            "WHERE event_time >= NOW() - INTERVAL 30 DAY"
        )
        cyclones = fetch_all(
            "SELECT COUNT(*) AS cnt FROM cyclone_alerts "
            "WHERE DATE(issued_at) = CURDATE()"
        )
        return jsonify({
            "rainfall_records_today": (rainfall[0]["cnt"] if rainfall else 0) or 0,
            "avg_rainfall_today_mm": round(float((rainfall[0]["avg_mm"] if rainfall else 0) or 0), 2),
            "flood_alerts_today": (floods[0]["cnt"] if floods else 0) or 0,
            "earthquakes_last_30_days": (quakes[0]["cnt"] if quakes else 0) or 0,
            "cyclone_advisories_today": (cyclones[0]["cnt"] if cyclones else 0) or 0,
        })
    except Exception as exc:
        logger.exception("api_summary failed: %s", exc)
        return jsonify({"error": "Failed to load summary"}), 500


@app.route("/api/rainfall/latest")
def api_rainfall_latest():
    """Most recent rainfall reading for every district -- used for map
    markers and the data table."""
    try:
        rows = fetch_all(
            """
            SELECT d.district_name, s.state_name, r.rainfall_mm,
                   r.temperature_c, r.humidity_percent,
                   r.latitude, r.longitude, r.recorded_at
            FROM rainfall_data r
            JOIN districts d ON r.district_id = d.district_id
            JOIN states s ON d.state_id = s.state_id
            WHERE r.id IN (
                SELECT MAX(id) FROM rainfall_data GROUP BY district_id
            )
            ORDER BY r.rainfall_mm DESC
            """
        )
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_rainfall_latest failed: %s", exc)
        return jsonify({"error": "Failed to load rainfall data"}), 500


@app.route("/api/rainfall/trend")
def api_rainfall_trend():
    """Average rainfall per day for the last 30 days, for the trend chart."""
    try:
        rows = fetch_all(
            """
            SELECT DATE(recorded_at) AS day, ROUND(AVG(rainfall_mm), 2) AS avg_mm,
                   ROUND(MAX(rainfall_mm), 2) AS max_mm
            FROM rainfall_data
            WHERE recorded_at >= NOW() - INTERVAL 30 DAY
            GROUP BY DATE(recorded_at)
            ORDER BY day ASC
            """
        )
        for r in rows:
            r["day"] = r["day"].isoformat()
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_rainfall_trend failed: %s", exc)
        return jsonify({"error": "Failed to load rainfall trend"}), 500


@app.route("/api/rainfall/top-states")
def api_top_states():
    try:
        rows = fetch_all(
            """
            SELECT s.state_name, ROUND(AVG(r.rainfall_mm), 2) AS avg_mm,
                   ROUND(MAX(r.rainfall_mm), 2) AS max_mm
            FROM rainfall_data r
            JOIN districts d ON r.district_id = d.district_id
            JOIN states s ON d.state_id = s.state_id
            WHERE DATE(r.recorded_at) = CURDATE()
            GROUP BY s.state_name
            ORDER BY avg_mm DESC
            LIMIT 10
            """
        )
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_top_states failed: %s", exc)
        return jsonify({"error": "Failed to load top states"}), 500


@app.route("/api/floods")
def api_floods():
    try:
        rows = fetch_all(
            """
            SELECT f.id, f.water_level, f.danger_level, f.severity, f.alert_message,
                   f.created_at, r.river_name, r.station_name, r.state_name,
                   r.latitude, r.longitude
            FROM flood_alerts f
            JOIN rivers r ON f.river_id = r.river_id
            ORDER BY f.created_at DESC
            LIMIT 50
            """
        )
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_floods failed: %s", exc)
        return jsonify({"error": "Failed to load flood alerts"}), 500


@app.route("/api/earthquakes")
def api_earthquakes():
    try:
        rows = fetch_all(
            """
            SELECT id, place, magnitude, depth_km, latitude, longitude, event_time
            FROM earthquakes
            WHERE event_time >= NOW() - INTERVAL 30 DAY
            ORDER BY event_time DESC
            LIMIT 100
            """
        )
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_earthquakes failed: %s", exc)
        return jsonify({"error": "Failed to load earthquakes"}), 500


@app.route("/api/cyclones")
def api_cyclones():
    try:
        rows = fetch_all(
            """
            SELECT id, cyclone_name, basin, latitude, longitude, wind_speed_kmph,
                   pressure_hpa, category, alert_level, advisory, issued_at
            FROM cyclone_alerts
            ORDER BY issued_at DESC
            LIMIT 20
            """
        )
        return jsonify(rows)
    except Exception as exc:
        logger.exception("api_cyclones failed: %s", exc)
        return jsonify({"error": "Failed to load cyclone advisories"}), 500


if __name__ == "__main__":
    logger.info("Starting Flask dashboard on %s:%d", FLASK_HOST, FLASK_PORT)
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
