-- ONE-TIME SETUP: copy a fixed 1% sample of the real 2022 NYC yellow-taxi trips
-- (public NYC TLC open data) into raw.tlc_yellow_trips_sample.
--
-- Cost: scans ~6.8 GB of the public table once (under 1% of the 1 TB monthly free
-- tier, and under the ~30 GB daily quota). After this, the generator only reads one
-- day-partition of our own copy at a time.
--
-- The sample is deterministic (a hash of each trip, not random sampling), so the
-- same trips are selected every time this runs. Expect roughly 360,000 rows.
-- The public data is genuinely messy: negative fares,
-- zero distances, dropoff before pickup. Those are kept: they are real DQ findings.

CREATE TABLE IF NOT EXISTS `empire-city-taxi.raw.tlc_yellow_trips_sample`
PARTITION BY DATE(pickup_datetime)
OPTIONS (
  description = "Fixed 1% sample of the public NYC TLC 2022 yellow-taxi trips (bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022). Replayed by the generator as Empire City Taxi trips.",
  labels = [("domain", "trips"), ("layer", "raw"), ("data_owner", "vp-operations"),
            ("data_steward", "ops-data-steward"), ("classification", "public"),
            ("source_system", "tlc"), ("data_origin", "public"), ("contains_pii", "false"),
            ("pci_scope", "false"), ("retention", "indefinite")]
)
AS
SELECT
  CAST(FARM_FINGERPRINT(CONCAT(
    CAST(pickup_datetime AS STRING), '|', CAST(dropoff_datetime AS STRING), '|',
    IFNULL(pickup_location_id, ''), '|', IFNULL(dropoff_location_id, ''), '|',
    CAST(total_amount AS STRING), '|', IFNULL(vendor_id, ''))) AS STRING) AS tlc_sample_key,
  vendor_id, pickup_datetime, dropoff_datetime, passenger_count, trip_distance, rate_code,
  payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, imp_surcharge,
  airport_fee, total_amount, pickup_location_id, dropoff_location_id
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
WHERE pickup_datetime >= '2022-01-01' AND pickup_datetime < '2023-01-01'
  AND MOD(ABS(FARM_FINGERPRINT(CONCAT(
    CAST(pickup_datetime AS STRING), '|', CAST(dropoff_datetime AS STRING), '|',
    IFNULL(pickup_location_id, ''), '|', IFNULL(dropoff_location_id, ''), '|',
    CAST(total_amount AS STRING), '|', IFNULL(vendor_id, '')))), 100) = 0;
