# India Disaster Monitoring System

A Python + MySQL + Flask system that monitors four hazard types across
India: rainfall, river floods, earthquakes, and tropical cyclones. It
collects data on a schedule, stores it in MySQL, raises flood alerts
automatically, generates a daily summary report, and serves a live
dashboard with an interactive map.

## What's real vs. simulated (read this first)

This system is built to be honest about data sources:

| Hazard      | Source                                   | Status |
|-------------|-------------------------------------------|--------|
| Rainfall, temperature, humidity | [OpenWeatherMap](https://openweathermap.org/api) current-weather API | **Real**, needs a free API key |
| Earthquakes | [USGS Earthquake Catalog](https://earthquake.usgs.gov/fdsnws/event/1/query) | **Real**, public, no key needed |
| River flood levels | Central Water Commission (CWC) gauge data | **Simulated** -- CWC does not publish a simple public REST API. The simulator generates realistic readings around each station's real normal/warning/danger thresholds, including occasional flood-risk excursions, so the full alerting pipeline is testable end-to-end. |
| Cyclone advisories | India Meteorological Department (IMD) / RSMC New Delhi | **Simulated** -- IMD does not publish a public REST API either. The simulator produces occasional plausible advisories, weighted toward the real April-June and October-December cyclone seasons. |

Both simulated feeds are built so a **real feed can be plugged in with zero
changes anywhere else in the system**: set `FLOOD_API_URL` / `CYCLONE_API_URL`
in `.env` and adjust the small `_fetch_from_api()` function in
`core/flood.py` / `core/cyclone.py` to match that feed's response shape.

The rainfall district list (`data/india_states_districts.json`) covers all
36 states/UTs with a representative set of ~90 major districts/cities
rather than the full 700+ district list, to keep the demo's API usage and
runtime sane. Add more entries in the same shape to extend it -- no code
changes required.

## Architecture

```
                     ┌─────────────────┐
                     │   scheduler.py   │  (runs daily, or use cron/Task Scheduler)
                     └────────┬─────────┘
                              │ calls
                     ┌────────▼─────────┐
                     │     main.py      │  orchestrator
                     └────────┬─────────┘
        ┌──────────┬──────────┼───────────┬─────────────┐
        ▼          ▼          ▼           ▼             ▼
   rainfall.py  flood.py  earthquake.py cyclone.py   alerts.py / reports.py
        │          │          │           │             │
        └──────────┴──────────┴───────────┴─────────────┘
                              │
                     ┌────────▼─────────┐
                     │   MySQL database  │
                     └────────┬─────────┘
                              │ reads
                     ┌────────▼─────────┐
                     │  dashboard/app.py │  Flask + REST API
                     └────────┬─────────┘
                              │ serves
                     ┌────────▼─────────┐
                     │  dashboard.html   │  Leaflet map + Chart.js
                     └───────────────────┘
```

## Project structure

```
india-disaster-monitoring/
├── main.py                    # Orchestrator: --setup / --run / --report
├── scheduler.py                # Runs main.py's cycle automatically every day
├── config.py                   # All settings (DB, API keys, thresholds)
├── logger_config.py             # Centralized logging (console + rotating file)
├── requirements.txt
├── .env.example                 # Copy to .env and fill in your values
├── README.md
│
├── core/
│   ├── database.py             # create_database(), create_tables(), insert_data(), fetch_all()
│   ├── rainfall.py             # fetch_rainfall_data()
│   ├── flood.py                # fetch_flood_data()
│   ├── earthquake.py           # fetch_earthquake_data()
│   ├── cyclone.py              # fetch_cyclone_data()
│   ├── alerts.py                # generate_alerts()
│   └── reports.py               # generate_daily_report()
│
├── data/
│   └── india_states_districts.json   # State -> district -> lat/lon reference data
│
├── db/
│   ├── schema.sql               # Full DDL (mirrors core/database.py)
│   └── analysis_queries.sql     # The 4 requested analysis queries + a summary query
│
├── dashboard/
│   ├── app.py                   # Flask app + REST API
│   ├── templates/
│   │   └── dashboard.html
│   └── static/
│       ├── css/style.css
│       └── js/dashboard.js
│
├── logs/                        # disaster_monitoring.log (rotating)
└── reports/                     # report_YYYY-MM-DD.txt (one per day)
```

## Setup

### 1. Prerequisites

- Python 3.9+
- A running MySQL server (8.0+ recommended) you can connect to
- A free [OpenWeatherMap API key](https://openweathermap.org/api) (for rainfall data)

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# edit .env: set DB_PASSWORD, OPENWEATHER_API_KEY, etc.
```

### 4. Create the database and tables

```bash
python main.py --setup
```

This calls `create_database()` then `create_tables()`. Safe to re-run any
time -- everything uses `CREATE ... IF NOT EXISTS`.

### 5. Run one monitoring cycle manually

```bash
python main.py --run
```

This calls, in order: `fetch_rainfall_data()` → `fetch_flood_data()` →
`generate_alerts()` → `fetch_earthquake_data()` → `fetch_cyclone_data()` →
`generate_daily_report()`. Watch `logs/disaster_monitoring.log` (or the
console) for progress and any warnings/errors -- each feed is wrapped in
its own try/except so one feed failing (e.g. no internet, bad API key)
doesn't stop the others from running.

### 6. Launch the dashboard

```bash
python dashboard/app.py
```

Open **http://localhost:5000** in your browser. The map and panels
auto-refresh every 60 seconds.

## Automatic daily scheduling

**Option A -- built-in scheduler (simplest, cross-platform):**

```bash
python scheduler.py
```

Runs once immediately, then every day at the time set by `DAILY_RUN_TIME`
in `.env` (default `06:00`). Keep this process running (e.g. in `screen`,
`tmux`, a Docker container, or as a service).

**Option B -- cron (Linux/macOS):**

```bash
crontab -e
# add:
0 6 * * * cd /path/to/india-disaster-monitoring && /path/to/venv/bin/python main.py --run >> logs/cron.log 2>&1
```

**Option C -- systemd timer (Linux):** create a `.service` that runs
`python main.py --run` and a matching `.timer` with `OnCalendar=06:00`.

**Option D -- Windows Task Scheduler:** create a daily trigger that runs
`python.exe main.py --run` with "Start in" set to the project folder.

## Generating a report on demand

```bash
python main.py --report
```

Writes `reports/report_YYYY-MM-DD.txt` and upserts a row in `daily_reports`.

## SQL analysis queries

See `db/analysis_queries.sql` for ready-to-run queries covering:

1. States with the highest rainfall
2. Districts/stations currently under flood alert
3. Recent earthquakes (last 30 days, M ≥ 5.0)
4. Rainfall trends over the last 30 days

These same queries (or close variants) back the dashboard's `/api/*`
endpoints in `dashboard/app.py`.

## Function reference (as required by the spec)

All located under `core/`, re-exported at the top of `main.py`:

| Function | File | Purpose |
|---|---|---|
| `create_database()` | `core/database.py` | Creates the MySQL database if missing |
| `create_tables()` | `core/database.py` | Creates all 9 tables if missing |
| `fetch_rainfall_data()` | `core/rainfall.py` | Pulls rainfall/temp/humidity per district from OpenWeatherMap |
| `fetch_flood_data()` | `core/flood.py` | Pulls/simulates river water levels |
| `fetch_earthquake_data()` | `core/earthquake.py` | Pulls M≥5.0 earthquakes from USGS (last 30 days) |
| `fetch_cyclone_data()` | `core/cyclone.py` | Pulls/simulates cyclone advisories |
| `generate_alerts()` | `core/alerts.py` | Compares water levels to danger thresholds, writes `flood_alerts` |
| `insert_data()` | `core/database.py` | Generic parameterised INSERT used by every fetch function |
| `generate_daily_report()` | `core/reports.py` | Aggregates the day's activity into `daily_reports` + a text file |

## Logging & error handling

- Every module logs to both the console and `logs/disaster_monitoring.log`
  (rotating, 5MB × 5 backups) via `logger_config.get_logger(__name__)`.
- Every network call and database operation is wrapped in `try/except` with
  specific exception types caught where possible (`requests.RequestException`,
  `mysql.connector.Error`, `KeyError`/`ValueError` for malformed payloads).
- `main.py`'s `run_monitoring_cycle()` wraps each of the five pipeline steps
  in its own try/except so a single feed failing never stops the others.

## Extending this system

- **Full district coverage:** add entries to `data/india_states_districts.json`.
- **Real flood data:** set `FLOOD_API_URL` and adapt `core/flood.py::_fetch_from_api()`.
- **Real cyclone data:** set `CYCLONE_API_URL` and adapt `core/cyclone.py::_fetch_from_api()`.
- **Notifications:** `generate_alerts()` is the natural place to add SMS/email/push
  notifications -- it already knows the severity and message for every alert raised.
- **Rainfall heatmap:** the dashboard currently uses sized circle markers; swap in
  the `leaflet.heat` plugin against the same `/api/rainfall/latest` data if you want
  a smoothed heatmap instead.
