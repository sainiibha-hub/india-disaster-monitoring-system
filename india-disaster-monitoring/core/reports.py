"""
core/reports.py

Generates a daily summary report combining rainfall, flood, earthquake and
cyclone activity for the current date, stores it in daily_reports, and
writes a human-readable .txt copy to the reports/ directory.
"""

import os
from datetime import date, datetime

from config import REPORTS_DIR
from core.database import get_connection, insert_data
from logger_config import get_logger

logger = get_logger(__name__)


def _query_one(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchone()


def generate_daily_report(report_date: date = None) -> dict:
    """Aggregate today's (or the given date's) activity across all four
    hazard types, store it in daily_reports, and write a text file copy to
    REPORTS_DIR. Returns the report as a dict."""
    report_date = report_date or date.today()

    conn = None
    cursor = None
    summary = {
        "report_date": report_date,
        "total_rainfall_records": 0,
        "avg_rainfall_mm": 0.0,
        "highest_rainfall_state": None,
        "highest_rainfall_mm": 0.0,
        "flood_alerts_count": 0,
        "earthquake_count": 0,
        "cyclone_alerts_count": 0,
    }

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        row = _query_one(
            cursor,
            """
            SELECT COUNT(*) AS cnt, AVG(rainfall_mm) AS avg_mm
            FROM rainfall_data
            WHERE DATE(recorded_at) = %s
            """,
            (report_date,),
        )
        if row:
            summary["total_rainfall_records"] = row["cnt"] or 0
            summary["avg_rainfall_mm"] = round(float(row["avg_mm"] or 0), 2)

        row = _query_one(
            cursor,
            """
            SELECT s.state_name AS state_name, MAX(r.rainfall_mm) AS max_mm
            FROM rainfall_data r
            JOIN districts d ON r.district_id = d.district_id
            JOIN states s ON d.state_id = s.state_id
            WHERE DATE(r.recorded_at) = %s
            GROUP BY s.state_name
            ORDER BY max_mm DESC
            LIMIT 1
            """,
            (report_date,),
        )
        if row:
            summary["highest_rainfall_state"] = row["state_name"]
            summary["highest_rainfall_mm"] = round(float(row["max_mm"] or 0), 2)

        row = _query_one(
            cursor,
            "SELECT COUNT(*) AS cnt FROM flood_alerts WHERE DATE(created_at) = %s",
            (report_date,),
        )
        summary["flood_alerts_count"] = row["cnt"] if row else 0

        row = _query_one(
            cursor,
            "SELECT COUNT(*) AS cnt FROM earthquakes WHERE DATE(event_time) = %s",
            (report_date,),
        )
        summary["earthquake_count"] = row["cnt"] if row else 0

        row = _query_one(
            cursor,
            "SELECT COUNT(*) AS cnt FROM cyclone_alerts WHERE DATE(issued_at) = %s",
            (report_date,),
        )
        summary["cyclone_alerts_count"] = row["cnt"] if row else 0

    except Exception as exc:
        logger.exception("Failed to aggregate daily report data: %s", exc)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    report_text = (
        f"India Disaster Monitoring -- Daily Report for {report_date.isoformat()}\n"
        f"{'=' * 60}\n"
        f"Rainfall records collected : {summary['total_rainfall_records']}\n"
        f"Average rainfall (mm)      : {summary['avg_rainfall_mm']}\n"
        f"Highest rainfall state     : {summary['highest_rainfall_state']} "
        f"({summary['highest_rainfall_mm']} mm)\n"
        f"Flood alerts issued        : {summary['flood_alerts_count']}\n"
        f"Earthquakes (M>=5.0)       : {summary['earthquake_count']}\n"
        f"Cyclone advisories         : {summary['cyclone_alerts_count']}\n"
        f"Generated at               : {datetime.now().isoformat(timespec='seconds')}\n"
    )
    summary["report_text"] = report_text

    # Persist to DB (one row per date -- re-running the same day overwrites it)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO daily_reports
                (report_date, total_rainfall_records, avg_rainfall_mm,
                 highest_rainfall_state, highest_rainfall_mm,
                 flood_alerts_count, earthquake_count, cyclone_alerts_count, report_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_rainfall_records = VALUES(total_rainfall_records),
                avg_rainfall_mm = VALUES(avg_rainfall_mm),
                highest_rainfall_state = VALUES(highest_rainfall_state),
                highest_rainfall_mm = VALUES(highest_rainfall_mm),
                flood_alerts_count = VALUES(flood_alerts_count),
                earthquake_count = VALUES(earthquake_count),
                cyclone_alerts_count = VALUES(cyclone_alerts_count),
                report_text = VALUES(report_text)
            """,
            (
                summary["report_date"], summary["total_rainfall_records"],
                summary["avg_rainfall_mm"], summary["highest_rainfall_state"],
                summary["highest_rainfall_mm"], summary["flood_alerts_count"],
                summary["earthquake_count"], summary["cyclone_alerts_count"],
                report_text,
            ),
        )
        conn.commit()
    except Exception as exc:
        logger.exception("Failed to store daily report in DB: %s", exc)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Also write a plain-text copy to disk
    try:
        file_path = os.path.join(REPORTS_DIR, f"report_{report_date.isoformat()}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        logger.info("Daily report written to %s", file_path)
    except OSError as exc:
        logger.exception("Failed to write daily report file: %s", exc)

    logger.info("generate_daily_report(): %s", summary)
    return summary
