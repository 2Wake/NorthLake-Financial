-- pull_trip_sample.sql
-- Create the ECT `trips` table from the PUBLIC NYC TLC dataset, with synthetic
-- driver_id / rider_id columns so the real trips link to the generated
-- drivers (1..300) and riders (1..2000) tables.
--
-- Usage: replace PROJECT with your BigQuery project id and run in the BigQuery
-- console or: bq query --use_legacy_sql=false < pull_trip_sample.sql
--
-- Cost note: TABLESAMPLE reads a fraction of the table, keeping bytes scanned
-- (and your free 1 TB/month) in check. If the 2022 table name has changed,
-- point it at any tlc_yellow_trips_<year> table that exists.

CREATE SCHEMA IF NOT EXISTS `PROJECT.ect`;

CREATE OR REPLACE TABLE `PROJECT.ect.trips` AS
WITH sampled AS (
  SELECT
    pickup_datetime, dropoff_datetime, passenger_count, trip_distance,
    fare_amount, tip_amount, tolls_amount, total_amount, payment_type,
    pickup_location_id, dropoff_location_id
  FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
       TABLESAMPLE SYSTEM (2 PERCENT)
  LIMIT 100000
),
numbered AS (
  SELECT ROW_NUMBER() OVER () AS trip_id, s.*
  FROM sampled AS s
)
SELECT
  trip_id,
  MOD(trip_id - 1, 300) + 1        AS driver_id,   -- FK -> drivers (1..300)
  MOD((trip_id - 1) * 7, 2000) + 1 AS rider_id,     -- FK -> riders  (1..2000)
  pickup_datetime, dropoff_datetime, passenger_count, trip_distance,
  fare_amount, tip_amount, tolls_amount, total_amount, payment_type,
  pickup_location_id, dropoff_location_id
FROM numbered;

-- The public data is genuinely messy. After loading, the data-quality SQL in
-- governance/data-quality-rules.md finds negative fares, impossible passenger
-- counts, zero/absurd distances, dropoff-before-pickup, and totals that don't
-- reconcile — issues you did NOT seed, which is the point.
