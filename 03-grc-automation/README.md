# Project 3 — GRC Automation *(planned)*

Turns Empire City Taxi's manual, point-in-time control operation into continuous assurance — directly addressing the root cause behind findings F-01, F-02, and F-05 in the [readiness assessment](../02-soc2-iso-audit/audit-readiness-assessment.md).

**Planned contents**
- **Evidence collectors** — Python scripts that pull synthetic "evidence" (access exports, config snapshots, scan results) on a schedule and write it to the evidence tracker, with timestamps and hashes.
- **Control-drift monitor** — checks a control's current state against its expected state (e.g., TLS policy, MFA coverage, access-review timeliness) and raises an issue when it drifts.
- **Access-review SLA tracker** — the automation that would have prevented the Q2 slip and the late revocations in WP-AC-02.
- **A small CLI / report** — produces a continuous-compliance snapshot from the collectors.

Scripting: Python (standard library + Faker for synthetic inputs). No real systems are touched.
