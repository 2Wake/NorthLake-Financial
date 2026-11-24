-- ONE-TIME SETUP: copy the 263 NYC taxi zones (public NYC TLC reference data) into
-- raw.tlc_taxi_zones. Trips' pickup_location_id / dropoff_location_id join to zone_id.
-- Cost: well under 1 GB scanned, once.

CREATE TABLE IF NOT EXISTS `empire-city-taxi.raw.tlc_taxi_zones`
OPTIONS (
  description = "NYC TLC taxi zones (bigquery-public-data.new_york_taxi_trips.taxi_zone_geom): zone id, name, borough and boundary.",
  labels = [("domain", "reference"), ("layer", "raw"), ("data_owner", "data-governance-manager"),
            ("data_steward", "ops-data-steward"), ("classification", "public"),
            ("source_system", "tlc"), ("data_origin", "public"), ("contains_pii", "false"),
            ("pci_scope", "false"), ("retention", "indefinite")]
)
AS
SELECT zone_id, zone_name, borough, zone_geom
FROM `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom`;
