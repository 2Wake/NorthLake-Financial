-- One row per zone. The public table has duplicate and missing zone IDs (rules REF-01 to REF-03),
-- so duplicates are collapsed and missing zones are added from the taxi_zone_supplement seed.
with public_zones as (
    select zone_id, any_value(zone_name) as zone_name, any_value(borough) as borough,
           any_value(zone_geom) as zone_geom, 'tlc_public_table' as zone_source
    from {{ ref('stg_tlc_taxi_zones') }}
    group by zone_id
),
supplement as (
    select cast(zone_id as string) as zone_id, zone_name, borough,
           cast(null as geography) as zone_geom, 'supplement' as zone_source
    from {{ ref('taxi_zone_supplement') }}
    where cast(zone_id as string) not in (select zone_id from public_zones)
)
select * from public_zones
union all
select * from supplement
