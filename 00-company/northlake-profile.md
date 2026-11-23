# NorthLake Financial — Company Profile

*Fictional company used throughout this portfolio. All details are synthetic.*

## Snapshot

| | |
|---|---|
| **Industry** | Fintech — embedded payments & lending analytics (B2B2C) |
| **Customers** | Mid-market banks and credit unions (≈40 institutions) |
| **Stage / size** | Series B · ≈180 employees · founded 2021 |
| **Headquarters** | Atlanta, GA (remote-first) |
| **Hosting** | Google Cloud (primary region `us-east4`, DR in `us-central1`) |
| **Compliance posture** | SOC 2 Type II (annual) · ISO 27001:2022 (in progress) · GDPR/CCPA · bank-partner security reviews |

## What NorthLake does

NorthLake provides API products its bank clients embed into their own digital banking apps:

1. **PayRails** — payment initiation and transaction enrichment APIs.
2. **LendLens** — lending-analytics APIs that score and categorize applicant financial data.
3. **Console** — a web dashboard where bank staff configure products, pull reports, and manage users.

Because NorthLake processes data *on behalf of* regulated banks, its clients push contractual security obligations down to NorthLake (security addenda, right-to-audit, breach-notification SLAs), and NorthLake's SOC 2 report is a routine item in its clients' own vendor due diligence.

## Data NorthLake handles

| Data type | Examples | Classification |
|---|---|---|
| Customer PII | Name, email, address, phone of bank end-users | Restricted |
| Financial data | Transaction records, account balances, lending application data | Restricted |
| Authentication data | Credentials, tokens, session data | Restricted |
| Bank configuration | Product settings, API keys, institution metadata | Confidential |
| Operational data | Logs, metrics, support tickets | Confidential / Internal |
| Marketing & public | Website, public docs | Public |

Classification scheme: **Restricted → Confidential → Internal → Public** (defined in the Data Classification Standard, Project 1).

## Technology environment (audit scope)

| Layer | Technology |
|---|---|
| Cloud | Google Cloud Platform (GCP) |
| Compute | GKE (Kubernetes), Cloud Run |
| Data | BigQuery (analytics), Cloud SQL (Postgres), Cloud Storage |
| Identity | Okta (workforce SSO), GCP IAM (infrastructure) |
| Endpoints | Managed laptops (MDM), no on-prem servers |
| CI/CD | GitHub + GitHub Actions, Terraform (IaC) |
| Security tooling | SIEM, cloud security posture monitoring, vulnerability scanner, PAM |
| GRC tooling | Compliance-automation platform (evidence collection), Jira (issues/remediation) |

## Trust Services Criteria in scope (SOC 2)

**Security (Common Criteria)**, **Availability**, and **Confidentiality**. *Processing Integrity* and *Privacy* are tracked internally but out of the current SOC 2 report scope (Privacy is covered under the GDPR/CCPA program).

## Key third parties (sub-service organizations)

| Vendor | Service | Inherent risk |
|---|---|---|
| Google Cloud | Infrastructure (IaaS/PaaS) | Carve-out; relies on GCP's own SOC 2 |
| Okta | Identity provider | High |
| A payments processor | Card rails | High |
| A data-analytics SaaS | Internal BI | Moderate |
| A support-ticketing SaaS | Customer support | Moderate |

Vendor assessments for these run through the **Vendor Risk Assessment** tool in `/docs` and the TPRM process in Project 1.

## Organizational context relevant to GRC

- **Security & GRC team**: a Security Engineering function plus a small GRC function (the role this portfolio simulates).
- **Control ownership** follows a hub-and-spoke model: the GRC function owns the *framework and evidence process*; individual controls are owned by the teams that operate them (IT, Platform Engineering, HR, etc.).
- **Governance cadence**: quarterly risk review, quarterly access reviews, annual policy review, annual SOC 2 Type II, ISO surveillance on the ISO cycle.
