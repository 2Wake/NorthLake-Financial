-- Excludes (Confidential): ssn_last4, salary, performance_rating, screening_status, screening_date.
select
    employee_id, first_name, last_name, email as work_email, department, title, pay_type, manager_id, role_code,
    hired_at, employment_status, terminated_at, record_updated_at as updated_at
from {{ ref('stg_hris_employees') }}
