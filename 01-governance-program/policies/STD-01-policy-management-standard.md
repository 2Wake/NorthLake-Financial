# STD-01 Policy Management Standard

> **Read-only copy.** The official version is the Confluence page *STD-01 Policy Management Standard* in the Empire City Taxi Governance space (ECTG, page 327917). If the two differ, Confluence prevails (section 11). Copied at v1.0 on 2026-11-24.

**Status: APPROVED v1.0.** Approved by Victor Hale, CISO, on November 24, 2026. Next review due November 24, 2027. Tracked in Jira GOV-22 (draft) and GOV-24 (review and approval).

## Document control

| Document ID | STD-01 |
| --- | --- |
| Title | Policy Management Standard |
| Version | 1.0 |
| Status | Approved |
| Owner | Victor Hale, Chief Information Security Officer |
| Approver | Victor Hale, Chief Information Security Officer |
| Author | Jordan Ellis, Data Governance Manager (with Elena Popescu, GRC Analyst) |
| Reviewers | Elena Popescu, GRC Analyst; Robert Feld, General Counsel |
| Approval date | November 24, 2026 |
| Effective date | November 24, 2026 |
| Next review date | November 24, 2027 |
| Classification | Internal |

## 1. Purpose

This standard sets out how Empire City Taxi Co. (ECT) writes, reviews, approves, publishes, reviews again and retires its governance documents. It makes sure every policy has a clear owner, is approved by someone with the authority to approve it, is kept current, and can be shown to an auditor with evidence.

## 2. Scope

This standard applies to all ECT information security, privacy and data governance documents: policies, standards and procedures. It applies to everyone who writes, reviews, approves or maintains them.

## 3. Document types

| Type | What it says | Example | Approved by | Review cycle |
| --- | --- | --- | --- | --- |
| **Policy** (POL-xx) | *What* ECT requires and *why*. Short and stable. | POL-02 Access Control Policy | Accountable executive (owner); POL-01 by the CEO | At least every 12 months |
| **Standard** (STD-xx) | Specific, mandatory rules that support a policy (settings, timeframes, formats). | STD-01 Policy Management Standard | Owner of the parent policy, or the CISO | At least every 12 months |
| **Procedure** (PRC-xx) | Step-by-step *how* a task is done. | Leaver access removal procedure | Department head responsible for the task | At least every 12 months, or when the process changes |
| **Supporting document** (DOC-xx) | Records that policies rely on, such as scope statements and inventories. | DOC-01 PCI DSS Scope & Cardholder Data Flow | As set in the document | As set in the document (PCI scope: every 12 months) |

Guidelines (optional advice) may be published but are not governed by this standard.

## 4. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| **Chief Information Security Officer (CISO)** | Owns this standard and the policy program. Resolves disputes over ownership. Reports policy status to the executive team. |
| **Policy owner** | The accountable executive named in the Policy Register. Makes sure the document is accurate, followed and reviewed on time. Approves the document unless another approver is named. |
| **Approver** | Has authority to make the document binding (see section 8). Records approval in the document control table. |
| **Author** | Usually a data steward or subject-matter expert. Drafts the document from the template and updates it after review. In ECT's federated model, stewards propose and owners approve. |
| **Reviewers** | Subject-matter experts and affected departments. Check accuracy and workability, and record comments on the page. |
| **Policy administrators** (Data Governance Manager and GRC Analyst) | Maintain the Policy Register and template, track review dates, chase overdue reviews, and keep the repository copy in sync. |
| **All staff and contractors** | Read and follow the policies that apply to them, and acknowledge them when asked. |

## 5. Numbering and naming

- Each document gets a permanent ID made of its type prefix and a two-digit number (POL-01, STD-01, PRC-01, DOC-01). IDs are never reused, even after a document is retired.
- Page titles use the format `ID Title`, for example `POL-02 Access Control Policy`.
- The Policy Register is the master list of IDs.

## 6. Versioning

| Version | Meaning |
| --- | --- |
| 0.1 – 0.8 | Draft, being written |
| 0.9 | Review complete, waiting for approval |
| 1.0 | First approved version |
| 1.1, 1.2 … | **Minor change**: wording, links, names or formatting that does not change any requirement. The owner approves; no full review needed. |
| 2.0, 3.0 … | **Major change**: any change to a requirement, scope, timeframe or responsibility. Goes through the full lifecycle again. |

Every version is listed in the document's change history. Confluence page history keeps earlier versions.

## 7. Lifecycle

| Status | Entry criteria | Exit criteria |
| --- | --- | --- |
| DRAFT | Page created from the template; register row added. | All template sections complete; author requests review. |
| IN REVIEW | Named reviewers notified. | Every comment resolved (accepted, or rejected with a reason); version set to 0.9. |
| APPROVED | Approver records approval (name, date, version) in document control and on the page. | A major change starts (back to Draft), or the document is retired. |
| RETIRED | Owner approves retirement and names any replacement. | None. The page is moved to an archive and kept for 7 years. |

## 8. Approval authority

- **POL-01 Information Security Policy:** approved by the CEO.
- **Other policies:** approved by the policy owner named in the register. Where a policy has two owners (for example Finance and Security), both must approve.
- **Standards:** approved by the owner of the parent policy, or by the CISO.
- **Procedures:** approved by the department head responsible for the process.
- Nobody may approve a document they wrote. If the owner is also the author, the CISO (or for CISO-authored documents, the CEO) approves.

**Evidence of approval** is required in three places, which must agree: (1) the document control table, (2) a comment from the approver on the page stating "Approved version X.Y", and (3) the Policy Register.

## 9. Review

- Every document is reviewed at least every **12 months** after its approval date. The next review date is set when the document is approved.
- A review is also required, without waiting, after any of these: a significant incident; an audit or assessment finding; a new law, regulation or contract requirement; a major change to systems or organization; a change in PCI DSS scope.
- A review that finds no changes is still recorded: the owner confirms it in the change history and the next review date moves forward 12 months.
- A document is **overdue** when today is after its next review date. Policy administrators report overdue documents to the CISO monthly and to the Data Governance Council at each meeting.

## 10. Exceptions

- Anyone who cannot meet a requirement must request an exception *before* the non-compliance, or as soon as it is discovered.
- Requests are raised in Jira (project GOV) and must state: the document and clause, the reason, the risk, any compensating controls, and the end date.
- Exceptions are approved by the policy owner. Exceptions rated high risk under the Risk Management Policy also need the CISO.
- Exceptions last at most **12 months** and must be renewed to continue. All exceptions are recorded in the exception log.
- Internal exceptions cannot waive legal, regulatory or PCI DSS requirements. Alternatives to a PCI DSS requirement must follow the PCI DSS compensating-control process.

## 11. Publication and communication

- The **official copy** of every document is its page in the Confluence space *Empire City Taxi Governance* (ECTG).
- A read-only copy of each approved document is kept in the ECT GRC repository. If the two differ, the Confluence page prevails and the difference is corrected.
- New and changed policies are announced to affected staff within 10 business days of approval. Staff acknowledge the policies that apply to them at hire and once a year, as set in the Acceptable Use and HR Security policies.

## 12. Compliance

Compliance with this standard is checked through the Policy Register (approval and review status). Failure to follow ECT policies may lead to disciplinary action, as set in the HR Security Policy.

## 13. Related documents

- POL-01 Information Security Policy
- [Policy Template](policy-template.md)
- Policy Register (Confluence; data copy in `data-platform/dbt/seeds/governance/policy_register.csv`)
- POL-06 Risk Management Policy (risk ratings for exceptions)

## Change history

| Version | Date | Author | Change | Approved by |
| --- | --- | --- | --- | --- |
| 0.1 | November 24, 2026 | Jordan Ellis | First draft | — |
| 1.0 | November 24, 2026 | Jordan Ellis | Reviewed and approved with no changes to the requirements in v0.1. Status set to Approved; approval, effective and next review dates recorded. | Victor Hale, CISO |
