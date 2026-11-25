{#- Every record that fails a data-quality rule, one row per (rule, record).
    Uses only the data itself. It never reads the answer key (gov_planted_defects). -#}

with
riders    as (select * from {{ ref('stg_app_riders') }}),
drivers   as (select * from {{ ref('stg_fleet_drivers') }}),
employees as (select * from {{ ref('stg_hris_employees') }}),
cards     as (select * from {{ ref('stg_payments_rider_cards') }}),
surveys   as (select * from {{ ref('stg_app_trip_surveys') }}),
trips     as (select * from {{ ref('stg_app_trips') }}),
campaigns as (select * from {{ ref('stg_app_marketing_campaigns') }}),
ledger    as (select * from {{ ref('stg_payments_financial_ledger') }}),
zones     as (select * from {{ ref('stg_tlc_taxi_zones') }}),
grants    as (select * from {{ ref('stg_iam_access_grants') }}),
policy    as (select * from {{ ref('access_policy') }}),
as_of     as (select max(_batch_date) as as_of_date from {{ ref('stg_app_trips') }}),

-- ACC-07: who should have approved each grant. Domain-owner approvals resolve to the owner of the
-- grant's domain; nobody approves their own access, so that case escalates to the CDO (or the CEO
-- for the CDO's own access).
expected_approver as (
    select g.grant_id, g.employee_id, g.approved_by,
           if(h.employee_id = g.employee_id, if(b.base_role = 'cdo', 'ceo', 'cdo'), b.base_role) as expected_role
    from grants g
    join (
        select g2.grant_id,
               case p.approver_role
                   when 'domain-owner' then case g2.domain_scope
                       when 'rider' then 'vp-rider-experience' when 'driver' then 'vp-driver-operations'
                       when 'trips' then 'vp-operations' when 'finance' then 'cfo' when 'people' then 'vp-people'
                       when 'marketing' then 'vp-marketing' when 'risk' then 'ciso'
                       when 'governance' then 'data-governance-manager' end
                   else p.approver_role
               end as base_role
        from grants g2
        join policy p using (access_role, dataset)
    ) b using (grant_id)
    left join employees h on h.role_code = b.base_role
    where g.approved_by is not null and g.approved_by != g.employee_id
),

findings as (
    select 'DQ-01' as rule_id, rider_id as record_id from riders where email is null
    union all
    select 'DQ-02', rider_id from riders where not regexp_contains(email, r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    union all
    select 'DQ-03', rider_id from riders where email is not null
        qualify row_number() over (partition by email order by rider_id) > 1
    union all
    select 'DQ-04', driver_id from drivers where not regexp_contains(ssn_last4, r'^\d{4}$')
    union all
    select 'DQ-05', driver_id from drivers where tlc_license is null
    union all
    select 'DQ-06', driver_id from drivers where background_check_status not in ('clear', 'pending', 'flagged')
    union all
    select 'DQ-07', card_id from cards where card_last4 is null or not regexp_contains(card_last4, r'^\d{4}$')
    union all
    select 'DQ-08', survey_id from surveys where rating not between 1 and 5
    union all
    select 'DQ-09', s.survey_id from surveys s left join trips t using (trip_id) where t.trip_id is null
    union all
    select 'DQ-10', survey_id from surveys
        where regexp_contains(comment, r'\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|[\w.+-]+@[\w-]+\.[\w.]+')
    union all
    select 'DQ-11', employee_id from employees where salary <= 0
    union all
    select 'DQ-12', campaign_id from campaigns where end_date < start_date
    union all
    select 'DQ-13', employee_id from employees where not regexp_contains(ssn_last4, r'^\d{4}$')
    union all
    select 'DQ-14', employee_id from employees where email is not null
        qualify row_number() over (partition by email order by employee_id) > 1
    union all
    select 'DQ-15', entry_id from ledger where account is null
    union all
    select 'DQ-16', driver_id from drivers where not regexp_contains(payout_account_last4, r'^\d{4}$')
    union all
    select 'ACC-01', g.grant_id from grants g left join policy p using (access_role, dataset)
        where g.grant_status = 'active' and p.access_role is null
    union all
    select 'ACC-02', g.grant_id from grants g join employees e using (employee_id)
        where g.grant_status = 'active' and e.employment_status = 'terminated'
    union all
    select 'ACC-03', g.grant_id from grants g join employees e using (employee_id)
        where g.grant_status = 'active' and g.granted_for_department != e.department
    union all
    select 'ACC-04', grant_id from grants where approved_by = employee_id
    union all
    select 'ACC-05', g.grant_id from grants g cross join as_of
        where g.grant_status = 'active' and g.expires_at < as_of.as_of_date
    union all
    select 'ACC-06', grant_id from grants where approved_by is null or request_ticket is null
    union all
    select 'ACC-07', x.grant_id from expected_approver x left join employees a on a.employee_id = x.approved_by
        where a.role_code is distinct from x.expected_role
    union all
    select 'T1', trip_id from trips where fare_amount <= 0
    union all
    select 'T2', trip_id from trips where passenger_count is null or passenger_count not between 1 and 6
    union all
    select 'T3', trip_id from trips where trip_distance <= 0 or trip_distance > 100
    union all
    select 'T4', trip_id from trips where dropoff_datetime < pickup_datetime
    union all
    select 'REF-01', zone_id from zones where true
        qualify row_number() over (partition by zone_id order by zone_name) > 1
    union all
    select 'REF-02', t.trip_id from trips t left join zones z on z.zone_id = t.pickup_location_id
        where z.zone_id is null
    union all
    select 'REF-03', t.trip_id from trips t left join zones z on z.zone_id = t.dropoff_location_id
        where z.zone_id is null
)

select
    f.rule_id,
    r.table_name,
    f.record_id,
    r.column_name,
    r.dimension,
    r.severity,
    r.origin,
    current_timestamp() as evaluated_at
from findings f
join {{ ref('dq_rules') }} r using (rule_id)
