# Empire City Taxi — Data Governance Organization

*Fictional organization for the ECT portfolio. All people are invented. Status: **DRAFT v0.1**, pending review.*

This document names who holds each governance role at ECT. It extends the [Data Ownership Model](data-ownership-model.md), which defines the roles, and feeds the [Data Governance Council Charter](data-governance-council-charter.md), which defines how those people make decisions together.

> **Names here, roles everywhere else.** People are named in this document, the council charter and meeting minutes. Labels, catalog ownership and data tables reference **role slugs** (e.g. `vp-driver-operations`) per the [Labeling Standard](labeling-standard.md), so a personnel change never requires relabeling data.

## Reporting lines

```
                                CEO · Marcus Delgado
        ┌──────────────┬─────────────┬──────────┴────┬───────────────┬────────────────┐
     CDO              CISO          CFO          General Counsel   VP Operations   (other VPs)
 Renée Okonkwo     Victor Hale   Thomas Brennan   Robert Feld      Luis Ortega
     │                 │                              │
 Data Governance   Platform / SRE              Privacy Officer
 Manager           Mateo Silva                 Priya Raman
 Jordan Ellis
     │
 Head of Data & Analytics
 Aisha Karim
```

- **The CDO** chairs the Data Governance Council, owns the data strategy, and is the **final escalation point** for data governance decisions.
- **The Data Governance Manager** runs the governance function day to day (the "hub"). This is the role the portfolio author plays.
- **The Privacy Officer** reports to General Counsel, not the CDO, so privacy can push back on data-use decisions independently.
- **Platform/SRE** reports to the CISO and acts as data custodian for every domain.

## Role holders

### Executive and hub roles

| Role | Person | Role slug | Governance responsibility |
|---|---|---|---|
| Chief Executive Officer | Marcus Delgado | `ceo` | Sponsors the governance program; receives the CDO's quarterly governance report |
| Chief Data Officer | Renée Okonkwo | `cdo` | Council chair and **final escalation point** as leader of the data organization: decides vetoed or deadlocked council matters; owns data strategy and the governance program |
| Data Governance Manager | Jordan Ellis | `data-governance-manager` | Council secretary; owns standards, catalog, issue register, KPIs |
| Chief Information Security Officer | Victor Hale | `ciso` | Security policy and access control; owner of the `risk` domain; security veto |
| Privacy Officer | Priya Raman | `privacy-officer` | Privacy obligations, consent, data subject requests; privacy veto |
| General Counsel | Robert Feld | `general-counsel` | Legal and regulatory interpretation (advisory) |

### Data Owners (accountable, one per domain)

| Domain | Owner | Role slug |
|---|---|---|
| `rider` | Hannah Cho, VP Rider Experience | `vp-rider-experience` |
| `driver` | Keisha Monroe, VP Driver Operations | `vp-driver-operations` |
| `trips` | Luis Ortega, VP Operations | `vp-operations` |
| `finance` | Thomas Brennan, CFO | `cfo` |
| `people` | Simone Laurent, VP People | `vp-people` |
| `marketing` | Derek Sullivan, VP Marketing | `vp-marketing` |
| `risk` | Victor Hale, CISO (`privacy_requests`: Priya Raman) | `ciso` / `privacy-officer` |
| `governance`, `reference` | Jordan Ellis, Data Governance Manager | `data-governance-manager` |

### Data Stewards (responsible day to day)

| Domain | Steward | Role slug |
|---|---|---|
| `rider` | Nadia Petrov | `rider-data-steward` |
| `driver` | Sam Whitaker | `driver-data-steward` |
| `trips` / `reference` | Grace Adeyemi | `ops-data-steward` |
| `finance` | Owen Park | `finance-data-steward` |
| `people` | Lena Fischer | `hr-data-steward` |
| `marketing` | Carlos Mendes | `marketing-data-steward` |
| `risk` | Yusuf Rahman | `risk-data-steward` |

### Custodians and consumers

| Role | Person | Role slug | Responsibility |
|---|---|---|---|
| Head of Platform / SRE (custodian) | Mateo Silva | `platform-sre` | Implements storage, encryption, access, backups and pipelines per owners' decisions |
| Head of Data & Analytics (consumer) | Aisha Karim | `data-analytics` | Represents data consumers; raises access requests and definition problems |

## Department objectives

Each department is measured on something real, and those measures sometimes pull against each other. **These tensions are why governance issues arise.** They are not failures of any one team.

| Department | Leader | Objective | Tends to push for… | …which conflicts with |
|---|---|---|---|---|
| Marketing | Derek Sullivan | Increase rider retention | Keeping and combining rider data, broad access | Privacy (minimization, deletion), Security |
| Finance | Thomas Brennan | Clean monthly reconciliation | One authoritative revenue definition | Operations' working definitions |
| Operations | Luis Ortega | Reduce trip cancellations | Speed and fewer process steps | Governance standards, change control |
| Driver Operations | Keisha Monroe | Faster driver onboarding | Activating drivers quickly | HR and Security offboarding checks |
| People (HR) | Simone Laurent | Smooth onboarding and offboarding | HR system as source of truth | Fleet system's own driver status |
| Security | Victor Hale | Reduce unauthorized access | Least privilege, masked data | Analytics' need for detail |
| Privacy | Priya Raman | Meet DSAR and consent deadlines | Deletion, consent enforcement | Marketing's historical data |
| Data & Analytics | Aisha Karim | Faster insights | Raw, row-level access | Security, Privacy |
| Data Governance | Jordan Ellis | Ownership, classification and quality coverage | Standardization | Everyone's speed |
