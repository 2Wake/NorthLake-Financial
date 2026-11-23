# Project 1 — Data Governance Program

Stands up a working data-governance program over a mixed data estate — **real public NYC taxi trips** plus **synthetic sensitive data** — on **BigQuery + OpenMetadata**: a catalog with **column classification**, a **business glossary**, **data ownership**, and **data-quality** monitoring. Classification traps and quality issues are deliberately present (seeded in the synthetic tables; genuinely occurring in the real trips), so the governance work is real rather than cosmetic.

This project is the foundation the rest of the portfolio builds on: it produces the data estate that [Project 3 (automation)](../03-grc-automation/) monitors and [Project 4 (AI in GRC)](../04-ai-in-grc/) classifies, and it operates the classification and access-review controls (**DP-01**, **AC-02**) tested in [Project 2 (audit)](../02-soc2-iso-audit/).

> The operational trips are the **public NYC TLC dataset**. Everything else — riders, drivers, cards, employees, financials, marketing — is **synthetic**. No real private data.

## What it demonstrates

- Designing a **data classification standard** and applying it at column level.
- A **hub-and-spoke ownership model** (owners, stewards, custodians).
- Building a **business glossary** and linking terms to data.
- Defining and running **data-quality rules** across six dimensions plus a **DLP/privacy** check, with a remediation log — on both synthetic and real data.
- Doing all of the above in a real open-source **data catalog** (OpenMetadata) over **BigQuery** — demonstrable catalog-tool experience.

## The data estate

| Table | Source | Rows | Notable sensitive columns |
|---|---|---|---|
| `trips` | **Real** (NYC TLC public data, sampled) | ~100k | pickup/dropoff location (tied to rider) |
| `riders` | Synthetic | 2,000 | email, phone, home_address |
| `rider_cards` | Synthetic | 1,800 | card_number, expiry, cardholder_name (PCI) |
| `trip_surveys` | Synthetic | 3,000 | comment (free-text PII) |
| `drivers` | Synthetic | 300 | tlc_license, ssn, payout_bank_account, background_check |
| `employees` | Synthetic | 150 | ssn, salary, performance_rating |
| `financial_ledger` | Synthetic | 144 | amount |
| `marketing_campaigns`, `rider_segments` | Synthetic | 40 / 12 | budget |

The real trips carry synthetic `driver_id` / `rider_id` columns so they **link** to the driver/rider tables — which also lets the quality checks test referential integrity *across* real and synthetic data.

**Seeded on purpose** (synthetic tables): classification traps (TLC license, card expiry, background-check status, performance rating, and free-text survey comments are commonly under-classified) and quality defects (null/invalid/duplicate emails, bad SSNs, out-of-range ratings, orphaned surveys, PII in comments). **Genuinely present** (real trips): negative fares, impossible passenger counts, zero/absurd distances, dropoff-before-pickup — issues you discover, not seed.

## Governance artifacts

| File | What it is |
|---|---|
| [`governance/data-classification-standard.md`](governance/data-classification-standard.md) | The four-tier scheme + handling requirements |
| [`governance/data-ownership-model.md`](governance/data-ownership-model.md) | Hub-and-spoke roles and domain ownership |
| [`governance/column-classification-map.csv`](governance/column-classification-map.csv) | The authoritative column→classification "answer key" |
| [`governance/business-glossary.csv`](governance/business-glossary.csv) | Glossary terms, ready to import into OpenMetadata |
| [`governance/data-quality-rules.md`](governance/data-quality-rules.md) | The DQ rule catalog with BigQuery SQL (incl. real-trips rules) |
| [`data/remediation_log.csv`](data/) | Output of the DQ run — the issues found |

---

## Walkthrough

### Prerequisites
- Python 3 (standard library only)
- A Google account and a **BigQuery sandbox** project (free, no credit card)
- `gcloud` + `bq` CLI, authenticated (`gcloud auth login`)
- **Docker** 20.10+ and **Docker Compose** v2, with ≥ 6 GiB RAM allocated

### Step 1 — Generate the synthetic tables
```bash
cd scripts
python3 generate_estate.py        # writes synthetic CSVs to ../data/
python3 run_data_quality.py       # writes ../data/remediation_log.csv
```

### Step 2 — Pull the real trips + load the synthetic tables
```bash
# edit pull_trip_sample.sql: replace PROJECT with your project id, then:
bq query --use_legacy_sql=false < pull_trip_sample.sql   # creates PROJECT.ect.trips
./load_to_bigquery.sh YOUR_PROJECT_ID ect US             # loads the synthetic tables
```

### Step 3 — Stand up OpenMetadata
```bash
mkdir openmetadata-docker && cd openmetadata-docker
curl -sL -o docker-compose.yml \
  https://github.com/open-metadata/OpenMetadata/releases/download/2.1.0-release/docker-compose.yml
docker compose -f docker-compose.yml up --detach
```
Open **http://localhost:8585** — log in with `admin@open-metadata.org` / `admin`.
*(Check the OpenMetadata releases page for the current version.)*

### Step 4 — Connect OpenMetadata to BigQuery
1. In GCP, create a **service account** with **BigQuery Data Viewer** + **BigQuery Metadata Viewer**, and download its **JSON key**. *Keep this key out of the repo — it's gitignored.*
2. In OpenMetadata: **Settings → Services → Databases → Add New Service → BigQuery**. Paste the JSON and your project id.
3. Run **Metadata** ingestion — the `ect` tables appear. Run the **Profiler** to populate column statistics (profile `trips` to see the real mess).

### Step 5 — Classify, define, and own
- **Classification tags:** create a `DataClassification` tag group with `Restricted / Confidential / Internal / Public`. Run OpenMetadata's **auto-classification/PII** first, then check it against [`column-classification-map.csv`](governance/column-classification-map.csv) — note what it missed (the `commonly_missed = Yes` columns are the interesting ones, e.g., the free-text `comment` and the trip locations).
- **Glossary:** **Govern → Glossary → Import** and upload [`business-glossary.csv`](governance/business-glossary.csv). Link terms (e.g., *Cardholder Data*, *TLC License*) to the relevant columns.
- **Ownership:** assign each table an **Owner** and domain per [`data-ownership-model.md`](governance/data-ownership-model.md).

### Step 6 — Data quality in the catalog
Recreate the [DQ rules](governance/data-quality-rules.md) as **Table/Column Tests** (e.g., `rating` between 1–5; `tlc_license` not-null; the trips reconciliation). Run them; the catalog shows live pass/fail per table. The committed [`remediation_log.csv`](data/) is the synthetic-table checks run locally.

### Step 7 — Capture it for the portfolio
Screenshot the running catalog into [`screenshots/`](screenshots/): a classified table (e.g., `drivers` with Restricted tags), the glossary, a failing DQ test, the `trips` profiler showing real anomalies, and an owned domain.

---

## Credentials & safety
- The service-account JSON key is **gitignored** — never commit it.
- Use a **read-only** service account and the **sandbox** project.
- Synthetic data for everything except the public NYC trips; nothing here touches real private systems.
