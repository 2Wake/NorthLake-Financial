# Empire City Taxi GRC — Work Log

Running log of all work, decisions and open items. It's the source for progress summaries and status updates. Newest entries at the top. Updated after every meaningful step (see [`CLAUDE.md`](CLAUDE.md)).

---

## 📋 Backlog

- [x] **Phase 0: generator framework.** Built, tested, and backfilled into `raw` (2026-01-01 → 2026-11-23).
- [ ] **Reference-data issue:** raise REF-01 to REF-03 as a governance issue (reference domain owner: Data Governance Manager) in the issue register.
- [ ] **Column classification map:** add the new raw table names and columns (e.g. `fleet_drivers.employee_id`, `driver_status`, `hris_employees.pay_type`), then drive the marts classification-cap test from the map instead of its column-name list.
- [ ] **Table and column descriptions.** Raw-table schema files, plus dbt `.yml` with `persist_docs`. Leave about 10–15% blank on purpose, tracked in a documentation-gap register, and fill them in a later remediation sprint.
- [ ] **Labels on tables:** applied in code on `raw`, `staging` and `marts`. **Remaining:** planted label gaps, tracked in the gap register.
- [ ] **Council operations.** Issue register (`GOV-###`) and decision log (`GOV-D-###`) as dbt seeds; minutes in `governance/council/minutes/`.
- [ ] **Phases 1–4 tables** (see the 2026-11-23 design review entry below).
- [ ] **GitHub Actions daily refresh:** workflow built. **Remaining:** the user does the console setup (`data-platform/docs/github-actions-setup.md`), then a test run. Until then, run by hand: `uv run ect-daily`, then `dbt build`.
- [ ] **DQ rule ownership:** add `proposed_by` (steward), `approved_by` (owner) and `approval_status` to `dq_rules.csv`. The 23 current rules are hub-drafted proposals awaiting steward and owner sign-off.
- [ ] **Council roles and responsibilities (federated model):** flesh out each council member's duties, decision rights and time commitment; hub vs. domain (spoke) responsibilities; steward duties including DQ rule authoring.
- [ ] **Collate:** sign up, connect to BigQuery read-only, evaluate its AI settings.
- [ ] **Knowledge Catalog:** free-tier discovery and glossary only; compare it with Collate.
- [ ] **Clean up merged branches** on GitHub (`five-tier-classification`, `governance-council`). The user asked to keep them for now.

---

## 2026-11-24 — Daily run (GitHub Actions); DQ rule ownership; federated model

### Done
- Merged `marts` to `main` from the CLI at the user's request (`8accce2`).
- **`uv run ect-daily`:** finds the newest loaded day (`MAX(_batch_date)` of `raw.app_trips`, ~3 MB read), then generates and loads every missing day through yesterday. A failed or skipped run is caught up the next day. Tested with a dry run: last loaded 2026-11-23, 0 days due.
- **`uv run ect-record`:** writes `data-platform/run-records/<date>.md` with the days loaded, row counts per table, and the dbt results (every warning or failure with its failing-record count). Counts and test names only, never data values.
- **Workflow** `.github/workflows/daily-refresh.yml`:
  - Runs daily at 10:30 UTC (5:30 am New York), plus a manual "Run workflow" button.
  - Steps: keyless Google sign-in → install → generator tests → `ect-daily` → `dbt build` → run record → commit.
- **Setup guide** `data-platform/docs/github-actions-setup.md`: console steps A–G for the user (APIs, service account, dataset access, Workload Identity pool and provider, impersonation grant, GitHub variables, test run).
- Read-only check: the IAM, IAM Credentials and Security Token Service APIs are **not enabled** yet. That's step A.

### Decisions
- **DQ rule ownership (the user's point):** data quality rules should be **written by data stewards, with the data owner's approval**, because they are closest to the data and its use. The 23 rules in `dq_rules.csv` are **drafts proposed by the governance hub**, pending each domain's sign-off. The hub owns the framework (catalog, findings, scorecard, controls); the domains own the rule content.
- **Leaning toward a federated (hub-and-spoke) governance model** over a centralized one. The hub (Data Governance Manager) sets standards, tooling, the scorecard and reporting. Domain owners and stewards (the spokes) make and enforce decisions for their data. Roles and responsibilities to be fleshed out (backlog).
- **Keyless sign-in** (Workload Identity Federation): restricted to this repository by an attribute condition; one service account, `ect-pipeline`.
- **Least privilege:** BigQuery Job User (project) plus BigQuery Data Editor on `raw`, `staging` and `marts` only. No service-account key is ever created.
- **Catch-up design:** the pipeline works out what's missing from BigQuery itself rather than trusting the schedule, so missed days heal themselves.
- **Run records are committed to the repo:** audit evidence for each run (Project 3 control monitoring), and the commits keep GitHub from pausing the schedule after 60 days of inactivity. **Open question:** commit them straight to `main`, which needs the user's OK, or to a separate branch.

### Next steps
1. The user decides where the bot commits run records.
2. The user does console steps A–G, then clicks **Run workflow**.

---

## 2026-11-24 — Marts, rule catalog and data-quality scorecard

### Done
- Merged `dbt-project` to `main` from the CLI at the user's request (`e412f30`).
- **Answered the user's questions:**
  - *Where are the reference rules?* Before this step there was only REF-01, a staging test. Now **all rules live in one catalog** (`seeds/dq_rules.csv`, 23 rules): DQ-01 to DQ-16 (planted), T1 to T4 (real trip data), REF-01 to REF-03 (reference data).
  - *How is `gov_planted_defects` used?* As the **answer key** for scoring the checks. `fct_dq_scorecard` compares the findings with it per record.
- **Rule logic in one place:** `marts.fct_dq_findings` lists every failing record (rule, table, record ID, column; never values). One dbt test per rule warns when there are findings. The old per-column DQ tests in staging were removed.
- **Scorecard** `marts.fct_dq_scorecard`: **100% detection on all 16 planted rules and 0 false positives**, scored record by record. Real-data findings: T1 2,492, T2 19,306, T3 5,011, T4 138, REF-01 2, REF-02 4,993, REF-03 3,879.
- **Two governance controls run on every build:**
  - `scorecard_every_planted_defect_caught` (error if a rule misses any planted defect);
  - `assert_marts_classification_cap` (error if a marts table is labeled above Sensitive, or has a Secret/Confidential column). **Both pass.**
- **14 marts tables** in `marts`, all labeled (layer `marts`, classification sensitive / internal / public):
  - Dimensions: `dim_employees`, `dim_drivers`, `dim_riders`, `dim_rider_cards`, `dim_taxi_zones`, `dim_campaigns`, `dim_rider_segments`, `dim_dq_rules`.
  - Facts: `fct_trips` (357k, partitioned by pickup date, clustered by driver), `fct_daily_zone_trips` (24.6k), `fct_trip_surveys`, `fct_ledger_entries`, `fct_dq_findings` (37.1k), `fct_dq_scorecard`.
- Full build: **114 nodes; 91 pass, 23 warn (the rules), 0 errors.** The heaviest query processed 75 MB.

### Decisions
- **How the Sensitive cap is applied in marts:**
  - **Removed:** SSN, bank account, card number, expiry and cardholder (Secret); salary, rating, contact details, licence, background check (Confidential).
  - **Masked:** card number → last 4 digits; survey comment → phone numbers and emails `[REDACTED]`.
  - **Generalized:** in `fct_trips`, pickup and dropoff zone → **borough**, because zone plus rider_id would reveal a person's movements. Zone-level demand is in `fct_daily_zone_trips`, aggregated with no rider or driver IDs.
- **`dim_rider_cards` is out of PCI scope** (last 4 digits only), so it's labeled `pci_scope: false`.
- **Reference data is corrected in marts, not staging.** `dim_taxi_zones` collapses duplicate IDs and adds zones 57, 104, 105, 264 and 265 from a documented supplement seed (`zone_source` shows which). Staging keeps the public data as published, so REF-01 stays visible.
- **Duplicate rules flag only the later copies** (by ID order), not the first holder of a value. That matches how the defect arises.
- **T5 dropped** (total ≠ components): the public table lacks the congestion surcharge, so it would flag almost every trip. T6 (bad driver/rider IDs) is now covered by the relationship tests.
- Marts are full-rebuild tables for now (small data). Switch `fct_trips` to incremental if build cost grows.

### Next steps
- GitHub Actions daily run (generate → load → `dbt build`), which needs a Workload Identity setup by the user in the console.
- Looker Studio: a DQ scorecard and trips dashboard on `marts`.

---

## 2026-11-24 — dbt project: staging layer and data-quality tests

### Done
- Merged `bulk-backfill` to `main` from the CLI at the user's request (`7c4b94e`).
- Built **`data-platform/dbt/`** (dbt 1.12, BigQuery). It uses the user's Google sign-in with no keys, a 1 GB cap per query, and job labels for cost tracing.
  - **16 staging views** in `staging`:
    - a current-version view (`stg_*`) for each raw table;
    - full-history views (`stg_*_history`, with `valid_from`, `valid_to`, `is_current`) for employees, drivers, riders, cards and segments;
    - trips, surveys, ledger, taxi zones, and the answer key.
  - Each view carries its description and **10 labels** (layer `staging`).
  - **Tests:**
    - 42 structural tests (unique IDs, plus links between tables: trips→drivers, drivers→HR, cards→riders, campaigns→segments). **All pass.**
    - The **16 data-quality rules DQ-01 to DQ-16**, as warnings. DQ-13 to DQ-16 are new, so every planted defect type has a rule.
  - **Freshness checks** on the daily-changing raw tables (warn after 2 days without a load, error after 4).
- **First scorecard:** every rule catches exactly the number planted, with no false positives. Uniqueness and allowed-values rules count distinct values rather than rows. The table is in `data-quality-rules.md`.
- **Verified history:** 647 employees and 470 drivers, each with exactly one current version. DRV10200 shows active → suspended → reinstated → inactive.

### Decisions
- **Revised:** history comes from **`raw` change logs** through dbt views, **not dbt snapshots**. Raw already stores every version, so history covers 2026-01-01 onward and can be rebuilt. Snapshots would only start recording from their first run and couldn't be rebuilt. Snapshots stay available for sources that aren't change logs.
- **Staging keeps defects as they are:** no clean-up, so the tests can find problems. Fixes happen only after an owner or council decision, which makes the remediation demo.
- **Data-quality rules are warnings, not failures.** Structural tests are errors.
- **dbt writes only to existing datasets** (`staging`, later `marts`). A schema-name macro stops dbt from creating new datasets.
- Staging is views, not tables: no storage cost, and always up to date with `raw`.

### Real-data findings (not planted)
- **REF-01:** the public taxi zone table has duplicate IDs. Zone 57 (Corona) is filed under 56, and 104/105 (the harbor islands) under 103. This explains why zone 57 trips have no match.

### Next steps
- Marts (`dim_*`, `fct_*`, capped at Sensitive) and a per-record DQ scorecard; or the GitHub Actions daily run.

---

## 2026-11-24 — Backfill loaded into BigQuery `raw`

### Done
- Merged `tlc-december-fix` to `main` from the CLI at the user's request (`5088859`).
- Added **bulk backfill** to the loader (`--bulk`): one load job per table for a whole date range, instead of one job per table per day (~2,300 jobs). It refuses to run if any of those days is already loaded, and it checks row counts.
- **Loaded 2026-01-01 → 2026-11-23** in about 1.5 minutes (loads are free). All 10 tables were created with their descriptions and 10 labels each, partitioned by `_batch_date`:

  | Table | Rows |
  |---|---|
  | `app_trips` | 357,049 (91 MB) |
  | `app_trip_surveys` | 10,908 |
  | `app_riders` | 4,645 |
  | `payments_rider_cards` | 3,894 |
  | `gov_planted_defects` | 1,237 |
  | `hris_employees` | 954 |
  | `fleet_drivers` | 783 |
  | `payments_financial_ledger` | 204 |
  | `app_rider_segments` | 132 |
  | `app_marketing_campaigns` | 62 |

- **Verified:**
  - Every row count matches the generator's manifests.
  - All 12 `raw` tables carry 10 labels.
  - **Re-loading 2026-11-23 left it at 1,090 trips**, so re-runs replace rather than duplicate.
  - Trip IDs are unique.

### Real-data findings (not planted)
- **5,000 trips have pickup zones that aren't in the zone reference table:** 264 "Unknown" (4,199), 265 "Outside NYC" (792), and zone 57 (2). That's a genuine reference-data gap, good material for a referential-integrity check and a reference-data issue.

### Risks / watch items
- Storage usage per table (`INFORMATION_SCHEMA.TABLE_STORAGE`) needs an extra permission the user's account doesn't have. Table details in the console show the sizes anyway.

### Next steps
- Suggested order: (1) dbt project (staging models and snapshots over `raw`), (2) GitHub Actions daily run, (3) column descriptions and the gap register, (4) Phase 1 tables.

---

## 2026-11-24 — TLC setup run; December gap fixed; backfill generated

### Done
- **The user ran `sql/01` and `sql/02` in the BigQuery console.** Verified read-only:
  - `raw.tlc_yellow_trips_sample`: **362,834 trips**, 76 MB, partitioned by day, 10 labels, no duplicate keys.
  - `raw.tlc_taxi_zones`: 263 zones, 10 labels.
- **Found:** the public 2022 table stops on **2022-11-30** (no December). **Fixed:** simulated dates that land in December now replay the trips from 5 weeks earlier, on the same weekday. The test now checks every day for two years.
- **Generated the backfill locally:** 2026-01-01 → 2026-11-23 (327 days). It contains 357,049 trips, 10,908 surveys, 4,645 rider records, 3,894 card records, 954 HR records, 783 fleet records, and 1,237 planted defects. Nothing is loaded yet.
- Checked a spurious alarm: every `tlc_sample_key` ends in "00". That is expected, because the 1% sample keeps only trips whose hash is divisible by 100.

### Real-data findings (not planted; future data-quality material)
- **2022-09-18 has only 36 trips** (normal is ~1,100), an apparent gap in the public data. It is replayed as **2026-09-13**, which makes a good test for a volume anomaly check.
- **2022-01-29 is low (339)** because of the real blizzard. That's a true dip, not an error.

### Next steps
- The user approves the backfill load into `raw` (loads are free).

---

## 2026-11-24 — Phase 0: daily data generator and loader

### Done
- Merged `project-context` (CLAUDE.md, public WORKLOG) to `main` from the CLI at the user's request (`fc55a41`).
- Built **`data-platform/`**: a Python package (uv, Python 3.12, Faker 37) with a generator, a loader, one-time SQL and tests.
  - **Generator** (`uv run ect-generate`): replays company life from **2026-01-01** day by day, and writes each day's new and changed records to `output/<date>/*.jsonl` with a manifest (row counts, SHA-256).
  - **Lifecycle:** hires and terminations; driver onboarding → background check → active; suspensions and reinstatements; a March 1 annual review; rider sign-ups, profile changes and closures; cards added and removed; new campaigns; monthly segment refresh; ledger postings on the 3rd.
  - **Drivers are now employees**, so every `DRV` has an `EMP` in HR. That is the foundation for GOV-004 (terminated in HR, still active in fleet), which gets planted in Phase 3.
  - **Trips:** about 1,000 real 2022 NYC yellow-taxi trips a day, replayed on the same weekday (52-week cycle). Synthetic drivers are assigned; riders only on app-booked card trips, while street hails have no rider. Surveys go on about 6% of app trips.
  - **Planted defects:** the 16 Project 1 defect types carry over. Every one is logged in the answer key `gov_planted_defects` (record and column only, never the bad value). The epoch batch plants 292.
  - **Loader** (`uv run ect-load`): creates each `raw` table on first load with its schema, description and labels. Tables are partitioned by `_batch_date`, and each day replaces only its own partition, so history is append-only and re-runs can't duplicate.
  - **One-time SQL** (validated with dry runs; **not run yet**): `sql/01` copies a fixed 1% sample of 2022 TLC trips (~6.8 GB scan, ~360k rows), and `sql/02` copies the 263 taxi zones (~2 MB).
  - **Tests:** 9 passing. They cover same date → identical data, byte-identical files, weekday-aligned TLC mapping, prefixed IDs, trips only to active drivers, schema and label coverage, Luhn-valid cards, and an answer key with no values.
- Checked the simulated state on 2026-11-23: 331 active drivers, 494 active employees, 3,714 active riders, 3,385 active cards, 0 HR/fleet mismatches.

### Decisions
- **2023 TLC data is not usable.** The public 2023 table is empty, so 2022 is replayed in a 52-week cycle that keeps weekdays aligned. Trips repeat yearly, but driver and rider assignments differ.
- **Replay-from-start design:** state on any date is rebuilt from 2026-01-01 (under 1 second for a year), so no state files need storing. The trade-off is that changing generator code changes history; `_generator_version` on every row traces which code made it.
- **Incremental extracts:** raw holds full record images each time a record changes, not just events. That is the standard input for dbt snapshots.
- **Code lives in `data-platform/`** at the repo root, because it serves all four projects. The Project 1 generator and CSVs stay as they are, as Project 1 artifacts.
- **The answer key goes in the warehouse** (`raw.gov_planted_defects`), so a data-quality scorecard (caught vs. planted) can run in SQL. Checks must not read it.
- **Safe synthetic values:** 555 phone numbers, reserved email domains, a test-style `4000 00` card prefix. Card numbers are Luhn-valid, so Google Sensitive Data Protection will recognise them.
- Labels are applied when the loader creates each raw table (part of the "labels on tables" backlog item). Planted label gaps are still to come.

### Risks / watch items
- `trip_distance`, fares and other TLC values pass through untouched, including the real data's errors. That is intended.
- The epoch batch is about 4,900 records; later days are a few dozen records plus about 1,000 trips.

- Committed as `629742a` on branch `phase-0-generator`; **merged to `main` from the CLI** at the user's request.
- The user chose to **run the one-time SQL themselves in the BigQuery console**.

### Next steps
1. The user runs `sql/01` and `sql/02` in the BigQuery console (one-time; ~6.8 GB scanned).
2. Backfill: `ect-generate --backfill`, then `ect-load` for 2026-01-01 → yesterday.
3. Check the tables in the BigQuery console.

---

## 2026-11-23 — Governance org and council charter; repo housekeeping

### Done
- **Org structure** (`01-governance-program/governance/governance-org-structure.md`): reporting lines, fictional named role holders, owners and stewards per domain, custodian and consumer roles, and the department objectives that create governance tensions.
- **Council charter** (`01-governance-program/governance/data-governance-council-charter.md`): purpose, authority, membership and voting, meetings and quorum, decision rules, issue lifecycle with severity targets, escalation path, a RACI for 12 decision types, standing agenda, 7 KPIs, and the initial backlog GOV-001 to GOV-006, each tied to a defect planted in the data.
- Committed as `245c3e7` on branch `governance-council`; **merged to `main` from the CLI** at the user's request.
- Added `CLAUDE.md` (project context and working agreements) and moved this log into the repo as `WORKLOG.md`. The user chose to keep the log **public**. Committed as `8fe21bb` on branch `project-context`; **merged to `main` from the CLI** at the user's request.

### Decisions
- Council members get **fictional names**. Names appear in docs and minutes only; labels and data use role slugs.
- **The CDO (Renée Okonkwo) is the final escalation point**, as leader of the data organization. Vetoes and deadlocks go to the CDO, and the CEO receives a quarterly governance report.
- The **CISO and Privacy Officer keep their vetoes**. The Privacy Officer reports to General Counsel, which keeps privacy independent of the CDO.

---

## 2026-11-23 — Classification, labels, dataset layout

### Done
- **Label standard** (`01-governance-program/governance/labeling-standard.md`, v0.1): label keys for datasets and tables, a domain register, formatting rules, a planned automated compliance check, and deliberate label gaps.
- **Dataset labels** applied by the user in the console (`layer`, `classification`, `data_custodian`, `environment`, `managed_by`) and confirmed with a read-only check.
- **Datasets** `raw`, `staging` and `marts` created by the user (US location, no table expiry), with descriptions. Ownership is carried by labels, not descriptions.
- Committed as `f403b0f` (branch `five-tier-classification`) and **merged to `main`** with the user's approval.

### Decisions
- **Five-tier classification: Secret → Confidential → Sensitive → Internal → Public**, replacing Restricted → Confidential → Internal → Public. The user chose "Internal" over "Restricted" for tier 4, because "Restricted" usually signals a high tier. **SSN = Secret.**
  - **Secret:** SSN, cardholder data (card number, expiry, name), payout bank account, credentials.
  - **Confidential:** contact PII, TLC license, background check, salary, performance rating, pickup/dropoff locations, free-text comments.
  - **Sensitive:** names, employee work email, fares/tips/totals, ledger amounts, budgets.
  - Column map: 6 Secret, 12 Confidential, 12 Sensitive, 38 Internal, 1 Public.
  - Handling: Secret never goes to non-prod or `marts`. Confidential is masked or aggregated in `marts`. **`marts` is capped at Sensitive.**
  - Applied across 15 files. The vendor-risk tool keeps its 1–4 scoring, with the option labels updated.
  - Also fixed a glossary CSV bug: unquoted commas would have broken the catalog import.
- **Dataset layout: by layer** (`raw` / `staging` / `marts`). The domain is carried by labels. Raw tables get a source-system prefix (`hris_`, `fleet_`, `payments_`, `app_`, `tlc_`). dbt names its tables `stg_*` in staging and `dim_*`/`fct_*` in marts. Access control is set per layer (analysts get `marts` only).
- **Prefixed IDs** (`DRV10042`, `EMP10001`, `RDR…`, `VEH…`) replace integer IDs.

### Design review of the ChatGPT notes (tables, lifecycle, org, council)
- Adopted: department conflicts and the governance council; lifecycle data (hires, terminations, reassignments, no physical deletes); staged rollout; taxi data treated as one source system among several.
- Adjusted:
  - **`raw` is append-only.** History tables come from **dbt snapshots**, not UPDATEs to BigQuery.
  - **The daily generator is deterministic code** run by GitHub Actions, not Claude-in-the-loop. Claude/MCP write access is a gated Project 4 item.
  - **Governance records are repo files loaded as dbt seeds.**
  - **Real TLC taxi zones** are used for locations.
  - **Project 2's control matrix** is reused as `compliance_controls`.
- **Rule:** every conflict scenario is backed by a defect planted in the data.
- **Phased table plan:**

  | Phase | Scope |
  |---|---|
  | 0 | Framework and the existing tables |
  | 1 | `vehicles`, `vehicle_assignments`, `payment_transactions`, `driver_payouts`, org seeds |
  | 2 | `rider_consent`, `support_tickets`, `privacy_requests`, `data_access_logs` |
  | 3 | Council scenarios |
  | 4 | Clickstream (nested `app_events`) |

---

## 2026-11-23 — Tools, sign-ins, Google Cloud guardrails

### Done
- Installed:
  - Homebrew (by the user)
  - gh 2.105.0
  - uv 0.13.9 and Python 3.12
  - Google Cloud CLI 594.0.1
  - dbt-core 1.12.7 with dbt-bigquery 1.12.4
- Signed in to GitHub CLI (`2Wake`), gcloud, and application-default credentials.
- Fixed `command not found: gh`: added Homebrew's setup line to `~/.zshrc`.
- Cloned the repo to `~/empire-city-taxi-grc`. The repo's git identity uses the GitHub noreply email, so no personal email appears in commits.
- Google Cloud project **`empire-city-taxi`** (billing enabled) set as the default.
- **Cost guardrails:**
  - Budget **"ECT free-tier guardrail"**: $5/month, alerts at 5¢, $1, $2.50 and $5 actual, plus a forecast alert. Created by Claude through the CLI, before the UI-only agreement.
  - **BigQuery "Query usage per day" quota set to 0.03 TiB (~30 GB)** by the user in the console. This hard cap keeps a month of queries under the 1 TB free tier.
  - `maximum_bytes_billed` per query (in dbt) and date-partitioned tables are still to come.

### Working agreements established
- The user makes all cloud and account configuration changes **in the web UI**. Claude provides the steps and changes no settings without explicit approval.
- Commits go on a branch. **Claude always asks before merging anything.**
- Every step is logged here.

---

## 2026-11-23 — Migrated from Claude Chat to Claude Code; stack decided

### Done
- Brought the Claude Chat build log (Projects 1 and 2 complete, Projects 3 and 4 planned) into Claude Code.
- Connected the GitHub MCP. It's read-only, so writes go through `gh`.
- Checked the laptop: 8 GB RAM, which rules out running OpenMetadata, Airflow and Metabase locally.

### Decisions

| Area | Decision | Rationale |
|---|---|---|
| Warehouse | **BigQuery with billing on** (not the sandbox) | Removes the sandbox's 60-day table expiry. About 2–3 GB/yr expected, against 10 GB of free storage. |
| Cost control | Daily query quota, per-query byte limit, budget alerts, partitioning | The quota and per-query limits block spending; alerts only warn. |
| Catalog / governance | **Collate free tier** (hosted OpenMetadata) | Uses no laptop RAM. |
| Orchestration | **GitHub Actions** daily, keyless login through Workload Identity Federation | Free, runs off the laptop. Cloud Composer costs hundreds of dollars a month. Each run's committed record doubles as control evidence. |
| Transform / DQ | **dbt Core**; the full DQ rule set runs daily in dbt | Free within the BigQuery free tier. Collate's free tier allows only 10 tests. |
| PII detection | Google Sensitive Data Protection (sampled one-off jobs) plus manual tags checked against the answer key | Collate's PII auto-classification is paid only. SDP's first 1 GB/month is free. |
| Reporting | Looker Studio | Free, in the cloud. |
| Avoid | Cloud Composer, Cloud SQL, scheduled Dataplex DQ scans | Cost. Dataplex DQ isn't in the free tier or covered by the BigQuery quota. |

### Risks / watch items
- **Collate's free tier is reclaimed after 4 weeks without a login.** Log in every couple of weeks, and keep the governance artifacts in the repo as the backup.
- Collate free-tier limits: 5 users, 500 assets, weekly refresh and tests, 10 test cases, 5 alerts.
- Collate's AI behavior is undocumented (on by default? auto-applied? which LLM?). Evaluate it after sign-up; possible Project 4 material.
- GitHub pauses scheduled workflows in public repos after 60 days without activity. The daily run-record commit keeps the repo active.
- Collate reads BigQuery through a read-only service-account key. Record it in the vendor-risk tool.
