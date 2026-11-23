# SOC 2 Type II — Audit Readiness Assessment

**Entity:** NorthLake Financial (fictional) · **Prepared by:** GRC · **Date:** 2026-10-15
**Scope:** Security, Availability, Confidentiality (TSC) · **Period:** FY2026 (Jan 1 – Oct 31, 2026)

## Purpose

An internal, honest assessment of whether NorthLake's control environment is ready for the external SOC 2 Type II examination. It rolls up the control matrix, the evidence tracker, and the testing workpapers into a findings list with severity and remediation, and gives leadership a go/no-go view.

## Readiness summary

| Metric | Value |
|---|---|
| Controls in scope | 26 |
| Fully implemented | 20 |
| Partially implemented | 5 |
| Not started | 1 |
| Controls tested this cycle | 12 (sample) |
| Controls effective | 7 |
| Controls with exceptions | 4 |
| Controls not yet testable | 1 (DP-02) |
| Evidence items (PBC) collected | 24 of 26 |

**Overall readiness: _Conditional._** The core security controls (access, encryption, logging, change, incident response, vendor risk) are implemented and largely effective. Readiness is held back by a cluster of **data-lifecycle and operating-timeliness gaps**. None rises to a material weakness, but the open findings should be remediated or have a credible remediation plan before the Type II window closes, since Type II tests operating effectiveness *over time*.

## Findings

Severity: **Critical** (likely report qualification / material) · **High** (significant deficiency risk) · **Medium** (control deficiency) · **Low** (improvement).

### F-01 — Data retention/disposal control not implemented; classification coverage incomplete · **High**
- **Controls:** DP-02 (Not started), DP-01 (Partially implemented, 78% tag coverage)
- **Issue:** There is no operating data retention and secure-disposal control (DP-02), and data classification tagging in the catalog covers only 78% of in-scope datasets. Confidentiality commitments depend on both.
- **Impact:** DP-02 cannot be tested at all this period; a control that does not exist cannot be attested. DP-01 gaps weaken reliance on classification-driven access and handling.
- **Remediation:** Define and implement a retention schedule with automated purge jobs; drive classification tag coverage to ≥95%. Owner: GRC Lead. Target: before Type II window close.

### F-02 — Vulnerability remediation SLA missed in two months · **High**
- **Control:** VM-01 (Partially implemented)
- **Issue:** Critical-severity remediation exceeded the 15-day SLA in 2 of the period's months (PBC-015).
- **Impact:** Operating-effectiveness exception on a core security control; recurring misses risk a significant-deficiency conclusion.
- **Remediation:** Add SLA dashboards and escalation; risk-accept exceptions with documented expiry where remediation is genuinely blocked. Owner: Security Eng. Target: 30 days.

### F-03 — Privileged access management rollout incomplete · **Medium**
- **Control:** IA-02 (Partially implemented)
- **Issue:** PAM (JIT elevation, session recording) is deployed for part of the environment; standing admin access remains in some GCP projects (PBC-008).
- **Impact:** Privileged-access evidence is incomplete; control not fully testable.
- **Remediation:** Complete PAM rollout across all production projects; eliminate standing admin. Owner: Security Eng. Target: 60 days.

### F-04 — DR failover test only partially completed · **Medium**
- **Control:** BC-01 (Partially implemented)
- **Issue:** The annual regional failover test was partially executed; full RTO/RPO validation not evidenced (PBC-019).
- **Impact:** Availability commitment not fully demonstrated for the period.
- **Remediation:** Complete a full failover test with documented RTO/RPO results. Owner: Platform/SRE. Target: next DR window.

### F-05 — Access-review occurrence and revocation timeliness · **Medium**
- **Controls:** AC-02 (and related AC-03)
- **Issue:** Per [WP-AC-02](workpapers/WP-AC-02-user-access-review.md): Q2 GCP IAM review ran 5 weeks late; 3 of 25 sampled revocations exceeded the 7-day SLA; and 2 of 15 terminations (AC-03) were disabled >24h.
- **Root cause:** Manual, single-analyst coordination with no automated reminders or SLA tracking.
- **Impact:** Operating-effectiveness exceptions on access controls; all access ultimately removed, no evidence of misuse → control deficiency, not significant.
- **Remediation:** Automate review scheduling and revocation SLA tracking ([Project 3](../03-grc-automation/)); add a backup reviewer. Owner: IT Manager + GRC. Target: 45 days.

### F-06 — Security awareness completion below target · **Low**
- **Control:** HR-01
- **Issue:** Annual training completion at 91% vs. 95% target (PBC-026).
- **Remediation:** Chase remaining staff; enforce completion before system access renewal. Owner: People Ops. Target: 30 days.

## Theme across findings

Four of six findings (F-01, F-02, F-05, and partly F-03/F-04) share one root cause: **manual, point-in-time control operation** that slips without automated scheduling, reminders, and SLA tracking. This is precisely the problem [Project 3 — GRC Automation](../03-grc-automation/) addresses by moving evidence collection and control monitoring to a continuous, API-driven model. The readiness gaps are less about missing controls than about **operating them reliably over time** — the exact thing Type II tests.

## Recommendation to leadership

Proceed toward the Type II examination, but treat **F-01 and F-02 as gating**: a retention control must exist and vulnerability-SLA performance must stabilize before the observation window closes, or the report risks exceptions on confidentiality and security. F-03–F-06 should carry documented remediation plans with owners and dates (above).
