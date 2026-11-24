# dbt project — `raw` → `staging` (→ `marts` next)

dbt turns the raw daily extracts into clean, tested tables, and runs the data-quality rules. Every model is a SQL file. dbt creates it in BigQuery, applies its description and labels, then runs the tests.

## What's here

| Folder | Contents |
|---|---|
| `models/staging/` | One view per raw table (`stg_*`) giving the **current version** of each record, plus `stg_*_history` views giving **every version** with `valid_from` / `valid_to` / `is_current` |
| `models/staging/_staging.yml` | Descriptions, labels (per the Labeling Standard) and tests, including the data-quality rules DQ-01 to DQ-16 |
| `models/staging/_sources.yml` | The raw tables and their freshness checks (warns if the daily load stops) |
| `macros/change_log.sql` | How "current version" and "history" are worked out from the raw change logs |
| `tests/generic/` | Reusable checks: pattern match, expression is true, no contact details in free text |
| `profiles.yml` | Connection to BigQuery, using your Google sign-in. No passwords or keys. 1 GB cap per query. |

**Staging keeps defects as they are.** It doesn't fix bad values, so the tests can find them. Fixes happen only after the data owner or the council decides, which is the remediation story.

**History comes from `raw`, not dbt snapshots.** Raw already holds every version of every record, so history can be rebuilt at any time, back to 2026-01-01. A snapshot would only start recording from its first run.

## Commands (run from this folder)

| Task | Command |
|---|---|
| Build everything and run all tests | `dbt build` |
| Just run the tests | `dbt test` |
| Only the data-quality rules | `dbt test --select "test_name:dq_*"` |
| Check the daily load is up to date | `dbt source freshness` |
| Browse docs and lineage in your browser | `dbt docs generate && dbt docs serve` |

Results: **PASS** is fine, **WARN** is a data-quality finding (expected for planted defects), **ERROR** means something structural broke and needs a look.
