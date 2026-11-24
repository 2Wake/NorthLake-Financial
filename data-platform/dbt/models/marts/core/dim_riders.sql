-- Excludes: email, phone, home_address (Confidential).
select
    rider_id, first_name, last_name, created_at, account_status, closed_at,
    record_updated_at as updated_at
from {{ ref('stg_app_riders') }}
