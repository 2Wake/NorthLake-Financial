-- Did the access check catch each planted role-account misconfiguration, by config and by enforcement?
-- The only reader of the role_account_answer_key seed. Also lists failures nobody planted.
with failures as (
    select service_account, dataset, rule_id,
           logical_or(method = 'config') as caught_by_config,
           logical_or(method = 'enforcement') as caught_by_enforcement
    from {{ ref('fct_role_access_tests') }}
    where result = 'fail'
    group by 1, 2, 3
)
select
    coalesce(k.service_account, f.service_account) as service_account,
    coalesce(k.dataset, f.dataset) as dataset,
    coalesce(k.rule_id, f.rule_id) as rule_id,
    k.service_account is not null as planted,
    k.note as planted_note,
    coalesce(f.caught_by_config, false) as caught_by_config,
    coalesce(f.caught_by_enforcement, false) as caught_by_enforcement
from {{ ref('role_account_answer_key') }} k
full outer join failures f
    on f.service_account = k.service_account and f.dataset = k.dataset and f.rule_id = k.rule_id
