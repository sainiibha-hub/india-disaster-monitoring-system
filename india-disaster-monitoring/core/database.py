"""
core/database.py

Database layer for the India Disaster Monitoring System.

Implements the required:
    - create_database()
    - create_tables()
    - insert_data()
plus a connection helper used by every other module.
"""

from typing import Optional

import mysql.connector
from mysql.connector import Error as MySQLError

from config import DB_CONFIG, DB_NAME
from logger_config import get_logger

logger = get_logger(__name__)


# --------------------------------------------------------------------------
# Connections
# --------------------------------------------------------------------------
def get_connection(use_database: bool = True):
    """Open and return a new MySQL connection.

    Raises mysql.connector.Error on failure (caller decides how to handle).
    """
    cfg = dict(DB_CONFIG)
    if use_database:
        cfg["database"] = DB_NAME
    return mysql.connector.connect(**cfg)


# --------------------------------------------------------------------------
# Schema setup
# --------------------------------------------------------------------------
def create_database():
    """Create the MySQL database if it does not already exist."""
    try:
        conn = get_connection(use_database=False)
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        logger.info("Database '%s' is ready.", DB_NAME)
    except MySQLError as exc:
        logger.exception("Failed to create database '%s': %s", DB_NAME, exc)
        raise
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def create_tables():
    """Create all tables required by the system, if they do not exist."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS states (
            state_id INT AUTO_INCREMENT PRIMARY KEY,
            state_name VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS districts (
            district_id INT AUTO_INCREMENT PRIMARY KEY,
            state_id INT NOT NULL,
            district_name VARCHAR(120) NOT NULL,
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            UNIQUE KEY uq_state_district (state_id, district_name),
            CONSTRAINT fk_district_state FOREIGN KEY (state_id)
                REFERENCES states(state_id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS rainfall_data (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            district_id INT NOT NULL,
            rainfall_mm DECIMAL(6,2) NOT NULL DEFAULT 0,
            temperature_c DECIMAL(5,2),
            humidity_percent DECIMAL(5,2),
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            recorded_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_rainfall_district FOREIGN KEY (district_id)
                REFERENCES districts(district_id) ON DELETE CASCADE,
            INDEX idx_rainfall_recorded_at (recorded_at),
            INDEX idx_rainfall_district (district_id)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS rivers (
            river_id INT AUTO_INCREMENT PRIMARY KEY,
            river_name VARCHAR(100) NOT NULL,
            station_name VARCHAR(120) NOT NULL,
            state_name VARCHAR(100) NOT NULL,
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            normal_level DECIMAL(6,2) NOT NULL,
            warning_level DECIMAL(6,2) NOT NULL,
            danger_level DECIMAL(6,2) NOT NULL,
            UNIQUE KEY uq_river_station (river_name, station_name)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS river_water_levels (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            river_id INT NOT NULL,
            water_level DECIMAL(6,2) NOT NULL,
            recorded_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_level_river FOREIGN KEY (river_id)
                REFERENCES rivers(river_id) ON DELETE CASCADE,
            INDEX idx_level_recorded_at (recorded_at)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS flood_alerts (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            river_id INT NOT NULL,
            water_level DECIMAL(6,2) NOT NULL,
            danger_level DECIMAL(6,2) NOT NULL,
            severity ENUM('Warning', 'Danger', 'Severe') NOT NULL,
            alert_message VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_alert_river FOREIGN KEY (river_id)
                REFERENCES rivers(river_id) ON DELETE CASCADE,
            INDEX idx_flood_alert_created (created_at)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS earthquakes (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            usgs_id VARCHAR(64) NOT NULL UNIQUE,
            place VARCHAR(255),
            magnitude DECIMAL(4,2) NOT NULL,
            depth_km DECIMAL(7,2),
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            event_time DATETIME NOT NULL,
            source VARCHAR(50) DEFAULT 'USGS',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_eq_event_time (event_time),
            INDEX idx_eq_magnitude (magnitude)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS cyclone_alerts (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            cyclone_name VARCHAR(100) NOT NULL,
            basin VARCHAR(50),
            latitude DECIMAL(9,6),
            longitude DECIMAL(9,6),
            wind_speed_kmph DECIMAL(6,2),
            pressure_hpa DECIMAL(6,2),
            category VARCHAR(50),
            alert_level ENUM('Watch', 'Warning', 'Severe') NOT NULL DEFAULT 'Watch',
            advisory VARCHAR(255),
            issued_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_cyclone_issued_at (issued_at)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_date DATE NOT NULL UNIQUE,
            total_rainfall_records INT DEFAULT 0,
            avg_rainfall_mm DECIMAL(6,2) DEFAULT 0,
            highest_rainfall_state VARCHAR(100),
            highest_rainfall_mm DECIMAL(6,2),
            flood_alerts_count INT DEFAULT 0,
            earthquake_count INT DEFAULT 0,
            cyclone_alerts_count INT DEFAULT 0,
            report_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """,
    ]

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
        logger.info("All tables created/verified successfully.")
    except MySQLError as exc:
        logger.exception("Failed to create tables: %s", exc)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --------------------------------------------------------------------------
# Generic insert helper
# --------------------------------------------------------------------------
def insert_data(table: str, data: dict, ignore_duplicates: bool = False) -> Optional[int]:
    """Generic parameterised INSERT.

    Args:
        table: target table name (must be one defined in create_tables()).
        data: column -> value mapping for the row to insert.
        ignore_duplicates: if True, uses INSERT IGNORE so duplicate unique
            keys (e.g. the same USGS earthquake id) are silently skipped
            instead of raising an error.

    Returns:
        The inserted row's auto-increment id, or None if the insert was
        ignored (duplicate) or failed.
    """
    if not data:
        logger.warning("insert_data() called with empty data for table '%s'", table)
        return None

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    verb = "INSERT IGNORE" if ignore_duplicates else "INSERT"
    sql = f"{verb} INTO {table} ({columns}) VALUES ({placeholders})"

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, list(data.values()))
        conn.commit()
        if cursor.rowcount == 0:
            logger.debug("insert_data: row skipped (duplicate) for table '%s'", table)
            return None
        return cursor.lastrowid
    except MySQLError as exc:
        logger.error("insert_data failed for table '%s': %s | data=%s", table, exc, data)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_all(query: str, params: tuple = ()):
    """Run a SELECT query and return list of dict rows."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchall()
    except MySQLError as exc:
        logger.error("fetch_all failed: %s | query=%s", exc, query)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --------------------------------------------------------------------------
# Reference data seeding (states / districts / rivers)
# --------------------------------------------------------------------------
def get_or_create_state(state_name: str) -> int:
    """Return state_id for state_name, creating the row if needed."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state_id FROM states WHERE state_name = %s", (state_name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO states (state_name) VALUES (%s)", (state_name,))
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_or_create_district(state_id: int, district_name: str, lat: float, lon: float) -> int:
    """Return district_id for (state_id, district_name), creating it if needed."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT district_id FROM districts WHERE state_id = %s AND district_name = %s",
            (state_id, district_name),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute(
            "INSERT INTO districts (state_id, district_name, latitude, longitude) "
            "VALUES (%s, %s, %s, %s)",
            (state_id, district_name, lat, lon),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_or_create_river(station: dict) -> int:
    """Return river_id for a station dict from config.RIVER_STATIONS,
    creating the row if needed (and refreshing its thresholds)."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT river_id FROM rivers WHERE river_name = %s AND station_name = %s",
            (station["river"], station["station"]),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute(
            """
            INSERT INTO rivers
                (river_name, station_name, state_name, latitude, longitude,
                 normal_level, warning_level, danger_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                station["river"], station["station"], station["state"],
                station["lat"], station["lon"],
                station["normal_level"], station["warning_level"], station["danger_level"],
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
