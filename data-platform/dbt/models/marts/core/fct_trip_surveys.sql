-- Free-text comments may contain personal data (Confidential). They are masked here:
-- phone numbers and email addresses become [REDACTED].
select
    survey_id, trip_id, rider_id, rating,
    regexp_replace(comment, r'\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|[\w.+-]+@[\w-]+\.[\w.]+', '[REDACTED]') as comment_redacted,
    submitted_at
from {{ ref('stg_app_trip_surveys') }}
