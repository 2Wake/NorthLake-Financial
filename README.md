# Empire City Taxi Co. — GRC Program Portfolio

A **simulated, end-to-end Governance, Risk & Compliance program** for a fictional NYC taxi & mobility operator, built to demonstrate hands-on GRC capability: standing up a control environment, running an audit cycle with real workpapers, governing data (over **real public NYC taxi data** plus synthetic sensitive data), and automating evidence and AI-assisted review.

Everything here uses **synthetic data for a fictional company**, layered on top of the **public NYC TLC trip dataset**. No real private company, customer, driver, or audit data appears in this repository.

> **Why this exists.** GRC job descriptions consistently ask for things that are hard to *show* on a résumé — leading an audit end-to-end, testing controls, mapping frameworks, classifying sensitive data, automating evidence. This repository is the working proof: a complete control environment and a documented audit cycle you can click through, read, and run.

---

## The company

**Empire City Taxi Co. (ECT)** is a fictional NYC taxi & for-hire mobility operator (≈150 corporate employees, ≈1,200 affiliated drivers) running a cloud-native platform on Google Cloud: rider and driver apps, dispatch, card payments, and a data warehouse. It handles rider PII, cardholder data, and driver PII, and is pursuing **SOC 2 Type II** and **ISO/IEC 27001:2022** while meeting **PCI DSS**, **GDPR/CCPA**, and NYC TLC obligations.

Full context: [`00-company/company-profile.md`](00-company/company-profile.md) · [`00-company/system-description.md`](00-company/system-description.md)

---

## Portfolio map

| # | Project | What it demonstrates | Status |
|---|---------|---------------------|--------|
| — | **Interactive tools** (`/docs`) | A working vendor-risk engine and a framework crosswalk, hosted on GitHub Pages | ✅ Live |
| 1 | [Data Governance Program](01-governance-program/) | Classification, glossary, ownership & data quality on **BigQuery + OpenMetadata**, over real NYC-taxi data + synthetic sensitive data | ✅ Built |
| 2 | [SOC 2 / ISO 27001 Audit](02-soc2-iso-audit/) | Control matrix, evidence/PBC tracking, **control-testing workpapers**, readiness assessment | ✅ Built |
| 3 | [GRC Automation](03-grc-automation/) | Python-driven evidence collection and control-drift monitoring | 🔜 Planned |
| 4 | [AI in GRC](04-ai-in-grc/) | Using AI to assist classification/review, with human-owned design and guardrails | 🔜 Planned |

## Interactive tools (GitHub Pages)

Hosted from `/docs` so they run in a browser with no setup:

- **Vendor Risk Assessment** — rate a vendor's inherent exposure, score its controls across eight domains, and derive a residual-risk rating and onboarding recommendation. Source: [`questionnaires/vendor-risk/`](questionnaires/vendor-risk/)
- **Control Crosswalk** — a searchable SOC 2 ↔ ISO 27001:2022 ↔ NIST 800-53 mapping with per-control implementation and evidence notes.

> Live site: _enable GitHub Pages on the `main` branch, `/docs` folder — see [`docs/README.md`](docs/README.md)._

---

## How to read this repo

- Start with the **company profile** to understand the fictional environment.
- The **governance program** (`01-`) builds the data estate (real taxi trips + synthetic sensitive data) that the rest of the work governs.
- The **audit project** (`02-`) ties the control environment to evidence and testing.
- The **crosswalk** (in `/docs`) shows how one tested control satisfies three frameworks at once.
- The **automation** and **AI** projects show how the manual program becomes continuous.

## Scope & integrity note

This is a learning and demonstration artifact. Framework mappings are illustrative and should defer to official reference tables (AICPA, ISO, NIST) in a real program. The operational trip data is the **public NYC TLC dataset**; all names, drivers, riders, cards, employees, financials, and "evidence" are fabricated for a fictional company.

## License

Content released under [CC BY 4.0](LICENSE); any code under MIT.
