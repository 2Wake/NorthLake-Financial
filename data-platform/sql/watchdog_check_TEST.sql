-- TEST COPY of watchdog_check.sql (setup part J3): always checks, so it fails until today's run has finished.
-- ECT watchdog, Google side (POL-09 statement 18; GOV-123, R-003). BigQuery scheduled query, runs as ect-watchdog.
-- Two schedules (16:05 and 17:05 UTC); only the run that lands at 12:xx New York checks, so it follows daylight saving.
-- Reads metadata only (partition list, table change times), never table contents.
-- Fails on purpose (ERROR) when the daily run hasn't finished. A Cloud Monitoring log alert on that error emails the
-- maintainer (setup part J3); BigQuery's own failure email doesn't arrive when the query runs as a service account.
DECLARE check_day DATE DEFAULT CURRENT_DATE('America/New_York');
DECLARE ny_hour INT64 DEFAULT 12;  -- TEST COPY: time check disabled. Delete this scheduled query after the test.
DECLARE latest_batch DATE;
DECLARE oldest_mart_rebuild DATE;

IF ny_hour != 12 THEN
  SELECT FORMAT('Skipped: %d:xx in New York, not the 12:00 check.', ny_hour) AS result;
  RETURN;
END IF;

SET latest_batch = (
  SELECT MAX(PARSE_DATE('%Y%m%d', partition_id))
  FROM `empire-city-taxi.raw.INFORMATION_SCHEMA.PARTITIONS`
  WHERE table_name = 'app_trips' AND REGEXP_CONTAINS(partition_id, r'^\d{8}$'));
-- Oldest rebuild among the marts tables: each table's latest change, then the earliest of those.
-- INFORMATION_SCHEMA, not the legacy __TABLES__ view: __TABLES__ needs permission to read table data,
-- which ect-watchdog doesn't have (test J3, 2026-11-27, GOV-170).
SET oldest_mart_rebuild = (
  SELECT DATE(MIN(table_changed), 'America/New_York')
  FROM (
    SELECT p.table_name, MAX(p.last_modified_time) AS table_changed
    FROM `empire-city-taxi.marts.INFORMATION_SCHEMA.PARTITIONS` AS p
    JOIN `empire-city-taxi.marts.INFORMATION_SCHEMA.TABLES` AS t USING (table_name)
    WHERE t.table_type = 'BASE TABLE'
    GROUP BY p.table_name));

IF latest_batch >= DATE_SUB(check_day, INTERVAL 1 DAY) AND oldest_mart_rebuild >= check_day THEN
  SELECT FORMAT('OK: daily run complete for %t (raw through %t; marts rebuilt %t).', check_day, latest_batch, oldest_mart_rebuild) AS result;
ELSE
  SELECT ERROR(FORMAT(
    'ECT WATCHDOG %s: the daily run has not completed by 12:00 New York on %t. raw.app_trips is loaded through %t (expected %t); the oldest marts table was rebuilt on %t (expected %t). Respond within 1 business day (POL-09 statement 18): check GitHub Actions, run the daily refresh by hand, and record the cause in Jira.',
    IF(latest_batch < DATE_SUB(check_day, INTERVAL 2 DAY), 'SEV3 (2 days in a row)', 'SEV4'),
    check_day, latest_batch, DATE_SUB(check_day, INTERVAL 1 DAY), oldest_mart_rebuild, check_day));
END IF;
