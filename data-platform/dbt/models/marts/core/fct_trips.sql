{{ config(
    materialized='table',
    partition_by={'field': 'pickup_date', 'data_type': 'date'},
    cluster_by=['driver_id']
) }}
-- Pickup and dropoff are generalized from zone to borough. A rider_id combined with
-- exact zones would reveal a person's movements (Confidential), which marts may not hold.
-- Zone-level analysis without riders is in fct_daily_zone_trips.
select
    t.trip_id,
    t.driver_id,
    t.rider_id,
    t.rider_id is not null as is_app_booking,
    date(t.pickup_datetime) as pickup_date,
    t.pickup_datetime,
    t.dropoff_datetime,
    pz.borough as pickup_borough,
    dz.borough as dropoff_borough,
    t.passenger_count,
    t.trip_distance,
    t.payment_type,
    case t.payment_type
        when '1' then 'credit_card' when '2' then 'cash' when '3' then 'no_charge'
        when '4' then 'dispute' when '5' then 'unknown' when '6' then 'voided'
        else 'other'
    end as payment_method,
    t.fare_amount,
    t.extra,
    t.mta_tax,
    t.tip_amount,
    t.tolls_amount,
    t.improvement_surcharge,
    t.airport_fee,
    t.total_amount,
    t._batch_date as batch_date
from {{ ref('stg_app_trips') }} t
left join {{ ref('dim_taxi_zones') }} pz on pz.zone_id = t.pickup_location_id
left join {{ ref('dim_taxi_zones') }} dz on dz.zone_id = t.dropoff_location_id
