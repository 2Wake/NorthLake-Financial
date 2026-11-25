-- Excludes: ssn_last4, payout_account_last4, payout_account_token, tlc_license, phone, home_address,
-- background_check_status (Confidential).
select
    driver_id, employee_id, first_name, last_name, driver_status, hired_at,
    status_changed_at, record_updated_at as updated_at
from {{ ref('stg_fleet_drivers') }}
