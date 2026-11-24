-- Current warehouse access, with names and departments, for access reviews.
select
    g.grant_id,
    g.employee_id,
    concat(e.first_name, ' ', e.last_name) as employee_name,
    e.department as employee_department,
    e.title as employee_title,
    e.employment_status,
    g.access_role,
    g.dataset,
    g.domain_scope,
    g.privilege,
    g.granted_for_department,
    g.request_ticket,
    g.approved_by,
    concat(a.first_name, ' ', a.last_name) as approver_name,
    a.role_code as approver_role_code,
    g.granted_at,
    g.expires_at,
    g.revoked_at,
    g.revoke_reason,
    g.grant_status
from {{ ref('stg_iam_access_grants') }} g
left join {{ ref('stg_hris_employees') }} e on e.employee_id = g.employee_id
left join {{ ref('stg_hris_employees') }} a on a.employee_id = g.approved_by
