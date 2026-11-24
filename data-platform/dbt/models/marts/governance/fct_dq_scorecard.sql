{#- One row per data-quality rule: how many records fail it, and for planted defects, how
    many the rule caught or missed, compared with the answer key (gov_planted_defects).
    This model is the ONLY place the answer key is read. -#}

with
rules    as (select * from {{ ref('dq_rules') }}),
findings as (select distinct rule_id, record_id from {{ ref('fct_dq_findings') }}),
planted  as (
    select distinct r.rule_id, p.record_id
    from {{ ref('stg_gov_planted_defects') }} p
    join rules r on r.defect_code = p.defect_code
),
planted_stats as (
    select p.rule_id,
           count(*) as planted,
           countif(f.record_id is not null) as planted_caught
    from planted p
    left join findings f using (rule_id, record_id)
    group by 1
),
finding_stats as (
    select f.rule_id,
           count(*) as findings,
           countif(p.record_id is null) as unplanted_findings
    from findings f
    left join planted p using (rule_id, record_id)
    group by 1
)

select
    r.rule_id,
    r.dimension,
    r.severity,
    r.table_name,
    r.column_name,
    r.expectation,
    r.origin,
    coalesce(fs.findings, 0) as findings,
    coalesce(ps.planted, 0) as planted,
    coalesce(ps.planted_caught, 0) as planted_caught,
    coalesce(ps.planted, 0) - coalesce(ps.planted_caught, 0) as planted_missed,
    coalesce(fs.unplanted_findings, 0) as unplanted_findings,
    safe_divide(ps.planted_caught, ps.planted) as detection_rate,
    current_timestamp() as evaluated_at
from rules r
left join planted_stats ps using (rule_id)
left join finding_stats fs using (rule_id)
