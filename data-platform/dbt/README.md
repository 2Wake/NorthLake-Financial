# dbt project — `raw` → `staging` → `marts`

dbt turns the raw daily extracts into clean, tested tables, and runs the data-quality rules. Every model is a SQL file. dbt creates it in BigQuery, applies its description and labels, then runs the tests.

## What's here

| Folder | Contents |
|---|---|
| `models/staging/` | One view per raw table (`stg_*`) giving the **current version** of each record, plus `stg_*_history` views giving **every version** with `valid_from` / `valid_to` / `is_current` |
| `models/staging/_staging.yml` | Descriptions, labels (per the Labeling Standard) and structural tests |
| `models/marts/core/` | What analysts use (`dim_*`, `fct_*`), **capped at Sensitive**: Secret columns removed; Confidential data removed, masked (card last 4, redacted comments) or generalized (zone → borough) |
| `models/marts/governance/` | `fct_dq_findings` (every failing record), `fct_dq_scorecard` (caught vs. planted per rule), `dim_dq_rules` |
| `models/marts/_marts.yml` | Marts descriptions, labels, tests, and one test per data-quality rule |
| `seeds/` | `dq_rules.csv` (the rule catalog) and `taxi_zone_supplement.csv` (zones missing from the public zone table) |
| `tests/assert_marts_classification_cap.sql` | **Governance control:** fails if any marts table is labeled above Sensitive or contains a Secret/Confidential column |
| `models/staging/_sources.yml` | The raw tables and their freshness checks (warns if the daily load stops) |
| `macros/change_log.sql` | How "current version" and "history" are worked out from the raw change logs |
| `tests/generic/` | Reusable checks: expression is true, rule has no findings |
| `profiles.yml` | Connection to BigQuery, using your Google sign-in. No passwords or keys. 1 GB cap per query. |

**Staging keeps defects as they are.** It doesn't fix bad values, so the tests can find them. Fixes happen only after the data owner or the council decides, which is the remediation story.

**History comes from `raw`, not dbt snapshots.** Raw already holds every version of every record, so history can be rebuilt at any time, back to 2026-01-01. A snapshot would only start recording from its first run.

## Commands (run from this folder)

| Task | Command |
|---|---|
| Build everything and run all tests | `dbt build` |
| Just run the tests | `dbt test` |
| See the data-quality scorecard | query `marts.fct_dq_scorecard` in the BigQuery console |
| Only the data-quality rule tests | `dbt test --select fct_dq_findings` |
| Check the daily load is up to date | `dbt source freshness` |
| Browse docs and lineage in your browser | `dbt docs generate && dbt docs serve` |

Results: **PASS** is fine, **WARN** is a data-quality finding (expected for planted defects), **ERROR** means something structural broke and needs a look.
