# Project 1 — Data Governance Program *(planned)*

Stands up NorthLake's data governance program over a synthetic data estate.

**Planned contents**
- **Ownership model** — hub-and-spoke: GRC owns the framework; data owners/stewards own domains.
- **Data classification standard** — the four-tier scheme (Restricted → Confidential → Internal → Public) with handling rules.
- **Synthetic data estate** — a generated BigQuery-style catalog (tables, columns, metadata) using Python/Faker, with intentional classification gaps and quality issues to find and remediate.
- **Data quality rules** — completeness/validity checks and a remediation log.
- **Access governance** — least-privilege role design and the quarterly access-review process that feeds control AC-02.

Ties to: control DP-01/DP-02 in the [audit project](../02-soc2-iso-audit/), and the access-review workpaper.
