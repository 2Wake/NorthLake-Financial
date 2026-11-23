# NorthLake Financial — GRC Program Portfolio

A **simulated, end-to-end Governance, Risk & Compliance program** for a fictional fintech, built to demonstrate hands-on GRC capability: standing up a control environment, running an audit cycle with real workpapers, automating evidence collection, and governing data and AI use.

Everything here uses **synthetic data for a fictional company**. No real company, customer, or audit data appears in this repository.

> **Why this exists.** GRC job descriptions consistently ask for things that are hard to *show* on a résumé — leading an audit end-to-end, testing controls, mapping frameworks, automating evidence. This repository is the working proof: a complete control environment and a documented audit cycle you can click through, read, and run.

---

## The company

**NorthLake Financial** is a Series B, cloud-native fintech (≈180 employees) that provides embedded payments and lending-analytics APIs to mid-market banks and credit unions. It is cloud-hosted on Google Cloud, handles customer PII and transaction data on behalf of its bank clients, and is pursuing **SOC 2 Type II** and **ISO/IEC 27001:2022** while maintaining **GDPR/CCPA** privacy obligations.

Full context: [`00-company/northlake-profile.md`](00-company/northlake-profile.md) · [`00-company/system-description.md`](00-company/system-description.md)

---

## Portfolio map

| # | Project | What it demonstrates | Status |
|---|---------|---------------------|--------|
| — | **Interactive tools** (`/docs`) | A working vendor-risk engine and a framework crosswalk, hosted on GitHub Pages | ✅ Live |
| 1 | [Data Governance Program](01-governance-program/) | Ownership model, data classification, quality, access governance | 🔜 Planned |
| 2 | [SOC 2 / ISO 27001 Audit](02-soc2-iso-audit/) | Control matrix, evidence/PBC tracking, **control-testing workpapers**, readiness assessment | 🏗️ In progress |
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
- The **audit project** (`02-`) is the spine — it ties the control environment to evidence and testing.
- The **crosswalk** (in `/docs`) shows how one tested control satisfies three frameworks at once.
- The **automation** and **AI** projects show how the manual program becomes continuous.

## Scope & integrity note

This is a learning and demonstration artifact. Framework mappings are illustrative and should defer to official reference tables (AICPA, ISO, NIST) in a real program. All names, systems, numbers, and "evidence" are fabricated for a fictional company.

## License

Content released under [CC BY 4.0](LICENSE); any code under MIT.
