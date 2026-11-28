-- SIMULATED policy acknowledgments collected by HR (generator 0.5.0 onward): one row per employee per
-- document acknowledged. Events, so each row arrives once; the New York date is added for due-date checks.
select
    *,
    date(acknowledged_at, 'America/New_York') as acknowledged_on
from {{ source('raw', 'hris_policy_acknowledgments') }}
