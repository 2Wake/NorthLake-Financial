select access_role, dataset, domain_scope, privilege, max_classification, time_bound_days, approver_role, purpose
from {{ ref('access_policy') }}
