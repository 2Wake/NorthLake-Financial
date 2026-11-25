-- Who must acknowledge each approved policy, by when, and whether they have.
-- Derived, so the list follows headcount every day: one row per ACTIVE employee (drivers included)
-- per approved policy version in the Policy Register. Owner decision 2026-11-24: all staff
-- acknowledge every approved policy (POL-01 statement 6 names POL-01 and POL-05 as the minimum).
-- Rule (POL-01 statement 6; STD-01 section 11): due 10 business days after the later of the
-- approval date and the hire date. Weekends are skipped; public holidays are not.
-- The yearly re-acknowledgment cycle is not modelled yet (first one falls due Nov 2027).
-- Acknowledgments received come from the policy_acknowledgments seed (the only record of them).
with policies as (
    select doc_id, version as doc_version, approval_date
    from {{ ref('policy_register') }}
    where doc_type = 'policy' and status = 'approved'
),
staff as (
    select employee_id, department, hired_at
    from {{ ref('stg_hris_employees') }}
    where employment_status = 'active'
),
required as (
    select
        s.employee_id,
        s.department,
        p.doc_id,
        p.doc_version,
        greatest(p.approval_date, coalesce(s.hired_at, p.approval_date)) as assigned_on
    from staff s
    cross join policies p
),
received as (
    select employee_id, doc_id, doc_version,
           min(acknowledged_on) as acknowledged_on,
           string_agg(evidence, '; ' order by acknowledged_on) as evidence
    from {{ ref('policy_acknowledgments') }}
    where acknowledged_on is not null
    group by 1, 2, 3
),
dated as (
    select
        r.*,
        (
            select max(d) from (
                select d
                from unnest(generate_date_array(date_add(r.assigned_on, interval 1 day),
                                                date_add(r.assigned_on, interval 20 day))) as d
                where extract(dayofweek from d) not in (1, 7)
                order by d
                limit 10
            )
        ) as due_on
    from required r
)
select
    concat(d.employee_id, '|', d.doc_id, '|', d.doc_version) as ack_key,
    d.employee_id,
    d.department,
    d.doc_id,
    d.doc_version,
    d.assigned_on,
    d.due_on,
    a.acknowledged_on,
    a.evidence,
    case
        when a.acknowledged_on is not null then 'acknowledged'
        when current_date() > d.due_on then 'overdue'
        else 'pending'
    end as ack_status,
    a.acknowledged_on is not null and a.acknowledged_on <= d.due_on as on_time
from dated d
left join received a
    on a.employee_id = d.employee_id and a.doc_id = d.doc_id and a.doc_version = d.doc_version
