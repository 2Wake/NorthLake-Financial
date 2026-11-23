# Project 2 — SOC 2 / ISO 27001 Audit Cycle

**The spine of the portfolio.** This project simulates running Empire City Taxi's annual **SOC 2 Type II** examination (with ISO 27001:2022 mapped alongside), from control environment to tested evidence to findings — the work a GRC owner actually does across an audit cycle.

It is built to demonstrate four things most résumés can only assert:

1. **A control environment** — a matrix of controls mapped to SOC 2, ISO 27001, and NIST, with owners and test methods.
2. **Evidence / PBC management** — tracking what the auditor requested, who provides it, and whether it's been collected and reviewed.
3. **Control testing** — actual workpapers that define a test, pull a population and sample, execute steps, and document results and exceptions.
4. **Readiness & findings** — an honest gap assessment with findings rated by severity and mapped to remediation.

> **Note on scope of the demonstration.** SOC 2 Type II is an *attestation performed by a licensed CPA firm* — a company does not audit itself. These workpapers are written from the **GRC owner's side of the engagement**: the internal control testing, self-assessment, and evidence preparation that make an external audit go smoothly. That is exactly the "audit readiness / audit facilitation / evidence collection / control validation" work named in the job descriptions this portfolio targets.

## Contents

| File | What it is |
|---|---|
| [`control-matrix.csv`](control-matrix.csv) | The control environment — 26 controls, framework mappings, owners, test method & frequency |
| [`evidence-tracker.csv`](evidence-tracker.csv) | The PBC / evidence register — requested items, owners, cadence, collection & review status |
| [`workpapers/`](workpapers/) | Control-testing workpapers (the actual test execution) |
| [`audit-readiness-assessment.md`](audit-readiness-assessment.md) | Readiness summary with findings rated Critical → Low and remediation |

## The audit cycle (how to read this project)

```
  Scope ──► Control matrix ──► Evidence requests (PBC) ──► Control testing ──► Findings ──► Remediation ──► Report
            (control-matrix)   (evidence-tracker)         (workpapers/)       (readiness-assessment)
```

1. **Scope** is set by the services and TSC in the [system description](../00-company/system-description.md): Security, Availability, Confidentiality.
2. The **control matrix** defines what's in place and how each control is tested.
3. The **evidence tracker** manages the Provided-By-Client (PBC) list — the backbone of any audit.
4. **Workpapers** document the internal testing of a sample of controls.
5. The **readiness assessment** rolls testing up into findings and a go/no-go view.

## How testing is rated

Each tested control receives one of:

- **Effective** — operating as designed across the period; no exceptions.
- **Exception noted** — one or more instances where the control did not operate as designed; rated by impact.
- **Deficiency** — a design or operating gap. Aggregated deficiencies may rise to a *significant deficiency* or *material weakness*.

Exceptions feed the [readiness assessment](audit-readiness-assessment.md), where they're rated and assigned remediation.

## Frameworks

Controls are mapped to **SOC 2 (Trust Services Criteria)**, **ISO/IEC 27001:2022 Annex A**, and **NIST 800-53 Rev 5** — the same crosswalk used by the interactive tool in `/docs`. One tested control evidences all three.
