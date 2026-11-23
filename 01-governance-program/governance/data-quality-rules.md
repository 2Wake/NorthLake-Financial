# NorthLake Data Quality Rules

*Fictional rule catalog for the NorthLake portfolio. Synthetic.*

Data quality is measured across six dimensions: **Completeness, Validity, Uniqueness, Consistency, Integrity, Timeliness**. Each rule below is implemented two ways: in [`run_data_quality.py`](../scripts/run_data_quality.py) (runs on the CSV estate, produces [`remediation_log.csv`](../data/remediation_log.csv)) and as BigQuery SQL (below), to run as a scheduled check or an OpenMetadata test.

## Rule catalog

| Rule | Dimension | Target | Severity | Expectation |
|---|---|---|---|---|
| DQ-01 | Completeness | `customers.email` | High | Email is present |
| DQ-02 | Validity | `customers.email` | Medium | Email matches a valid format |
| DQ-03 | Uniqueness | `customers.email` | High | Email is unique |
| DQ-04 | Validity (range) | `customers.date_of_birth` | High | DOB is not in the future |
| DQ-05 | Integrity | `accounts.customer_id` | High | FK exists in `customers` |
| DQ-06 | Consistency | `accounts.status` | Medium | Value ∈ {active, closed, suspended} |
| DQ-07 | Validity (range) | `lending_applications.credit_score` | High | 300 ≤ score ≤ 850 |
| DQ-08 | Completeness | `lending_applications.annual_income` | Medium | Income is present |

## BigQuery SQL (each returns the failing rows)

Replace `nl` with your dataset name.

```sql
-- DQ-01 Completeness: missing email
SELECT customer_id FROM `nl.customers` WHERE email IS NULL OR TRIM(email) = '';

-- DQ-02 Validity: malformed email
SELECT customer_id, email FROM `nl.customers`
WHERE email IS NOT NULL AND email != ''
  AND NOT REGEXP_CONTAINS(email, r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

-- DQ-03 Uniqueness: duplicate email
SELECT email, COUNT(*) c FROM `nl.customers`
WHERE email != '' GROUP BY email HAVING c > 1;

-- DQ-04 Validity: future date_of_birth
SELECT customer_id, date_of_birth FROM `nl.customers`
WHERE date_of_birth > CURRENT_DATE();

-- DQ-05 Integrity: orphaned accounts
SELECT a.account_id, a.customer_id FROM `nl.accounts` a
LEFT JOIN `nl.customers` c USING (customer_id)
WHERE c.customer_id IS NULL;

-- DQ-06 Consistency: non-canonical status
SELECT account_id, status FROM `nl.accounts`
WHERE status NOT IN ('active','closed','suspended');

-- DQ-07 Validity: credit_score out of range
SELECT app_id, credit_score FROM `nl.lending_applications`
WHERE SAFE_CAST(credit_score AS INT64) IS NULL
   OR SAFE_CAST(credit_score AS INT64) NOT BETWEEN 300 AND 850;

-- DQ-08 Completeness: missing annual_income
SELECT app_id FROM `nl.lending_applications`
WHERE annual_income IS NULL OR CAST(annual_income AS STRING) = '';
```

## Current results (on the generated estate)

From the latest `run_data_quality.py`:

| Rule | Dimension | Target | Failing rows | % |
|---|---|---|---|---|
| DQ-01 | Completeness | customers.email | 19 | 3.80% |
| DQ-02 | Validity | customers.email | 10 | 2.00% |
| DQ-03 | Uniqueness | customers.email | 8 | 1.60% |
| DQ-04 | Validity | customers.date_of_birth | 1 | 0.20% |
| DQ-05 | Integrity | accounts.customer_id | 15 | 1.88% |
| DQ-06 | Consistency | accounts.status | 181 | 22.62% |
| DQ-07 | Validity | lending_applications.credit_score | 8 | 1.14% |
| DQ-08 | Completeness | lending_applications.annual_income | 9 | 1.29% |

*(Counts vary if the generator seed changes. The full line-level log is in [`remediation_log.csv`](../data/remediation_log.csv).)*

## Remediation workflow

1. A failing rule raises an issue assigned to the **data steward** for that domain.
2. The steward triages: fix at source, backfill, or risk-accept with an expiry.
3. High-severity integrity/validity issues (DQ-04, DQ-05, DQ-07) block downstream use until resolved.
4. Rules run on a schedule; trends feed the governance KPIs reported to leadership.

In OpenMetadata these become **Table/Column Tests** with the same thresholds, so the catalog shows a live quality status per table — and the same signal supports control monitoring in [Project 3](../../03-grc-automation/).
