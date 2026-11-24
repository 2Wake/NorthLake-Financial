-- Observed, not generated: every access check ever run (one row per account, dataset and method per run).
select run_date, tested_at, service_account, dataset, probe_table, method, observed, detail, _batch_date
from {{ source('raw', 'iam_role_access_tests') }}
