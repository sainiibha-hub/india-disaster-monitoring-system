-- ============================================================================
-- India Disaster Monitoring System -- Database Schema
-- This file mirrors exactly what core/database.py's create_database() and
-- create_tables() produce. You normally don't need to run this by hand --
-- `python main.py --setup` does it for you -- but it's provided so the
-- schema can be reviewed, versioned, or applied manually (e.g. via the
-- mysql CLI or a GUI tool).
-- ============================================================================

CREATE DATABASE IF NOT EXISTS india_disaster_monitoring
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE india_disaster_monitoring;

-- ---------------------------------------------------------------------------
-- Reference data: states and districts
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS states (
    state_id INT AUTO_INCREMENT PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

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

-- ---------------------------------------------------------------------------
-- Rainfall monitoring
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Flood monitoring: river gauge stations, readings, and alerts
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Earthquake monitoring (USGS)
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Cyclone monitoring (IMD-style advisories)
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Daily reports
-- ---------------------------------------------------------------------------
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
