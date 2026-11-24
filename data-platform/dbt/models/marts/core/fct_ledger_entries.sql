select entry_id, period, account, amount, currency, recorded_at
from {{ ref('stg_payments_financial_ledger') }}
