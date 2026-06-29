"""
scheduler.py

Runs the disaster monitoring cycle automatically, every day, at the time
configured by DAILY_RUN_TIME in config.py / .env (default 06:00 local time).

This keeps a long-running process alive with a simple in-process scheduler
(the `schedule` library), which is the most portable option across
Windows/Linux/macOS. For production deployments you may prefer to invoke
`python main.py --run` directly from:
    - cron (Linux/macOS), e.g.:
        0 6 * * * /usr/bin/python3 /path/to/main.py --run >> /path/to/logs/cron.log 2>&1
    - systemd timers (Linux)
    - Windows Task Scheduler

Run with:  python scheduler.py
Stop with: Ctrl+C
"""

import time

import schedule

from config import DAILY_RUN_TIME
from main import setup, run_monitoring_cycle
from logger_config import get_logger

logger = get_logger(__name__)


def scheduled_job():
    logger.info("Scheduled trigger fired -- running monitoring cycle.")
    try:
        run_monitoring_cycle()
    except Exception:
        logger.exception("Scheduled monitoring cycle failed.")


def main():
    setup()  # make sure DB/tables exist before the first run

    schedule.every().day.at(DAILY_RUN_TIME).do(scheduled_job)
    logger.info(
        "Scheduler started. The monitoring cycle will run every day at %s. "
        "Press Ctrl+C to stop.", DAILY_RUN_TIME,
    )

    # Run once immediately on startup so you don't have to wait until the
    # next scheduled time to see data flow in. Comment this out if you only
    # want the daily scheduled run.
    scheduled_job()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
