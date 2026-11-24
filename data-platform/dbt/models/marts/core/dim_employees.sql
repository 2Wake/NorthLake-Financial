-- Excludes: ssn (Secret); salary, performance_rating (Confidential).
select
    employee_id, first_name, last_name, email as work_email, department, title, pay_type,
    hired_at, employment_status, terminated_at, record_updated_at as updated_at
from {{ ref('stg_hris_employees') }}
