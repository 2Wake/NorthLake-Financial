{{ config(materialized='table', partition_by={'field': 'pickup_date', 'data_type': 'date'}) }}
-- Zone-level demand and revenue per day. Aggregated, with no rider or driver IDs.
select
    date(t.pickup_datetime) as pickup_date,
    t.pickup_location_id as pickup_zone_id,
    z.zone_name as pickup_zone_name,
    z.borough as pickup_borough,
    count(*) as trips,
    countif(t.rider_id is not null) as app_bookings,
    sum(t.fare_amount) as fare_amount,
    sum(t.tip_amount) as tip_amount,
    sum(t.total_amount) as total_amount,
    avg(t.trip_distance) as avg_trip_distance
from {{ ref('stg_app_trips') }} t
left join {{ ref('dim_taxi_zones') }} z on z.zone_id = t.pickup_location_id
group by 1, 2, 3, 4
