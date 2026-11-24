select segment_id, name, definition, size_estimate, record_updated_at as updated_at
from {{ ref('stg_app_rider_segments') }}
