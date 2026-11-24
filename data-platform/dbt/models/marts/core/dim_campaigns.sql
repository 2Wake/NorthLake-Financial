select campaign_id, name, channel, start_date, end_date, budget, target_segment_id,
       record_updated_at as updated_at
from {{ ref('stg_app_marketing_campaigns') }}
