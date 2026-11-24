-- Card numbers are masked to the last 4 digits (allowed for display under PCI DSS), and only
-- for well-formed numbers. Excludes: card_number, card_expiry, cardholder_name (Secret).
select
    card_id, rider_id,
    if(regexp_contains(card_number, r'^\d{4} \d{4} \d{4} \d{4}$'), right(card_number, 4), null) as card_last4,
    card_status, added_at, record_updated_at as updated_at
from {{ ref('stg_payments_rider_cards') }}
