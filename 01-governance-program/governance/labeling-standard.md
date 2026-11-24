# Empire City Taxi — Data Labeling Standard

*Fictional standard for the ECT portfolio. Synthetic. Status: **DRAFT v0.1**, pending review.*

## Purpose

Labels are key–value tags attached to BigQuery **datasets** and **tables**. ECT uses them to record, on the data itself, **which business domain it belongs to, who is accountable for it, how sensitive it is, and where it came from.**

Labels make governance **queryable**. A single query against BigQuery's metadata can answer "which tables hold PII but have no named steward?" Labels also carry into the catalog (Collate), billing reports and dashboards. Because ECT organizes datasets **by processing layer** (`raw` → `staging` → `marts`) rather than by domain, labels are the **primary way to tell which domain a table belongs to.**

This standard implements the [Data Classification Standard](data-classification-standard.md) and the [Data Ownership Model](data-ownership-model.md) at the table level.

## Scope

| Object | Labeled? | How |
|---|---|---|
| Datasets (`raw`, `staging`, `marts`) | ✅ | Set in the BigQuery console by the platform owner |
| Tables and views | ✅ | Set **in code**: the loader for `raw`; dbt `labels` config for `staging` and `marts` |
| Columns | ❌ BigQuery has no column labels | Column classification lives in [`column-classification-map.csv`](column-classification-map.csv), dbt `meta`, and catalog tags. BigQuery **policy tags** (column-level access control) are a future control. |
| Query jobs | ✅ | dbt and the pipeline label their queries (e.g. `pipeline: daily-refresh`) for cost attribution |

## Label keys

### Required on every table

| Key | Meaning | Allowed values |
|---|---|---|
| `domain` | Business domain that owns the data | See [Domain register](#domain-register) |
| `layer` | Processing layer | `raw`, `staging`, `marts` |
| `data_owner` | **Role** accountable for the data (approves access and classification, accepts risk) | Role slug from the domain register, e.g. `vp-driver-operations` |
| `data_steward` | **Role** responsible day to day (definitions, quality, glossary) | Role slug, e.g. `driver-data-steward` |
| `classification` | **Highest** classification of any column in the table | `secret`, `confidential`, `sensitive`, `internal`, `public` |
| `source_system` | System the data originates from | `hris`, `fleet`, `payments`, `app`, `tlc`, `governance`, `reference`, `derived` (built from more than one system) |
| `data_origin` | Integrity marker: real or synthetic | `synthetic`, `public` (real NYC TLC open data) |

### Required when applicable

| Key | When | Values |
|---|---|---|
| `contains_pii` | Any column holds personal data about a rider, driver, or employee | `true` / `false` (always set it on tables in `raw` and `staging`) |
| `pci_scope` | Any column holds cardholder data (card number, expiry, cardholder name) | `true` / `false` |
| `retention` | A retention period applies | `1y`, `3y`, `7y`, `indefinite` (final values set by the future retention policy) |

### Required on datasets

| Key | Values |
|---|---|
| `layer` | `raw`, `staging`, `marts` |
| `classification` | Highest classification permitted in the dataset (see below) |
| `data_custodian` | `platform-sre` (implements storage, encryption and access) |
| `environment` | `sandbox` |
| `managed_by` | `pipeline` (raw) or `dbt` (staging, marts) |

**Dataset values to set in the console:**

| Dataset | `layer` | `classification` | `data_custodian` | `environment` | `managed_by` |
|---|---|---|---|---|---|
| `raw` | raw | secret | platform-sre | sandbox | pipeline |
| `staging` | staging | secret | platform-sre | sandbox | dbt |
| `marts` | marts | **sensitive** | platform-sre | sandbox | dbt |

> **Design rule:** `marts` is capped at **Sensitive**. **Secret** columns (SSN, card data, bank accounts) never leave `raw` or `staging`. **Confidential** columns (contact details, TLC license, HR data, precise locations, free text) are dropped, masked, or aggregated before they reach marts. Analysts are granted access to `marts` only.

## Domain register

The owner and steward values are **provisional** until the org design and governance council charter are finalized.

| `domain` | Scope | `data_owner` | `data_steward` |
|---|---|---|---|
| `rider` | Riders, cards, consent, preferences, surveys, support | `vp-rider-experience` | `rider-data-steward` |
| `driver` | Drivers, vehicles, assignments, shifts | `vp-driver-operations` | `driver-data-steward` |
| `trips` | Trips and trip operations | `vp-operations` | `ops-data-steward` |
| `finance` | Ledger, payments, payouts, refunds | `cfo` | `finance-data-steward` |
| `people` | Employees, departments, HR history | `vp-people` | `hr-data-steward` |
| `marketing` | Campaigns, segments, promotions | `vp-marketing` | `marketing-data-steward` |
| `risk` | Privacy requests, access logs, incidents, vendors, controls | `ciso` (table-level override allowed, e.g. `privacy-officer` for `privacy_requests`) | `risk-data-steward` |
| `governance` | Governance issues, decisions, ownership assignments (dbt seeds) | `data-governance-manager` | `data-governance-manager` |
| `reference` | Shared reference data (e.g. NYC taxi zones) | `data-governance-manager` | `ops-data-steward` |
| `digital` | *(Phase 4)* App and clickstream events | *TBD* | *TBD* |

## Formatting rules

BigQuery enforces most of these; ECT adds the last three.

1. Keys and values use **lowercase letters, digits, `_` and `-` only**, maximum **63 characters**. Keys must start with a letter.
2. Keys use `snake_case` (`data_owner`); values use `kebab-case` (`vp-driver-operations`).
3. **Roles, never people.** Owner and steward labels name a role, not a person. People change jobs; roles persist, and names don't leak into billing exports.
4. **No personal data or classified values in labels.** Labels are visible to anyone with metadata access and appear in billing data.
5. **Booleans are written `true` / `false`**, never `yes`, `y`, `1`.

## Example

`raw.fleet_drivers`:

```yaml
domain: driver
layer: raw
data_owner: vp-driver-operations
data_steward: driver-data-steward
classification: secret
source_system: fleet
data_origin: synthetic
contains_pii: "true"
pci_scope: "false"
retention: 7y
```

## Compliance and monitoring

- **Source of truth:** labels are set in code (loader and dbt), so every change goes through a reviewed commit. Dataset labels set in the console are recorded in this standard.
- **Automated check** *(planned, Project 3)*: a daily query against BigQuery's `INFORMATION_SCHEMA.TABLE_OPTIONS` flags any table that:
  - is missing a required label,
  - has a value outside the allowed list, or
  - is `contains_pii: true` with no `data_steward`.

  Findings feed the governance issue register.
- **Deliberate gaps** *(portfolio exercise)*: a small number of tables are intentionally shipped with missing or wrong labels, for example a missing `data_steward` or PII marked `false`. They are listed in the gap register so that detection can be measured: "the check found X of Y planted gaps."

## Ownership of this standard

| | |
|---|---|
| Standard owner | Data Governance Manager |
| Approver | Data Governance Council |
| Review cycle | Annually, or when a domain or system is added |
| Change process | Pull request to this repository, approved by the standard owner |
