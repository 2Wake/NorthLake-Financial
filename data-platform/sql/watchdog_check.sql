-- ECT watchdog, Google side (POL-09 statement 18; GOV-123, R-003). BigQuery scheduled query, runs as ect-watchdog.
-- Two schedules (16:05 and 17:05 UTC); only the run that lands at 12:xx New York checks, so it follows daylight saving.
-- Reads metadata only (partition list, table change times), never table contents.
-- Fails on purpose (ERROR) when the daily run hasn't finished; BigQuery then emails the person who set up the schedule.
DECLARE check_day DATE DEFAULT CURRENT_DATE('America/New_York');
DECLARE ny_hour INT64 DEFAULT EXTRACT(HOUR FROM CURRENT_DATETIME('America/New_York'));
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
SET oldest_mart_rebuild = (
  SELECT DATE(TIMESTAMP_MILLIS(MIN(last_modified_time)), 'America/New_York')
  FROM `empire-city-taxi.marts.__TABLES__` WHERE type = 1);

IF latest_batch >= DATE_SUB(check_day, INTERVAL 1 DAY) AND oldest_mart_rebuild >= check_day THEN
  SELECT FORMAT('OK: daily run complete for %t (raw through %t; marts rebuilt %t).', check_day, latest_batch, oldest_mart_rebuild) AS result;
ELSE
  SELECT ERROR(FORMAT(
    'ECT WATCHDOG %s: the daily run has not completed by 12:00 New York on %t. raw.app_trips is loaded through %t (expected %t); the oldest marts table was rebuilt on %t (expected %t). Respond within 1 business day (POL-09 statement 18): check GitHub Actions, run the daily refresh by hand, and record the cause in Jira.',
    IF(latest_batch < DATE_SUB(check_day, INTERVAL 2 DAY), 'SEV3 (2 days in a row)', 'SEV4'),
    check_day, latest_batch, DATE_SUB(check_day, INTERVAL 1 DAY), oldest_mart_rebuild, check_day));
END IF;
