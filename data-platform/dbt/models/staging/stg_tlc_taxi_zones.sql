select zone_id, zone_name, borough, zone_geom
from {{ source('raw', 'tlc_taxi_zones') }}
