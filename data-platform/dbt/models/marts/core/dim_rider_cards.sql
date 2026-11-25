-- ECT holds only the processor's last 4 digits (generator 0.4.0), kept only when well formed.
-- Excludes: card_token (Confidential); card_expiry, cardholder_name (Secret).
select
    card_id, rider_id,
    if(regexp_contains(card_last4, r'^\d{4}$'), card_last4, null) as card_last4,
    card_status, added_at, record_updated_at as updated_at
from {{ ref('stg_payments_rider_cards') }}
