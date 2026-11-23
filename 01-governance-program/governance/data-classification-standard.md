# Empire City Taxi — Data Classification Standard

*Fictional standard for the ECT portfolio. Synthetic.*

## Purpose

Every data element ECT handles is assigned one of four classifications. Classification drives the handling controls — encryption, access, retention, logging — and feeds the SOC 2 / ISO 27001 / PCI control environment (control **DP-01** in the [audit project](../../02-soc2-iso-audit/)).

## The four tiers

| Tier | Classification | Definition | Examples in the estate |
|---|---|---|---|
| 1 | **Restricted** | PII, sensitive financial data, cardholder data, driver regulated identifiers, and secrets. Disclosure causes significant harm and/or regulatory breach. | Rider/driver SSN, email, phone, address; **card number/expiry/name**; **TLC license**; payout bank account; background-check status; employee salary & performance; free-text survey comments |
| 2 | **Confidential** | Sensitive business or financial data whose disclosure would harm ECT, a rider, or a driver, but not regulated PII. | Rider/driver name, employee email, trip fares/tips/totals, marketing budget, **trip pickup/dropoff locations** |
| 3 | **Internal** | Operational data for internal use; low harm if disclosed. | Internal IDs, timestamps, trip distance/passenger count, payment-type codes, segment definitions |
| 4 | **Public** | Approved for public release; no restriction. | Currency codes, published fares, marketing site |

## Handling requirements by tier

| Control | Restricted | Confidential | Internal | Public |
|---|---|---|---|---|
| Encryption at rest | Required | Required | Required | Optional |
| Encryption in transit | Required | Required | Required | Required |
| Access | Need-to-know, approved, least privilege | Role-based, business need | Internal, authenticated | Unrestricted |
| Access reviews | Quarterly | Quarterly | Annual | — |
| Logging of access | Required | Required | Recommended | — |
| Masking in non-prod | Required | Required | Optional | — |
| Retention | Defined schedule + secure deletion | Defined schedule | Business-defined | — |

Cardholder data (card number/expiry/name) additionally follows **PCI DSS** — stored, processed, and transmitted only within the PCI scope, and never in free-text or analytics tables.

## Assignment

- Classification is assigned at the **column** level (a table takes the highest classification of its columns for storage controls).
- The authoritative mapping for the estate is [`column-classification-map.csv`](column-classification-map.csv).
- In the catalog (OpenMetadata), classifications are applied as **tags** (`Restricted`, `Confidential`, `Internal`, `Public`) on columns; sensitive categories (PII, Cardholder Data, Location) are applied as additional tags.

## Commonly missed columns

Classification is only as good as its coverage. Columns frequently under-classified in a first pass — flagged `commonly_missed = Yes` in the map — include: **trip pickup/dropoff locations** (combined with a rider, they reveal a person's movements), **TLC license** (a regulated identifier treated as mundane), **card_expiry / cardholder_name** (cardholder data hiding next to the PAN), **driver background-check status** and **employee performance rating** (sensitive HR), and **trip_surveys.comment** (free text that can contain phone numbers and emails — the DLP trap). Finding these is the point of the governance review — see the walkthrough in the [project README](../README.md).
