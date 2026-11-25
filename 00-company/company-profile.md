# Empire City Taxi Co. — Company Profile

*Fictional company used throughout this portfolio. All details are synthetic.*

## Snapshot

| | |
|---|---|
| **Industry** | Taxi & for-hire mobility (NYC) |
| **Services** | Licensed yellow/green cab fleet, a rider app (*ECT Rider*), and a driver app (*ECT Driver*) |
| **Stage / size** | Private, ≈150 corporate employees, ≈1,200 affiliated drivers · founded 2019 |
| **Headquarters** | Long Island City, Queens, NY (remote-friendly) |
| **Hosting** | Google Cloud. The fictional design names a primary region (`us-east4`) and a DR region (`us-central1`); the real portfolio platform runs in one location (BigQuery `US`) and recovers by rebuilding from code and the generator (POL-15). |
| **Compliance posture** | SOC 2 Type II (annual) · ISO 27001:2022 (in progress) · **PCI DSS** (card payments) · GDPR/CCPA · NYC TLC regulatory requirements |

## What Empire City Taxi does

ECT operates a licensed NYC taxi fleet and a technology platform that dispatches trips, processes rider payments, and pays drivers:

1. **ECT Rider** — a consumer app to hail, pay for, and rate trips.
2. **ECT Driver** — a driver app for dispatch, navigation, and earnings.
3. **Dispatch & Matching** — the service that assigns trips to drivers.
4. **Payments** — rider card processing and driver payouts.
5. **Console** — internal operations and administration (fleet, drivers, support, reporting).

Because ECT accepts card payments and employs/contracts drivers, it holds a broad range of sensitive data — rider PII, cardholder data, and driver PII — which puts it in scope for PCI DSS and privacy law in addition to SOC 2 / ISO 27001. Card numbers are entered only into the payment providers' card-entry component and in-cab terminals; ECT keeps a provider token and the last 4 digits (DOC-01 v2.0).

## Data Empire City Taxi handles

| Data type | Examples | Classification |
|---|---|---|
| Rider PII | Name, email, phone, home address | Confidential (name: Sensitive) |
| Cardholder data | Card number, expiry, cardholder name (PCI). Held by the payment providers, not ECT; ECT keeps a token and last 4 (Sensitive). Expiry and name are still stored pending GOV-148. | Secret |
| Driver PII | Name, **TLC license**, SSN, address, payout bank account, background-check status | Secret (SSN, bank account) / Confidential |
| Employee data | HR records, compensation, SSN | Secret (SSN) / Confidential |
| Financial data | Revenue, driver earnings, ledgers | Sensitive (payout bank accounts: Secret) |
| Trip / operational | Pickup/dropoff, fare, distance, payment type | Confidential (pickup/dropoff) / Sensitive (fare) / Internal |
| Marketing | Campaigns, rider segments | Sensitive (budgets) / Internal |
| Public | Published fares, marketing site | Public |

Classification scheme: **Secret → Confidential → Sensitive → Internal → Public** (defined in the Data Classification Standard, Project 1).

## Technology environment (audit scope)

| Layer | Technology |
|---|---|
| Cloud | Google Cloud Platform (GCP) |
| Compute | GKE (Kubernetes), Cloud Run |
| Data | BigQuery (analytics), Cloud SQL (Postgres), Cloud Storage |
| Identity | Okta (workforce SSO), GCP IAM (infrastructure) |
| Endpoints | Managed laptops (MDM); driver/rider mobile apps |
| CI/CD | GitHub + GitHub Actions, Terraform (IaC) |
| Security tooling | SIEM, cloud security posture monitoring, vulnerability scanner, PAM |
| GRC tooling | Compliance-automation platform (evidence collection), Jira (issues/remediation) |

## Trust Services Criteria in scope (SOC 2)

**Security (Common Criteria)**, **Availability**, and **Confidentiality**. *Processing Integrity* and *Privacy* are tracked internally but out of the current SOC 2 report scope (Privacy is covered under the GDPR/CCPA program; card handling under PCI DSS).

## Key third parties (sub-service organizations)

| Vendor | Service | Inherent risk |
|---|---|---|
| Google Cloud | Infrastructure (IaaS/PaaS) | Carve-out; relies on GCP's own SOC 2 |
| Okta | Identity provider | High |
| Payments processor | Card acquiring / rails | High |
| Background-check provider | Driver screening | High |
| Mapping / routing SaaS | Navigation & ETA | Moderate |
| Support-ticketing SaaS | Customer & driver support | Moderate |

Vendor assessments run through the **Vendor Risk Assessment** tool in `/docs` and the TPRM process in Project 1.

## Organizational context relevant to GRC

- **Security & GRC team**: a Security Engineering function plus a small GRC function (the role this portfolio simulates).
- **Control ownership** follows a hub-and-spoke model: the GRC function owns the *framework and evidence process*; individual controls are owned by the teams that operate them (IT, Platform Engineering, Driver Operations, HR, etc.).
- **Governance cadence**: quarterly risk review, quarterly access reviews, annual policy review, annual SOC 2 Type II, ISO surveillance on the ISO cycle, PCI attestation annually.
