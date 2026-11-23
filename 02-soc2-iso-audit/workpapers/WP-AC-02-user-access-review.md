# Workpaper WP-AC-02 — User Access Reviews

| | |
|---|---|
| **Control ID** | AC-02 — User access reviews |
| **Frameworks** | SOC 2 CC6.2, CC6.3 · ISO 27001 A.5.18 · NIST AC-2, AC-6 |
| **Control owner** | IT Manager |
| **Tester** | GRC (internal control testing) |
| **Period tested** | FY2026 (Jan 1 – Oct 31, 2026) |
| **Test date** | 2026-10-12 |
| **Test methods** | Inspection, Reperformance |

## 1. Control description

Access to in-scope production systems and the Console application is reviewed at least quarterly. Reviewers (system/data owners) certify that each user's access remains appropriate or flag it for revocation; revocations are ticketed to IT and completed. The control exists to enforce least privilege over time and detect access that should have been removed.

## 2. Test objective

Determine whether, during the period, access reviews were (a) **performed** for each required quarter, (b) **complete** (covered the full user population), and (c) **acted upon** (flagged access was revoked in a timely manner).

## 3. Population and sampling

| | |
|---|---|
| **Population** | 4 quarterly review campaigns across 3 in-scope systems (Okta, GCP IAM, Console) = 12 campaign instances |
| **Sampling approach** | Test all 4 quarters for each system (full period coverage), then sample users within campaigns for revocation follow-through |
| **User sample** | 25 user-access line items flagged "revoke" across the 4 campaigns, selected judgmentally to cover each quarter and each system |

## 4. Test steps performed

1. **Inspected** the access-governance platform for evidence that a review campaign was launched and closed in each of Q1–Q4 for each in-scope system (completeness of occurrence).
2. **Reconciled** each campaign's user list against an authoritative user export for that quarter to confirm the review covered the full population (completeness of coverage).
3. For the 25 sampled "revoke" decisions, **reperformed** the follow-through: traced each to its revocation ticket and to system evidence that access was actually removed, and measured the time from reviewer decision to removal.
4. **Inspected** reviewer identity to confirm reviews were performed by the appropriate system/data owner (not self-reviewed).

## 5. Results

| Test step | Result |
|---|---|
| Campaigns occurred each quarter (12 instances) | **11 of 12 effective.** Q2 GCP IAM campaign was launched 5 weeks late (started 2026-05-09 for the quarter ending 2026-03-31). |
| Campaign covered full population | Effective — sampled campaigns reconciled to the user export with no omitted users. |
| Revocations completed (25 sampled) | **22 of 25 effective.** 3 revocations completed 9–14 days after the reviewer decision, exceeding the 7-day internal target. |
| Appropriate reviewer | Effective — no self-reviews identified. |

## 6. Exceptions noted

- **EX-1 (timeliness of occurrence):** The Q2 GCP IAM access review was performed 5 weeks after quarter-end. For 5 weeks the quarterly review did not occur on schedule for one in-scope system.
- **EX-2 (timeliness of action):** 3 of 25 sampled revocations (12%) were completed outside the 7-day internal SLA (9–14 days). Access was ultimately removed in all cases; no evidence the retained access was used.

## 7. Root cause (per discussion with control owner)

Both exceptions trace to the same cause: access reviews and revocation follow-up were **manually coordinated by one analyst** with no automated reminder or SLA tracking. When that analyst was out, the Q2 campaign slipped, and revocation tickets were not consistently chased to closure within SLA.

## 8. Conclusion

**Control AC-02: Exception noted.** The control is appropriately designed but did **not operate effectively throughout the period** — there was a gap in occurrence (Q2) and in operating timeliness (revocation SLA). The deficiency is assessed as a **control deficiency**, not a significant deficiency: coverage was complete, all flagged access was eventually removed, and there is no evidence of misuse. Rated **Medium** in the readiness assessment (finding **F-05**).

## 9. Remediation recommended

1. Move access-review scheduling and revocation tracking into the GRC platform with automated reminders and SLA timers, removing the single-analyst dependency. *(This is the exact use case built in [Project 3 — GRC Automation](../../03-grc-automation/).)*
2. Add a secondary reviewer/backstop so a campaign cannot slip when one person is unavailable.
3. Add a monthly check on open revocation tickets approaching the 7-day SLA.

## 10. Cross-references

- Evidence: PBC-005 (`evidence-tracker.csv`)
- Finding: F-05 (`audit-readiness-assessment.md`)
- Related control: AC-03 Joiner/Mover/Leaver (shares the deprovisioning timeliness theme; see F-05 note)
