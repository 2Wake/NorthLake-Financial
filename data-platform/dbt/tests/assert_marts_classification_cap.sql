{#- Governance control: marts may hold data up to Sensitive (Data Classification Standard).
    Fails for any marts table that
      * has no classification label, or a label above Sensitive, or
      * contains a column that is Secret or Confidential in raw (by column name).
    Each failing row names the table and the problem. -#}
{%- set marts = ['dim_employees', 'dim_drivers', 'dim_riders', 'dim_rider_cards', 'dim_taxi_zones',
                 'dim_campaigns', 'dim_rider_segments', 'dim_dq_rules', 'fct_trips',
                 'fct_daily_zone_trips', 'fct_trip_surveys', 'fct_ledger_entries',
                 'fct_dq_findings', 'fct_dq_scorecard', 'fct_access_grants', 'dim_access_policy', 'fct_role_access_tests', 'fct_role_access_scorecard',
                 'fct_classification_findings', 'fct_classification_scorecard'] %}
{%- for m in marts %}
-- depends_on: {{ ref(m) }}
{%- endfor %}

with tables as (
    select table_name
    from `{{ target.project }}.marts.INFORMATION_SCHEMA.TABLES`
),
labels as (
    select table_name,
           regexp_extract(option_value, r'"classification", "([a-z]+)"') as classification
    from `{{ target.project }}.marts.INFORMATION_SCHEMA.TABLE_OPTIONS`
    where option_name = 'labels'
),
-- Secret and Confidential columns from the column classification map, as named in raw
restricted_columns as (
    select column_name from unnest([
        'ssn', 'payout_bank_account', 'card_number', 'card_expiry', 'cardholder_name',
        'phone', 'home_address', 'tlc_license', 'background_check_status', 'salary',
        'performance_rating', 'comment', 'email', 'pickup_location_id', 'dropoff_location_id'
    ]) as column_name
)

select t.table_name, concat('classification label is ', coalesce(l.classification, 'missing')) as problem
from tables t
left join labels l using (table_name)
where l.classification is null or l.classification not in ('sensitive', 'internal', 'public')

union all

select c.table_name, concat('restricted column present: ', c.column_name)
from `{{ target.project }}.marts.INFORMATION_SCHEMA.COLUMNS` c
join restricted_columns r using (column_name)
