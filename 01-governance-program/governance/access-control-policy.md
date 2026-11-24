# Access Control Policy (warehouse)

**Owner:** Chief Information Security Officer (`ciso`) · **Steward:** Risk Data Steward (`risk-data-steward`) · **Status:** Draft v0.1 (2026-11-24)

Who may use which BigQuery dataset, who approves it, and how access is reviewed. The machine-readable
version is the **access policy matrix**, [`data-platform/dbt/seeds/governance/access_policy.csv`](../../data-platform/dbt/seeds/governance/access_policy.csv).
The generator issues grants from it, and the ACC checks test grants against it.

## Principles

1. **Least privilege by layer.** `raw` holds Secret data (SSNs, card numbers, bank accounts), so only custodians and a few named roles get it. Analysts work on `marts`, which is capped at Sensitive.
2. **Access follows the role, not the person.** Each employee has one access role. A role grants a fixed set of datasets.
3. **Approval by the accountable owner, never by yourself.** If the policy's approver is the requester, the request escalates (to the CDO, or to the CEO for the CDO).
4. **Time-bound for exceptions.** Security's `raw` access is per investigation, for at most 14 days.
5. **Joiner / mover / leaver.** Access is granted after hire, removed when someone leaves, and removed and re-requested when someone changes department.

## Access policy matrix

| Access role | Who | raw | staging | marts | Approver |
|---|---|---|---|---|---|
| `platform_admin` | Platform / SRE, data engineers (custodians) | admin | admin | admin | CISO |
| `analytics_engineer` | Analytics engineers | read | write | write | CISO (raw), Head of D&A |
| `data_analyst` | Data & Analytics analysts | **none** | none | read | Head of D&A |
| `domain_analyst` | Analysts in a business department | none | none | read (own domain) | Domain owner |
| `data_steward` | Domain data stewards | none | read (own domain) | read | Domain owner / Head of D&A |
| `security_analyst` | Security team | read, **14 days max** | read | read | CISO |
| `privacy_analyst` | Privacy team | read (rider) | read (rider) | read | Privacy Officer |
| `governance_admin` | Data Governance team | none | read | read | CDO |
| `executive` | Leaders | none | none | read | CDO |
| `business_user` | Everyone else (incl. support, engineers, drivers) | none | none | none | n/a |

## Access checks (ACC rules)

Run daily in dbt (`marts.fct_dq_findings`, dimension *Access*). Each is a warning test.

| Rule | Check | Planted scenario |
|---|---|---|
| ACC-01 | Every active grant is allowed by the matrix | Analyst granted `raw` by her manager |
| ACC-02 | Leavers have no active access | Offboarding missed the revocation |
| ACC-03 | Movers' old-department access is removed | Privilege creep after a transfer |
| ACC-04 | Nobody approved their own access | Separation-of-duties breach |
| ACC-05 | Time-bound access ends at its expiry date | Investigation access never removed |
| ACC-06 | Every grant has an approval and a ticket | Access granted outside the process |
| ACC-07 | The approver is the role the matrix names | Approved by the wrong person |

Findings are scored against the generator's answer key in `marts.fct_dq_scorecard`, like the DQ rules.

## User access review

`marts.fct_access_grants` lists current access with names, departments and approvers. Quarterly, each
domain owner reviews the grants to their domain and the CISO reviews `raw` (to be scheduled through the council).

## Enforcement (real)

The simulated grants above are data. A small set of **real role service accounts** will prove the policy in
BigQuery itself (for example, an analyst account that is denied `raw`). Their setup is done by the owner in the
Google Cloud console; see the WORKLOG.
