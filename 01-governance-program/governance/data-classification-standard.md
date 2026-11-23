# NorthLake Data Classification Standard

*Fictional standard for the NorthLake portfolio. Synthetic.*

## Purpose

Every data element NorthLake handles is assigned one of four classifications. Classification drives the handling controls — encryption, access, retention, logging — and feeds the SOC 2 / ISO 27001 control environment (control **DP-01** in the [audit project](../../02-soc2-iso-audit/)).

## The four tiers

| Tier | Classification | Definition | Examples in the estate |
|---|---|---|---|
| 1 | **Restricted** | PII, sensitive financial data, cardholder data, and secrets. Disclosure causes significant harm and/or regulatory breach. | SSN, email, phone, DOB, address; card number/expiry/name; balance, annual income, credit score; API-key secrets |
| 2 | **Confidential** | Sensitive business or financial data whose disclosure would harm NorthLake or a client, but not regulated PII. | Customer name, bank name, routing number, transaction amount, loan amount, lending decision, workforce email |
| 3 | **Internal** | Operational data for internal use; low harm if disclosed. | Internal IDs, timestamps, account/transaction status, MCC codes, audit-log attributes |
| 4 | **Public** | Approved for public release; no restriction. | Currency codes, published reference data |

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

## Assignment

- Classification is assigned at the **column** level (a table takes the highest classification of its columns for storage controls).
- The authoritative mapping for the estate is [`column-classification-map.csv`](column-classification-map.csv).
- In the catalog (OpenMetadata), classifications are applied as **tags** (`Restricted`, `Confidential`, `Internal`, `Public`) on columns; sensitive categories (PII, Cardholder Data) are applied as additional tags.

## Commonly missed columns

Classification is only as good as its coverage. Columns frequently under-classified in a first pass — flagged `commonly_missed = Yes` in the map — include: **date_of_birth** (sensitivity comes from combination, not the field alone), **card_expiry / cardholder_name** (cardholder data hiding next to the PAN), **api_key_hash** (a secret, even though hashed), **console_users.email** (workforce PII, not customer PII), and **lending decision** (adverse-action relevant). Finding these is the point of the governance review — see the walkthrough in the [project README](../README.md).
