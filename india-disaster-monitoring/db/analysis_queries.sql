-- ============================================================================
-- India Disaster Monitoring System -- Analysis Queries
-- Run these directly via the mysql CLI / a GUI tool, or adapt them inside
-- core/database.py's fetch_all() for use elsewhere in the app.
-- ============================================================================

USE india_disaster_monitoring;

-- ----------------------------------------------------------------------------
-- 1. States with the highest rainfall (today)
-- ----------------------------------------------------------------------------
SELECT
    s.state_name,
    COUNT(*)                      AS readings,
    ROUND(AVG(r.rainfall_mm), 2)  AS avg_rainfall_mm,
    ROUND(MAX(r.rainfall_mm), 2)  AS peak_rainfall_mm
FROM rainfall_data r
JOIN districts d ON r.district_id = d.district_id
JOIN states s    ON d.state_id    = s.state_id
WHERE DATE(r.recorded_at) = CURDATE()
GROUP BY s.state_name
ORDER BY avg_rainfall_mm DESC
LIMIT 10;

-- Variant: highest rainfall states over the last 7 days
-- SELECT s.state_name, ROUND(AVG(r.rainfall_mm), 2) AS avg_rainfall_mm
-- FROM rainfall_data r
-- JOIN districts d ON r.district_id = d.district_id
-- JOIN states s    ON d.state_id    = s.state_id
-- WHERE r.recorded_at >= NOW() - INTERVAL 7 DAY
-- GROUP BY s.state_name
-- ORDER BY avg_rainfall_mm DESC
-- LIMIT 10;


-- ----------------------------------------------------------------------------
-- 2. Districts / stations currently under flood alert
--    ("currently" = most recent alert per river is still Danger/Severe and
--     was raised within the last 24 hours)
-- ----------------------------------------------------------------------------
SELECT
    r.river_name,
    r.station_name,
    r.state_name,
    fa.water_level,
    fa.danger_level,
    fa.severity,
    fa.alert_message,
    fa.created_at
FROM flood_alerts fa
JOIN rivers r ON fa.river_id = r.river_id
WHERE fa.id IN (
    SELECT MAX(id) FROM flood_alerts GROUP BY river_id
)
AND fa.severity IN ('Danger', 'Severe')
AND fa.created_at >= NOW() - INTERVAL 24 HOUR
ORDER BY fa.water_level DESC;


-- ----------------------------------------------------------------------------
-- 3. Recent earthquakes (last 30 days, magnitude >= 5.0, most recent first)
-- ----------------------------------------------------------------------------
SELECT
    place,
    magnitude,
    depth_km,
    latitude,
    longitude,
    event_time
FROM earthquakes
WHERE event_time >= NOW() - INTERVAL 30 DAY
  AND magnitude >= 5.0
ORDER BY event_time DESC;

-- Variant: strongest earthquakes in the period, regardless of recency
-- SELECT place, magnitude, depth_km, event_time
-- FROM earthquakes
-- WHERE event_time >= NOW() - INTERVAL 30 DAY
-- ORDER BY magnitude DESC
-- LIMIT 20;


-- ----------------------------------------------------------------------------
-- 4. Rainfall trends for the last 30 days (daily average + peak across India)
-- ----------------------------------------------------------------------------
SELECT
    DATE(recorded_at)             AS day,
    ROUND(AVG(rainfall_mm), 2)    AS avg_rainfall_mm,
    ROUND(MAX(rainfall_mm), 2)    AS peak_rainfall_mm,
    COUNT(*)                      AS readings
FROM rainfall_data
WHERE recorded_at >= NOW() - INTERVAL 30 DAY
GROUP BY DATE(recorded_at)
ORDER BY day ASC;

-- Variant: rainfall trend for a single state over the last 30 days
-- SELECT DATE(r.recorded_at) AS day, ROUND(AVG(r.rainfall_mm), 2) AS avg_rainfall_mm
-- FROM rainfall_data r
-- JOIN districts d ON r.district_id = d.district_id
-- JOIN states s    ON d.state_id    = s.state_id
-- WHERE s.state_name = 'Kerala'
--   AND r.recorded_at >= NOW() - INTERVAL 30 DAY
-- GROUP BY DATE(r.recorded_at)
-- ORDER BY day ASC;


-- ----------------------------------------------------------------------------
-- Bonus: today's headline summary (used by the dashboard's /api/summary)
-- ----------------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM rainfall_data WHERE DATE(recorded_at) = CURDATE())      AS rainfall_records_today,
    (SELECT ROUND(AVG(rainfall_mm), 2) FROM rainfall_data WHERE DATE(recorded_at) = CURDATE()) AS avg_rainfall_today_mm,
    (SELECT COUNT(*) FROM flood_alerts WHERE DATE(created_at) = CURDATE())       AS flood_alerts_today,
    (SELECT COUNT(*) FROM earthquakes WHERE event_time >= NOW() - INTERVAL 30 DAY) AS earthquakes_last_30_days,
    (SELECT COUNT(*) FROM cyclone_alerts WHERE DATE(issued_at) = CURDATE())      AS cyclone_advisories_today;
