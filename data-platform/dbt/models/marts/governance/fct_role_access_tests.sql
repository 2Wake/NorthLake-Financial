-- Latest access check of each role account, judged against the access policy matrix.
-- expected = allow when the policy gives the account's access role any access to the dataset.
--   ACC-08  excess access:  observed allow, policy says deny
--   ACC-09  missing access: observed deny,  policy says allow
--   ACC-10  check failed:   the check itself errored (no result)
with latest as (
    select * from {{ ref('stg_iam_role_access_tests') }}
    where run_date = (select max(run_date) from {{ ref('stg_iam_role_access_tests') }})
),
allowed as (
    select distinct access_role, dataset from {{ ref('access_policy') }}
),
judged as (
    select
        t.run_date, t.tested_at, t.service_account, a.access_role, t.dataset, t.method, t.probe_table,
        if(p.access_role is null, 'deny', 'allow') as expected,
        t.observed, t.detail
    from latest t
    left join {{ ref('role_service_accounts') }} a using (service_account)
    left join allowed p on p.access_role = a.access_role and p.dataset = t.dataset
)
select
    *,
    case
        when observed = 'error' then 'ACC-10'
        when observed = 'allow' and expected = 'deny' then 'ACC-08'
        when observed = 'deny' and expected = 'allow' then 'ACC-09'
    end as rule_id,
    case
        when observed = 'error' then 'error'
        when observed = expected then 'pass'
        else 'fail'
    end as result
from judged
