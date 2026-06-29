"""
main.py

Entry point for the India Disaster Monitoring System.

Usage:
    python main.py --setup          # create database + tables only
    python main.py --run            # run one full monitoring cycle
    python main.py --report         # generate today's report only
    python main.py                  # same as --setup followed by --run

This module re-exports the core functions at the top level so they match
the names requested in the project spec:
    create_database, create_tables, fetch_rainfall_data, fetch_flood_data,
    fetch_earthquake_data, generate_alerts, insert_data
"""

import argparse
import sys

from core.database import create_database, create_tables, insert_data  # noqa: F401
from core.rainfall import fetch_rainfall_data
from core.flood import fetch_flood_data
from core.earthquake import fetch_earthquake_data
from core.cyclone import fetch_cyclone_data
from core.alerts import generate_alerts
from core.reports import generate_daily_report
from logger_config import get_logger

logger = get_logger(__name__)


def setup():
    """One-time (idempotent) database + schema setup."""
    logger.info("Setting up database and tables...")
    create_database()
    create_tables()
    logger.info("Setup complete.")


def run_monitoring_cycle():
    """Run a full end-to-end monitoring cycle:
    fetch rainfall -> fetch flood levels -> generate flood alerts ->
    fetch earthquakes -> fetch cyclone advisories -> generate daily report.
    """
    logger.info("===== Starting disaster monitoring cycle =====")

    try:
        rainfall_count = fetch_rainfall_data()
    except Exception:
        logger.exception("fetch_rainfall_data() crashed; continuing with other feeds.")
        rainfall_count = 0

    try:
        river_readings = fetch_flood_data()
    except Exception:
        logger.exception("fetch_flood_data() crashed; continuing with other feeds.")
        river_readings = []

    try:
        flood_alerts = generate_alerts(river_readings)
    except Exception:
        logger.exception("generate_alerts() crashed.")
        flood_alerts = []

    try:
        earthquake_count = fetch_earthquake_data()
    except Exception:
        logger.exception("fetch_earthquake_data() crashed.")
        earthquake_count = 0

    try:
        cyclone_count = fetch_cyclone_data()
    except Exception:
        logger.exception("fetch_cyclone_data() crashed.")
        cyclone_count = 0

    try:
        report = generate_daily_report()
    except Exception:
        logger.exception("generate_daily_report() crashed.")
        report = {}

    logger.info(
        "===== Cycle complete: rainfall=%d, flood_alerts=%d, earthquakes=%d, cyclones=%d =====",
        rainfall_count, len(flood_alerts), earthquake_count, cyclone_count,
    )
    return report


def main():
    parser = argparse.ArgumentParser(description="India Disaster Monitoring System")
    parser.add_argument("--setup", action="store_true", help="Create database and tables only")
    parser.add_argument("--run", action="store_true", help="Run one full monitoring cycle")
    parser.add_argument("--report", action="store_true", help="Generate today's report only")
    args = parser.parse_args()

    try:
        if args.setup and not args.run and not args.report:
            setup()
        elif args.run:
            run_monitoring_cycle()
        elif args.report:
            generate_daily_report()
        else:
            # Default: ensure schema exists, then run a full cycle.
            setup()
            run_monitoring_cycle()
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Exiting.")
        sys.exit(0)
    except Exception:
        logger.exception("Fatal error in main(). Exiting with status 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
