select rule_id, dimension, table_name, column_name, severity, expectation, origin
from {{ ref('dq_rules') }}
