# Vendor Security Assessment Questionnaires — A Reference Guide

A practical guide to the standardized questionnaires used in third-party risk management (TPRM): what each one is, its strengths and weaknesses, and when to reach for it based on the vendor you're assessing.

> **The core idea.** A mature TPRM program almost never writes questionnaires from scratch. It **risk-tiers the vendor first**, then sends a standardized questionnaire sized to that tier. The skill isn't inventing questions — it's choosing the right instrument, tailoring it, and evaluating what comes back. The [Vendor Risk Assessment tool](vendor-risk/) in this repo is a condensed, tiered distillation of the standards below.

---

## The TPRM assessment flow

```
  Inherent-risk tiering  ──►  Select questionnaire  ──►  Collect + evidence  ──►  Review & score  ──►  Remediate / accept  ──►  Reassess
  (data, access,              (sized to the tier)        (SOC 2, pen test,       (gaps vs. your       (contract clauses,      (periodic)
   criticality)                                           cert evidence)          requirements)         risk acceptance)
```

Inherent risk (what the vendor is trusted with) decides **depth**. A vendor with no access to data gets a light touch; one processing customer PII gets the full assessment plus evidence review.

---

## At a glance

| Questionnaire | Source | Cost | Depth | Best for |
|---|---|---|---|---|
| **SIG Core** | Shared Assessments | Paid (membership) | Very deep (1000s of Qs, scoped) | High-risk / critical vendors, regulated industries |
| **SIG Lite** | Shared Assessments | Paid (membership) | Moderate (~300 Qs) | Standard vendors, first-pass on higher-risk |
| **CAIQ** | Cloud Security Alliance | Free | Moderate–deep (cloud-specific) | SaaS / cloud / IaaS vendors |
| **VSAQ** | Google (open source) | Free | Light–moderate, adaptive | Quick web/app-centric assessments, learning |
| **HECVAT** | EDUCAUSE | Free | Light → Full tiers | Vendors selling to higher education |
| **HITRUST CSF** | HITRUST | Paid (certification) | Very deep, certifiable | Healthcare / PHI-handling vendors |
| **Bespoke short-form** | You | — | Light (10–30 Qs) | Low-risk vendors, pre-screening |
| *(Evidence, not a questionnaire)* **SOC 2 Type II report** | AICPA / vendor's CPA | — | — | Any vendor that has one — often *replaces* a questionnaire |

---

## The standards in detail

### SIG (Standardized Information Gathering) — Shared Assessments
The de-facto industry standard for TPRM. A large, scoped question library maintained by the Shared Assessments member community, refreshed annually and mapped to many frameworks (ISO 27001, NIST, PCI, etc.).

- **SIG Core** — the full library; you scope it to the vendor's risk domains.
- **SIG Lite** — a shorter, high-level subset for a faster assessment.

**Pros:** Comprehensive, framework-mapped, widely recognized — vendors often have a SIG ready to share. One assessment covers many frameworks. **Cons:** Requires a paid Shared Assessments membership; SIG Core can be heavy and needs scoping to avoid over-asking. **Best use case:** High-risk and critical vendors, and programs in regulated industries (financial services, healthcare) that need defensible, standardized coverage.

### CAIQ (Consensus Assessments Initiative Questionnaire) — Cloud Security Alliance
A free, cloud-focused questionnaire that maps directly to the CSA **Cloud Controls Matrix (CCM)**. Many SaaS vendors publish a completed CAIQ in the CSA **STAR Registry**, so you can often get it without even sending a request.

**Pros:** Free; purpose-built for cloud/SaaS; maps to CCM (and through it to ISO 27001, SOC 2, NIST); frequently pre-filled and public. **Cons:** Cloud-specific — weaker fit for non-cloud vendors; self-attested unless backed by CSA STAR Level 2 (third-party validated). **Best use case:** SaaS, PaaS, and IaaS vendors — the first thing to ask a cloud vendor for.

### VSAQ (Vendor Security Assessment Questionnaire) — Google (open source)
An open-source, **adaptive** questionnaire (questions branch based on answers) that Google released publicly. Lighter weight and developer-friendly.

**Pros:** Free and open; adaptive flow avoids irrelevant questions; a great *learning* reference because you can read the question logic in source. **Cons:** Less of an industry "standard" that vendors recognize; narrower than SIG; maintained lightly. **Best use case:** Fast, web/application-centric assessments, and as a teaching tool for how questionnaires are structured.

### HECVAT (Higher Education Community Vendor Assessment Toolkit) — EDUCAUSE
A free toolkit tailored to vendors selling into higher education, with tiers: **HECVAT Lite** (quick), **Full** (comprehensive), and specialized versions.

**Pros:** Free; tiered; purpose-built for the data and compliance concerns of universities (FERPA, research data). **Cons:** Niche to higher ed; less useful outside that sector. **Best use case:** Any vendor being evaluated by a college, university, or ed-tech buyer.

### HITRUST CSF — HITRUST Alliance
Not just a questionnaire but a **certifiable framework** harmonizing HIPAA, ISO, NIST, PCI and more. A vendor can hold a HITRUST certification, which is strong third-party assurance.

**Pros:** Deep, healthcare-oriented, independently certifiable — a HITRUST cert is high-assurance evidence. **Cons:** Expensive and heavy for vendors to obtain; overkill outside healthcare/PHI. **Best use case:** Vendors handling PHI, or any healthcare-sector third party where HIPAA assurance matters.

### Bespoke short-form (your own)
A short internal questionnaire (10–30 questions) for low-risk vendors or as a pre-screen before deciding whether a deeper assessment is warranted.

**Pros:** Fast, proportionate, no licensing. **Cons:** Not standardized or externally recognized; easy to under-scope if misapplied to a risky vendor. **Best use case:** Low inherent-risk vendors (no data, no access) and initial triage. *This is the tier the NorthLake tool's "light touch" path represents.*

### SOC 2 Type II report — the evidence that often replaces a questionnaire
Strictly, a SOC 2 report is an **independent attestation**, not a questionnaire — but in practice it's the single most valuable artifact in vendor review. For a vendor with a current SOC 2 Type II, reviewing the report (scope, period, exceptions, complementary user-entity controls) can substitute for much of a questionnaire. Always ask for it first; read the exceptions, not just the opinion.

---

## Choosing by vendor type and tier

| Vendor situation | Start with | Then |
|---|---|---|
| **Cloud / SaaS, any tier** | Ask for their **CAIQ** (or CSA STAR entry) and **SOC 2 Type II** | Escalate to SIG Lite/Core if high-risk or gaps remain |
| **High-risk / critical** (customer PII, privileged access) | **SIG Core** (scoped) + SOC 2 Type II + pen-test summary | Contractual security addendum; annual reassessment |
| **Standard-risk** | **SIG Lite** or **CAIQ** + SOC 2 | Targeted follow-ups on gaps |
| **Low-risk** (no data, no access) | **Bespoke short-form** | Re-tier only if scope changes |
| **Healthcare / PHI** | **HITRUST** certification if held; else SIG + HIPAA addendum | BAA in place |
| **Higher-ed buyer** | **HECVAT** (Lite → Full by risk) | — |
| **Has a current SOC 2 Type II** | **Review the report first** | Short questionnaire only for gaps the report doesn't cover |

### Two rules of thumb

1. **Match depth to inherent risk.** Over-assessing a low-risk vendor wastes everyone's time and trains vendors to rush; under-assessing a high-risk one is where incidents come from.
2. **Prefer evidence over attestation.** A completed questionnaire is self-reported. A SOC 2 Type II, a penetration-test report, or a HITRUST/ISO certificate is independently validated — weight it accordingly.

---

## How this maps to the NorthLake tool

The [Vendor Risk Assessment tool](vendor-risk/) implements the *process* these standards support: inherent-risk tiering, weighted control scoring across the same domains SIG and CAIQ cover (governance, access, data protection, infrastructure, incident response, resilience, compliance, subprocessors), and a residual-risk rating with an onboarding decision. It's a tiered, condensed instrument — the kind you'd send in place of a full SIG — not a replacement for the standards when deep, regulated assurance is required.

*All examples and the companion tool use a fictional vendor and synthetic data.*
