# Vendor Risk Assessment — Tool Spec

`vendor-risk-assessment.html` is the interactive third-party risk assessment used in this portfolio. It is also published to [`/docs`](../../docs/) for the live site. This document explains where it came from and exactly how it scores.

## About this tool — provenance

This is an **original tool built for this GRC portfolio**, not a copy of any proprietary questionnaire. Its questions were written to mirror the **structure and domains** of the recognized standards — the CSA **CAIQ**, Shared Assessments **SIG Lite**, and the **NIST 800-53 SR / 800-161** supply-chain themes — organized into eight control domains. It is **modeled on** those standards; it does not reproduce the licensed SIG library or any copyrighted question set verbatim.

The scoring approach (inherent risk × control effectiveness → residual risk) is **standard third-party-risk methodology**, consistent with the Shared Assessments risk-tiering model; it is not proprietary to any vendor.

**How to describe it honestly:** *"A vendor-risk tool I built for a GRC portfolio, modeled on standard questionnaires (CAIQ, SIG Lite) and standard inherent/residual risk-tiering, using a fictional company and synthetic data."* It should **not** be described as an official, certified, or standards-verbatim assessment. It was built with AI assistance — itself a relevant GRC-automation skill.

All vendors, scores, and data in the tool are **fictional/synthetic**.

## What it does

1. Rates a vendor's **inherent risk** from what it would be trusted with (data sensitivity, system access, business criticality).
2. Scores **control effectiveness** across eight domains from a weighted questionnaire.
3. Derives a **residual risk** rating by combining the two, and outputs flagged gaps, remediations, and an onboarding recommendation.

It loads with a sample vendor so it opens in a realistic working state. Feeds control **VN-01** in the [audit project](../../02-soc2-iso-audit/).

---

## Scoring mechanism

### 1. Inherent risk

Three inputs, each rated 1–4 (1 = lowest exposure, 4 = highest):

| Input | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Data sensitivity | Public / none | Internal / Sensitive | Confidential (PII/PHI) | Secret (SSN/cardholder/credentials) |
| System access | None | Limited / read-only | Application / system | Privileged / admin |
| Business criticality | Low | Moderate | High | Mission-critical |

**Weighted inherent score** (data weighted highest, as sensitivity drives exposure):

```
inherent_score = (data × 0.40) + (access × 0.35) + (criticality × 0.25)
```

**Inherent tier** from the score:

| Score | Tier |
|---|---|
| < 1.85 | Low |
| 1.85 – < 2.70 | Moderate |
| 2.70 – < 3.45 | High |
| ≥ 3.45 | Critical |

### 2. Control effectiveness

Each questionnaire item carries a weight reflecting how much the control matters:

| Weight label | Value |
|---|---|
| KEY (e.g., MFA, encryption, SOC 2, breach notification) | 3 |
| STD | 2 |
| LOW | 1 |

Each answer earns credit:

| Answer | Credit |
|---|---|
| Yes | 1.0 |
| Partial | 0.5 |
| No | 0.0 |
| N/A | *excluded from the calculation entirely* |

**Control effectiveness %** (N/A items drop out of both numerator and denominator, so they neither help nor hurt):

```
control_effectiveness = Σ(credit × weight) / Σ(weight of applicable items) × 100
```

**Control band:**

| Effectiveness | Band |
|---|---|
| ≥ 85% | Strong |
| 65 – 84% | Adequate |
| 40 – 64% | Weak |
| < 40% | Poor |

### 3. Residual risk

Residual risk is inherent exposure **modulated by** how effective the controls are — strong controls pull a high-inherent vendor down, weak controls push it up. The lookup:

| Inherent ↓ / Controls → | Strong | Adequate | Weak | Poor |
|---|---|---|---|---|
| **Critical** | High | High | Critical | Critical |
| **High** | Moderate | High | High | Critical |
| **Moderate** | Low | Moderate | High | High |
| **Low** | Low | Low | Moderate | Moderate |

The logic: even excellent controls can't make a vendor handling your most sensitive data "low" residual risk (Critical-inherent floors at High); and weak controls on a sensitive vendor drive residual to Critical.

### 4. Gaps and recommendation

- **Key gaps** — every KEY (weight 3) or STD (weight 2) item answered **No** or **Partial** is surfaced as a finding with a specific remediation, sorted most-severe first.
- **Recommendation** — driven by the residual tier:

| Residual | Recommendation |
|---|---|
| Critical | Do not onboard until critical gaps are remediated and re-assessed. |
| High | Onboard only with a remediation plan, security addendum, and enhanced monitoring. |
| Moderate | Approve with standard controls, a DPA, and annual reassessment. |
| Low | Approve; reassess annually or on material change. |

---

## Worked example (the sample vendor)

The tool loads with *CloudPay Analytics* — inherent inputs: **Data = 3 (Confidential), Access = 3 (system), Criticality = 3 (High)**.

**Inherent:** `(3 × 0.40) + (3 × 0.35) + (3 × 0.25) = 1.20 + 1.05 + 0.75 = 3.00` → **High** (2.70–3.45).

**Controls:** across the 22 items, the sample's answers earn **34 of a possible 51 weighted points** → `34 / 51 = 67%` → **Adequate** (65–84%).

**Residual:** High inherent × Adequate controls → **High** (from the matrix). The tool flags the KEY/STD gaps (e.g., MFA-review timeliness, no SOC 2 from a subprocessor, missing breach-notification SLA) and recommends: *onboard only with a remediation plan and enhanced monitoring.*

---

## Limitations

- A questionnaire result is **self-reported**; weight independent evidence (SOC 2 Type II, pen-test reports, certifications) more heavily. See the [questionnaire reference guide](../README.md).
- The weights and thresholds here are a **defensible default**, not a universal standard — a real program calibrates them to its own risk appetite.
- Illustrative tool on a fictional vendor; all data synthetic.
