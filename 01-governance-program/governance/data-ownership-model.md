# Empire City Taxi — Data Ownership Model

*Fictional model for the ECT portfolio. Synthetic.*

## Hub-and-spoke governance

ECT runs a **hub-and-spoke** operating model. A central **data-governance function (the hub)** owns the framework — the classification standard, the glossary, the quality rules, and the catalog — while **domain teams (the spokes)** own their data day-to-day. This scales governance without creating a bottleneck: the hub sets the rules; the spokes operate within them.

```
                         ┌─────────────────────────┐
                         │   Data Governance (hub) │
                         │  standard · glossary ·  │
                         │  quality rules · catalog│
                         └────────────┬────────────┘
         ┌───────────┬────────────┬───┴────┬────────────┬───────────┐
       Rider      Driver       Trips/Ops  Finance    People/HR     Marketing
       domain     domain        domain    domain      domain        domain
```

## Roles (RACI)

| Role | Who | Responsibility |
|---|---|---|
| **Data Owner** | Domain executive (e.g., VP Driver Operations) | Accountable for a data domain: approves classification and access, owns risk acceptance. |
| **Data Steward** | Senior analyst/manager in the domain | Operational: maintains definitions, monitors quality, triages issues, keeps the glossary current. |
| **Data Custodian** | Platform/SRE, Security | Technical: implements storage, encryption, access controls, and backups per the owner's decisions. |
| **Governance (hub)** | GRC / data-governance function | Owns the framework, the catalog, and the standards; reports coverage and quality to leadership. |

## Domain ownership for the estate

| Domain | Tables | Owner | Steward | Custodian |
|---|---|---|---|---|
| Rider | `riders`, `rider_cards`, `trip_surveys` | VP Rider Experience | Rider Data Steward | Platform/SRE |
| Driver | `drivers` | VP Driver Operations | Driver Data Steward | Platform/SRE |
| Trips/Ops | `trips` | VP Operations | Ops Data Steward | Platform/SRE |
| Finance | `financial_ledger` | CFO | Finance Data Steward | Platform/SRE |
| People/HR | `employees` | VP People | HR Data Steward | Security Eng |
| Marketing | `marketing_campaigns`, `rider_segments` | VP Marketing | Marketing Data Steward | Platform/SRE |

## How ownership shows up in the catalog

In OpenMetadata, each table/dataset is assigned an **Owner** (team or user) and domain. Stewards are the reviewers for quality incidents and glossary changes. This is also what makes the **access-review** control real: owners certify who should have access to their domain's Restricted data each quarter, feeding control **AC-02** in the [audit project](../../02-soc2-iso-audit/).

## Why this model

- **Accountability without central bottleneck** — the people closest to the data own its quality and access, while the hub keeps the rules consistent.
- **Auditable** — every Restricted table (rider PII, driver PII, cardholder data, HR) has a named owner who can be shown to certify access, which is exactly what a SOC 2 / ISO access-review control needs.
