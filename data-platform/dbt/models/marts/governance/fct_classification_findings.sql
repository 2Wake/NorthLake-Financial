{#- Checks on the column classification register (seeds/governance/column_classification_register.csv).
    One row per problem found. Uses the register and BigQuery's own metadata only; it never
    reads the answer key. -#}
{%- set datasets = ['raw', 'staging', 'marts'] %}

with
register as (select * from {{ ref('column_classification_register') }}),

tiers as (
    select * from unnest([
        struct('Public' as tier, 1 as rnk), ('Internal', 2), ('Sensitive', 3), ('Confidential', 4), ('Secret', 5)
    ])
),

physical_columns as (
    {%- for ds in datasets %}
    select '{{ ds }}' as layer, table_name, column_name
    from `{{ target.project }}.{{ ds }}.INFORMATION_SCHEMA.COLUMNS`
    {%- if not loop.last %} union all{% endif %}
    {%- endfor %}
),

table_labels as (
    {%- for ds in datasets %}
    select '{{ ds }}' as layer, table_name,
           regexp_extract(option_value, r'"classification", "([a-z]+)"') as label_classification,
           regexp_extract(option_value, r'"data_steward", "([a-z-]+)"') as label_steward
    from `{{ target.project }}.{{ ds }}.INFORMATION_SCHEMA.TABLE_OPTIONS`
    where option_name = 'labels'
    {%- if not loop.last %} union all{% endif %}
    {%- endfor %}
),

register_ranked as (
    select r.*, t.rnk
    from register r
    left join tiers t on t.tier = r.classification
),

findings as (
    -- CLS-01 Coverage: a column exists in BigQuery but has no register entry
    select 'CLS-01' as rule_id, p.layer, p.table_name, p.column_name,
           'Column has no classification in the register' as detail
    from physical_columns p
    left join register r using (layer, table_name, column_name)
    where r.column_name is null

    union all
    -- CLS-02 Orphan: a register entry for a column that no longer exists
    select 'CLS-02', r.layer, r.table_name, r.column_name, 'Register entry for a column that does not exist'
    from register r
    left join physical_columns p using (layer, table_name, column_name)
    where p.column_name is null

    union all
    -- CLS-03 Not approved: still proposed, or never reviewed by the data owner
    select 'CLS-03', layer, table_name, column_name,
           concat('Status is ', coalesce(status, 'blank'), '; owner approval missing')
    from register
    where coalesce(status, '') != 'approved' or coalesce(approved_by, '') = ''

    union all
    -- CLS-04 Table label vs columns: the table's classification label should equal its highest column classification
    select 'CLS-04', l.layer, l.table_name, '*',
           concat('Table label is ', l.label_classification, ' but highest column classification is ',
                  lower(coalesce(m.top_tier, 'none')))
    from table_labels l
    left join (
        select layer, table_name, array_agg(classification order by rnk desc limit 1)[offset(0)] as top_tier
        from register_ranked where rnk is not null
        group by 1, 2
    ) m using (layer, table_name)
    where lower(coalesce(m.top_tier, '')) != l.label_classification

    union all
    -- CLS-05 Lineage drift: a staging column inherited from raw has a different classification than
    -- its raw source. Either side may be the wrong one, so both rows are flagged.
    select 'CLS-05', side.layer, side.table_name, side.column_name,
           concat('Staging says ', d.staging_class, ', raw source says ', d.raw_class)
    from (
        select s.table_name as stg_table, r.table_name as raw_table, s.column_name,
               s.classification as staging_class, r.classification as raw_class
        from register s
        join register r
          on r.layer = 'raw'
         and r.table_name = regexp_replace(regexp_replace(s.table_name, r'^stg_', ''), r'_history$', '')
         and r.column_name = s.column_name
        where s.layer = 'staging' and s.treatment = 'inherited' and s.classification != r.classification
    ) d
    cross join unnest([
        struct('staging' as layer, d.stg_table as table_name, d.column_name as column_name),
        struct('raw', d.raw_table, d.column_name)
    ]) side
    where true
    qualify row_number() over (partition by side.layer, side.table_name, side.column_name) = 1

    union all
    -- CLS-06 Marts cap: marts may hold data up to Sensitive
    select 'CLS-06', layer, table_name, column_name, concat('Classified ', classification, ' in marts (cap is Sensitive)')
    from register_ranked
    where layer = 'marts' and rnk > 3

    union all
    -- CLS-07 Steward mismatch: the register's steward differs from the table's data_steward label
    select 'CLS-07', r.layer, r.table_name, r.column_name,
           concat('Register steward ', r.data_steward, '; table label steward ', l.label_steward)
    from register r
    join table_labels l using (layer, table_name)
    where r.data_steward != l.label_steward

    union all
    -- CLS-08 Invalid value: not one of the five tiers, exactly as spelled in the standard
    select 'CLS-08', layer, table_name, column_name, concat('"', coalesce(classification, ''), '" is not a valid tier')
    from register_ranked
    where rnk is null
)

select
    rule_id,
    case rule_id
        when 'CLS-01' then 'Column not classified'
        when 'CLS-02' then 'Register entry for missing column'
        when 'CLS-03' then 'Classification not approved'
        when 'CLS-04' then 'Table label inconsistent with columns'
        when 'CLS-05' then 'Classification changes between raw and staging'
        when 'CLS-06' then 'Above the marts cap'
        when 'CLS-07' then 'Register steward differs from table label'
        when 'CLS-08' then 'Invalid classification value'
    end as rule_name,
    layer, table_name, column_name, detail,
    current_timestamp() as evaluated_at
from findings
