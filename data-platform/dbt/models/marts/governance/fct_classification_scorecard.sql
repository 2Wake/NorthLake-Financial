{#- Compares the classification register with the answer key, one row per column that
    should be classified. Shows whether the register is right, and whether any check
    (fct_classification_findings) flagged the problem. The only model that reads the answer key. -#}

with
answer_key as (select * from {{ ref('column_classification_answer_key') }}),
register   as (select * from {{ ref('column_classification_register') }}),
findings   as (select * from {{ ref('fct_classification_findings') }}),
tiers as (
    select * from unnest([
        struct('Public' as tier, 1 as rnk), ('Internal', 2), ('Sensitive', 3), ('Confidential', 4), ('Secret', 5)
    ])
),
flags as (
    -- a finding on the column itself, or a table-level finding (column '*') on its table
    select k.layer, k.table_name, k.column_name,
           array_agg(distinct f.rule_id ignore nulls order by f.rule_id) as flagged_by
    from answer_key k
    join findings f
      on f.layer = k.layer and f.table_name = k.table_name and f.column_name in (k.column_name, '*')
    group by 1, 2, 3
)

select
    k.layer,
    k.table_name,
    k.column_name,
    k.classification as expected_classification,
    r.classification as recorded_classification,
    case
        when r.column_name is null then 'missing'
        when tr.rnk is null then 'invalid_value'
        when tr.rnk = tk.rnk then 'correct'
        when tr.rnk < tk.rnk then 'under_classified'
        else 'over_classified'
    end as verdict,
    k.classification in ('Secret', 'Confidential') as is_high_risk,
    r.status,
    coalesce(fl.flagged_by, []) as flagged_by,
    array_length(coalesce(fl.flagged_by, [])) > 0 as is_flagged,
    k.rationale,
    current_timestamp() as evaluated_at
from answer_key k
left join register r using (layer, table_name, column_name)
left join tiers tk on tk.tier = k.classification
left join tiers tr on tr.tier = r.classification
left join flags fl using (layer, table_name, column_name)
