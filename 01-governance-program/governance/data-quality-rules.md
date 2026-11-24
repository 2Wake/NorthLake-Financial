# Empire City Taxi — Data Quality Rules

*Fictional rule catalog for the ECT portfolio. Synthetic data; real public trips.*

Data quality is measured across six dimensions: **Completeness, Validity, Uniqueness, Consistency, Integrity, Timeliness** (plus a **Privacy/DLP** check). Rules on the synthetic tables are implemented in [`run_data_quality.py`](../scripts/run_data_quality.py) (produces [`remediation_log.csv`](../data/remediation_log.csv)). Rules on the **real `trips` table** are BigQuery SQL (below) — the public NYC data is genuinely messy, so those you discover rather than seed.

## Synthetic-table rules

| Rule | Dimension | Target | Severity | Expectation |
|---|---|---|---|---|
| DQ-01 | Completeness | `riders.email` | High | Present |
| DQ-02 | Validity | `riders.email` | Medium | Valid format |
| DQ-03 | Uniqueness | `riders.email` | High | Unique |
| DQ-04 | Validity | `drivers.ssn` | High | Matches NNN-NN-NNNN |
| DQ-05 | Completeness | `drivers.tlc_license` | High | Present (required to drive) |
| DQ-06 | Consistency | `drivers.background_check_status` | Medium | ∈ {clear, pending, flagged} |
| DQ-07 | Validity | `rider_cards.card_number` | High | 16 digits (PCI — don't store raw) |
| DQ-08 | Validity | `trip_surveys.rating` | Medium | 1–5 |
| DQ-09 | Integrity | `trip_surveys.trip_id` | High | FK exists in `trips` |
| DQ-10 | Privacy (DLP) | `trip_surveys.comment` | High | No PII in free text |
| DQ-11 | Validity | `employees.salary` | Medium | > 0 |
| DQ-12 | Validity | `marketing_campaigns.end_date` | Low | ≥ start_date |
| DQ-13 | Validity | `employees.ssn` | High | Matches NNN-NN-NNNN |
| DQ-14 | Uniqueness | `employees.email` | Medium | Unique |
| DQ-15 | Completeness | `financial_ledger.account` | High | Present (every posting needs a GL account) |
| DQ-16 | Validity | `drivers.payout_bank_account` | High | 9 digits |

### Latest results (generated estate)

| Rule | Target | Failing | % |
|---|---|---|---|
| DQ-01 | riders.email (missing) | 71 | 3.55% |
| DQ-02 | riders.email (format) | 36 | 1.80% |
| DQ-03 | riders.email (dup) | 26 | 1.30% |
| DQ-04 | drivers.ssn | 13 | 4.33% |
| DQ-05 | drivers.tlc_license | 6 | 2.00% |
| DQ-06 | drivers.background_check_status | 37 | 12.33% |
| DQ-07 | rider_cards.card_number | 45 | 2.50% |
| DQ-08 | trip_surveys.rating | 64 | 2.13% |
| DQ-09 | trip_surveys.trip_id | 55 | 1.83% |
| DQ-10 | trip_surveys.comment (PII) | 79 | 2.63% |
| DQ-11 | employees.salary | 2 | 1.33% |
| DQ-12 | marketing_campaigns.end_date | 3 | 7.50% |

*(Counts shift if the generator seed changes. Line-level detail in [`remediation_log.csv`](../data/remediation_log.csv).)*

## Living platform (dbt) — rules running daily

Since 2026-11-24 the rules run on the living data platform ([`data-platform/dbt`](../../data-platform/dbt/)). Everything is in one place:

| Piece | What it does |
|---|---|
| [`seeds/dq_rules.csv`](../../data-platform/dbt/seeds/dq_rules.csv) | **The rule catalog**: rule ID, dimension, target table and column, severity, expectation, and which planted defect the rule should catch |
| `marts.fct_dq_findings` | Every failing record, one row per rule and record. Uses the data only, and holds record IDs, never the bad values |
| `marts.fct_dq_scorecard` | Per rule: findings, planted, caught, missed, unplanted findings, detection rate. **The only reader of the answer key** (`gov_planted_defects`) |
| dbt tests `dq_*`, `t*`, `ref_*` | One test per rule. A **warning** when a rule has findings (expected, since defects are planted) |
| dbt test `scorecard_every_planted_defect_caught` | **Control test on the checks:** fails the build if any planted defect goes undetected |

Three groups of rules:
- **DQ-01 to DQ-16 (planted):** defects the generator plants on purpose, scored against the answer key. DQ-13 to DQ-16 were added so every planted defect type has a rule.
- **T1 to T4 (real trip data):** defects in the real NYC TLC trips, carried over from the Project 1 SQL below. T5 (totals reconcile) was dropped because the public table lacks the congestion surcharge, and T6 became the dbt relationship tests.
- **REF-01 to REF-03 (reference data):** problems in the public taxi zone table and in trip zone codes.

### Scorecard, first run (2026-01-01 → 2026-11-23)

| Rule | Target | Findings | Planted | Caught | Missed |
|---|---|---|---|---|---|
| DQ-01 | `app_riders.email` missing | 121 | 121 | 121 | 0 |
| DQ-02 | `app_riders.email` format | 86 | 86 | 86 | 0 |
| DQ-03 | `app_riders.email` duplicate | 56 | 56 | 56 | 0 |
| DQ-04 | `fleet_drivers.ssn` format | 17 | 17 | 17 | 0 |
| DQ-05 | `fleet_drivers.tlc_license` missing | 9 | 9 | 9 | 0 |
| DQ-06 | `fleet_drivers.background_check_status` | 59 | 59 | 59 | 0 |
| DQ-07 | `payments_rider_cards.card_number` | 114 | 114 | 114 | 0 |
| DQ-08 | `app_trip_surveys.rating` | 239 | 239 | 239 | 0 |
| DQ-09 | `app_trip_surveys.trip_id` orphan | 221 | 221 | 221 | 0 |
| DQ-10 | `app_trip_surveys.comment` PII | 276 | 276 | 276 | 0 |
| DQ-11 | `hris_employees.salary` | 4 | 4 | 4 | 0 |
| DQ-12 | `app_marketing_campaigns.end_date` | 2 | 2 | 2 | 0 |
| DQ-13 | `hris_employees.ssn` format | 12 | 12 | 12 | 0 |
| DQ-14 | `hris_employees.email` duplicate | 9 | 9 | 9 | 0 |
| DQ-15 | `payments_financial_ledger.account` | 1 | 1 | 1 | 0 |
| DQ-16 | `fleet_drivers.payout_bank_account` | 11 | 11 | 11 | 0 |
| T1 | fare ≤ 0 | 2,492 | — | — | — |
| T2 | passenger count missing or outside 1–6 | 19,306 | — | — | — |
| T3 | distance ≤ 0 or > 100 miles | 5,011 | — | — | — |
| T4 | dropoff before pickup | 138 | — | — | — |
| REF-01 | duplicate zone IDs (56, 103) | 2 | — | — | — |
| REF-02 | pickup zone not in zone table | 4,993 | — | — | — |
| REF-03 | dropoff zone not in zone table | 3,879 | — | — | — |

**Detection rate 100% on every planted rule, with zero false positives.** Real-data findings (T, REF) are genuine and unplanted.

## Real `trips` table — BigQuery SQL

The public NYC TLC data has real defects. Replace `PROJECT` with your project id.

```sql
-- T1 Validity: negative or zero fares
SELECT trip_id, fare_amount FROM `PROJECT.ect.trips` WHERE fare_amount <= 0;

-- T2 Validity (range): impossible passenger counts
SELECT trip_id, passenger_count FROM `PROJECT.ect.trips`
WHERE passenger_count = 0 OR passenger_count > 6;

-- T3 Validity: zero or absurd trip distance
SELECT trip_id, trip_distance FROM `PROJECT.ect.trips`
WHERE trip_distance <= 0 OR trip_distance > 100;

-- T4 Consistency: dropoff before pickup
SELECT trip_id, pickup_datetime, dropoff_datetime FROM `PROJECT.ect.trips`
WHERE dropoff_datetime < pickup_datetime;

-- T5 Integrity: total doesn't reconcile with components (allow small rounding)
SELECT trip_id, total_amount, fare_amount, tip_amount, tolls_amount
FROM `PROJECT.ect.trips`
WHERE ABS(total_amount - (fare_amount + tip_amount + tolls_amount)) > 5;

-- T6 Integrity: trips referencing a driver/rider outside the valid range
SELECT trip_id FROM `PROJECT.ect.trips`
WHERE driver_id NOT BETWEEN 1 AND 300 OR rider_id NOT BETWEEN 1 AND 2000;
```

You won't know the counts until you run them — that's the point. Profile the table in OpenMetadata first, note what looks off, then write the rule.

## Remediation workflow

1. A failing rule raises an issue assigned to the **data steward** for that domain.
2. The steward triages: fix at source, backfill, or risk-accept with an expiry.
3. High-severity integrity/validity/DLP issues block downstream use until resolved. The DLP finding (DQ-10) also triggers reclassification of the column to Confidential.
4. Rules run on a schedule; trends feed the governance KPIs reported to leadership.

In OpenMetadata these become **Table/Column Tests** with the same thresholds, so the catalog shows a live quality status per table — and the same signal supports control monitoring in [Project 3](../../03-grc-automation/).
