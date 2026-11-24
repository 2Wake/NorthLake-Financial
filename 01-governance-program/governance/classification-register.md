# Empire City Taxi — Column Classification Register

*Fictional governance process for the ECT portfolio. Status: **DRAFT v0.1**, pending council approval.*

Every column in the warehouse (`raw`, `staging`, `marts`) has a classification under the
[Data Classification Standard](data-classification-standard.md). This document explains where
that information lives, who maintains it, and how it is checked.

## Where classifications live

| Record | File | Purpose |
|---|---|---|
| **Classification register** (operational) | [`data-platform/dbt/seeds/governance/column_classification_register.csv`](../../data-platform/dbt/seeds/governance/column_classification_register.csv) | The single source of truth: one row per column per layer, with classification, data category, treatment, owner, steward and approval. Loaded into BigQuery as `staging.column_classification_register`. |
| **Answer key** | [`column_classification_answer_key.csv`](../../data-platform/dbt/seeds/governance/column_classification_answer_key.csv) | The correct classification of every column. Used **only** to score the register; checks never read it. |
| Table labels | Loader (`raw`) and dbt YAML (`staging`, `marts`) | Table-level `classification`, `data_owner`, `data_steward`. Must agree with the register (check CLS-04). |

The Project 1 [`column-classification-map.csv`](column-classification-map.csv) is **superseded**. It
remains as a Project 1 artifact and seeded the answer key.

### Register columns

`layer, table_name, column_name, classification, data_category, treatment, data_owner, data_steward, status, proposed_by, approved_by, approved_on, rationale`

- **treatment** shows how a value got into its layer: `source` (raw), `inherited` (staging copies raw), `seed`, or in marts `passthrough`, `masked`, `generalized`, `aggregated` or `derived`.
- **status** is `approved` only after the data owner signs off.

## How it is maintained (federated model)

| Step | Who | How |
|---|---|---|
| Propose a classification or change | **Data steward** of the domain | Pull request editing the register. `status: proposed`, `proposed_by` = steward role. |
| Approve | **Data owner** | Reviews and approves the pull request. Sets `status: approved`, `approved_by`, `approved_on`. |
| Consult | CISO, Privacy Officer | Required reviewers for any Secret or Confidential change |
| Maintain the standard, register format and checks | **Data Governance Manager** (hub) | Owns this document, the checks and the scorecard |
| Disputes | **Data Governance Council** | Per the [council charter](data-governance-council-charter.md) RACI ("Disputed classification") |

The pull request history is the audit trail of every classification decision.

## Automated checks (`marts.fct_classification_findings`, every daily run)

| Rule | Check |
|---|---|
| CLS-01 | Every column in BigQuery has a register entry (coverage) |
| CLS-02 | Every register entry points to a column that exists |
| CLS-03 | Every entry is approved by the data owner |
| CLS-04 | Each table's classification label equals its highest column classification |
| CLS-05 | Columns copied from raw into staging keep the same classification (lineage) |
| CLS-06 | Nothing in `marts` is above Sensitive |
| CLS-07 | The register's steward matches the table's `data_steward` label |
| CLS-08 | Classification is one of the five tiers, spelled exactly |

`marts.fct_classification_scorecard` compares the register with the answer key: correct,
under-classified, over-classified, missing or invalid, and which check (if any) caught it. It
feeds council KPI #2 ("Secret and Confidential columns correctly classified").

## Planted scenarios

The register deliberately contains realistic mistakes, so the checks and the council process
can be demonstrated. Each one reflects how classification goes wrong in practice.

| ID | Scenario | Register rows | Why it happens | Caught by |
|---|---|---|---|---|
| S01 | **Precise location tagged Internal** (council issue **GOV-003**) | `app_trips` / `stg_app_trips` pickup and dropoff location: Internal (should be Confidential) | Zone IDs look like harmless codes; combined with `rider_id` they reveal a person's movements | CLS-04 |
| S02 | **PII in free text missed** | `app_trip_surveys` / `stg_` comment: Internal (should be Confidential) | "It's just feedback" — but riders type phone numbers and emails | CLS-04 |
| S03 | **Cardholder data partly classified** | `payments_rider_cards` card_expiry: Confidential, cardholder_name: Sensitive (both should be Secret) | Only the card number is treated as PCI; expiry and name are forgotten | CLS-05 |
| S04 | **Regulated identifier under-classified** | `fleet_drivers.tlc_license`: Internal (should be Confidential) in raw only | Licence numbers seem public | CLS-05 |
| S05 | **HR performance data under-classified everywhere** | `performance_rating`: Internal in raw and both staging views (should be Confidential) | Consistent mistake by one steward | **None — a blind spot.** Needs a steward review or content-based scan |
| S06 | **Lineage drift** | `stg_fleet_drivers.ssn`: Confidential; `stg_hris_employees_history.salary`: Sensitive | Classification retyped in a new layer instead of inherited | CLS-05 |
| S07 | **Over-classification blocking analytics** | `fct_daily_zone_trips` zone ID and name: Confidential (should be Internal) | Security applies the raw rule to aggregated data | CLS-04, CLS-06 |
| S08 | **Masked value over-classified** | `dim_rider_cards.card_last4`: Secret (should be Sensitive) | Masking not recognized | CLS-04, CLS-06 |
| S09 | **New columns never classified** | 8 columns added by the HR, fleet and dispatch systems, with no register entry | Schema changes ship without a classification review | CLS-01 |
| S10 | **Approval backlog** | 3 marts columns `proposed`, not approved | Owners slow to review | CLS-03 |
| S11 | **Wrong steward recorded** | `payments_rider_cards` rows list the Rider steward, not Finance | Rider vs. Finance ownership of card data unclear | CLS-07 |
| S12 | **Retired tier name** | Ledger `amount`: "Restricted" / "restricted" | The pre-2026-11-23 four-tier scheme still in use | CLS-08 |

**First run (2026-11-24):** 27 of 508 columns wrong or missing. 24 were flagged by a check; the 3 not
flagged are all S05. High-risk (Secret and Confidential) columns correctly classified: **72.5%**
(37 of 51) against a target of 100%.
