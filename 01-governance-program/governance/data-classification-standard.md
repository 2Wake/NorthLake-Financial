# Empire City Taxi — Data Classification Standard

*Fictional standard for the ECT portfolio. Synthetic.*

## Purpose

Every data element ECT handles is assigned one of five classifications. The classification decides the handling controls (encryption, access, retention, logging) and feeds the SOC 2 / ISO 27001 / PCI control environment (control **DP-01** in the [audit project](../../02-soc2-iso-audit/)).

## The five tiers

Tier 1 is the most sensitive.

| Tier | Classification | Definition | Examples in the estate |
|---|---|---|---|
| 1 | **Secret** | Regulated identifiers, cardholder data, financial account data, and credentials. Disclosure causes severe harm, regulatory breach, or direct fraud. | **SSN** (drivers, employees); **cardholder data** (card number, expiry, cardholder name); **payout bank account**; secrets and keys |
| 2 | **Confidential** | Personal data that is regulated or high-harm, and sensitive HR data. Disclosure causes significant harm to a person or a privacy-law breach. | Rider/driver email, phone, home address; **TLC license**; background-check status; employee salary and performance rating; **trip pickup/dropoff locations**; free-text survey comments |
| 3 | **Sensitive** | Basic personal data and business or financial data whose disclosure would harm ECT, a rider, or a driver. | Rider/driver/employee names; employee work email; trip fares, tips, totals; ledger amounts; marketing budgets |
| 4 | **Internal** | Operational data for internal use. Low harm if disclosed. | Internal IDs, timestamps, trip distance, passenger count, payment-type codes, segment definitions |
| 5 | **Public** | Approved for public release. No restriction. | Currency codes, published fares, marketing site |

## Handling requirements by tier

| Control | Secret | Confidential | Sensitive | Internal | Public |
|---|---|---|---|---|---|
| Encryption at rest | Required; tokenize or encrypt at field level where feasible | Required | Required | Required | Optional |
| Encryption in transit | Required | Required | Required | Required | Required |
| Access | Named individuals only; approved; least privilege | Need-to-know; approved | Role-based; business need | Authenticated employees | Unrestricted |
| Access reviews | Quarterly | Quarterly | Semi-annual | Annual | — |
| Logging of access | Required, with alerting | Required | Required | Recommended | — |
| Non-production use | Never (synthetic or tokenized only) | Masked | Masked | Allowed | Allowed |
| Analytics layer (`marts`) | **Never** | Masked or aggregated only | Allowed | Allowed | Allowed |
| Retention | Minimum necessary + secure deletion | Defined schedule + secure deletion | Defined schedule | Business-defined | — |

Cardholder data (card number, expiry, name) also follows **PCI DSS**. It is stored, processed and transmitted only within the PCI scope, and never appears in free-text or analytics tables.

## Assignment

- Classification is assigned at the **column** level. A table takes the highest classification of its columns for storage controls, and that value is recorded in the table's `classification` label (see the [Labeling Standard](labeling-standard.md)).
- The authoritative mapping for the estate is [`column-classification-map.csv`](column-classification-map.csv).
- In the catalog, classifications are applied as **tags** on columns (`Secret`, `Confidential`, `Sensitive`, `Internal`, `Public`). Sensitive categories (PII, Cardholder Data, Location) are applied as additional tags.

## Commonly missed columns

Classification is only as good as its coverage. Columns frequently under-classified in a first pass are flagged `commonly_missed = Yes` in the map:

- **Trip pickup/dropoff locations.** Combined with a rider, they reveal a person's movements.
- **TLC license.** A regulated identifier often treated as mundane.
- **card_expiry / cardholder_name.** Cardholder data sitting next to the card number.
- **payout_bank_account.** Financial account data in an operational table.
- **Driver background-check status** and **employee performance rating.** Sensitive HR data.
- **trip_surveys.comment.** Free text that can contain phone numbers and emails (the DLP trap).

Finding these is the point of the governance review. See the walkthrough in the [project README](../README.md).
