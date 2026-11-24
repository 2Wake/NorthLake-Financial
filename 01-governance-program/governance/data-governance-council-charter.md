# Empire City Taxi — Data Governance Council Charter

*Fictional charter for the ECT portfolio. All people are invented. Status: **DRAFT v0.1**, pending review.*

## 1. Purpose

The Data Governance Council is ECT's decision-making body for data. It:
- resolves disputes between departments over data ownership, classification, access, quality and definitions;
- approves data standards and policy exceptions;
- accepts or rejects data risk on the company's behalf.

The council exists because the right answer often depends on balancing **two legitimate business interests**, such as marketing insight and privacy. That balance should be struck openly, by accountable people, and written down.

## 2. Authority

The council is chartered by the CEO and led by the CDO. Its decisions are binding on all departments, subject to the escalation path in §7. The council **approves** the following:
- [Data Classification Standard](data-classification-standard.md)
- [Labeling Standard](labeling-standard.md)
- [Data Ownership Model](data-ownership-model.md)
- Business glossary definitions
- Exceptions to any of the above

## 3. Membership

People are named in the [Governance Organization](governance-org-structure.md).

| Seat | Holder | Vote |
|---|---|---|
| **Chair** | Renée Okonkwo, CDO | Votes; breaks ties |
| **Secretary** | Jordan Ellis, Data Governance Manager | Non-voting. Runs the agenda, minutes, issue register and KPIs |
| Domain owners | Hannah Cho (Rider), Keisha Monroe (Driver Ops), Luis Ortega (Operations), Thomas Brennan (Finance), Simone Laurent (People), Derek Sullivan (Marketing) | Vote |
| Security | Victor Hale, CISO | Votes; **security veto** |
| Privacy | Priya Raman, Privacy Officer | Votes; **privacy veto** |
| Advisors | Mateo Silva (Platform/SRE), Aisha Karim (Data & Analytics), Robert Feld (General Counsel) | Non-voting |

Data stewards attend when an item in their domain is on the agenda.

## 4. Meetings

| | |
|---|---|
| Cadence | Monthly, first Tuesday, 60 minutes |
| Ad-hoc session | Within **5 business days** for any Critical issue (§6) |
| Quorum | The Chair (or a delegate) **plus** a majority of voting members. **The CISO or Privacy Officer must be present** when any Secret or Confidential matter is decided. |
| Agenda | Circulated by the Secretary 3 business days ahead (template in §9) |
| Minutes | Published within 2 business days to `governance/council/minutes/YYYY-MM.md` |

## 5. Decision rules

1. **Consensus first.** The Chair seeks agreement after hearing each affected department.
2. **Vote if needed.** A simple majority of voting members present. The Chair breaks ties.
3. **Vetoes.** The CISO may veto on security grounds and the Privacy Officer on privacy or legal grounds. A veto must be justified in the minutes, and it escalates the matter to the CDO for a final decision. The CDO decides after hearing the vetoing member and the affected owners, and records the reasoning in the decision log.
4. **Conflict of interest.** An owner whose own domain is in dispute presents the case but **does not vote** on it.
5. **Every decision is recorded** with the following, in the decision log (`GOV-D-###`):
   - the options considered
   - the rationale
   - the decision owner
   - an action owner and due date
   - a review date

## 6. Issue lifecycle

Every governance issue gets an ID (`GOV-###`) in the issue register and moves through six stages:

```
Identify ─► Assign ─► Assess ─► Decide ─► Remediate ─► Validate ─► Closed
```

| Stage | Who | What happens |
|---|---|---|
| **Identify** | Anyone (often an automated check, a steward, or an analyst) | Issue logged with evidence: query, test result, screenshot |
| **Assign** | Data Governance Manager | Accountable owner and responsible steward named; severity set |
| **Assess** | Steward + affected departments | Business impact, regulatory implications, options |
| **Decide** | Data owner, or the **council** if departments disagree or risk exceeds the owner's authority | Decision logged (`GOV-D-###`) |
| **Remediate** | Action owner (usually the custodian or steward) | Technical or process fix |
| **Validate** | Data Governance Manager | Fix confirmed with evidence (e.g. the test now passes); issue closed |

**Severity and targets:**

| Severity | Example | Decision by |
|---|---|---|
| Critical | Secret data exposed; legal deadline at risk | Ad-hoc council within 5 business days |
| High | Confidential data mis-classified; finance doesn't reconcile | Next monthly council |
| Medium | Missing owner or steward; definition conflict | Data owner within 30 days |
| Low | Missing description; naming inconsistency | Steward within 60 days |

## 7. Escalation path

```
Data Steward ─► Data Owner ─► Data Governance Manager ─► Council ─► CDO (final)
```

The CDO is the **final escalation point** as leader of the data organization. The CDO's decision on an escalated matter is final, and it is reported to the CEO in the quarterly governance report.

Issues escalate when:
- departments disagree;
- the decision exceeds the owner's authority (e.g. accepting risk on Secret data);
- a target date is missed; or
- a veto is used.

## 8. Decision rights (RACI)

R = Responsible · A = Accountable · C = Consulted · I = Informed

| Decision | Council | CDO | Data Owner | Steward | DG Manager | CISO | Privacy | Custodian | Analytics |
|---|---|---|---|---|---|---|---|---|---|
| Classify or reclassify a column | I | I | **A** | R | C | C | C | I | I |
| Disputed classification | **A** | R | C | C | R | C | C | I | I |
| Grant access to **Secret** data | I | I | **A** | C | I | R | C | R | I |
| Grant access to **Confidential** data | — | — | **A** | C | I | C | C | R | I |
| Accept data risk (owner's domain) | I | I | **A** | C | R | C | C | I | — |
| Accept risk on Secret data or across domains | **A** | R | C | C | R | C | C | I | — |
| Approve or change a glossary definition | I | — | **A** | R | C | — | — | — | C |
| Resolve a definition conflict between domains | **A** | R | C | C | R | — | — | — | C |
| Policy or standard exception | **A** | C | R | C | R | C | C | I | I |
| Approve or change a data standard | **A** | R | C | C | R | C | C | I | I |
| Retention vs. deletion conflict | **A** | C | C | C | R | C | **R** | R | I |
| Onboard a new data source | I | I | **A** | R | C | C | C | R | I |

## 9. Standing agenda

1. Decisions and actions from last meeting: status
2. **KPI review** (§10)
3. New Critical and High issues
4. Decisions requested: one item at a time (steward presents, departments respond, decide)
5. Exceptions due for review
6. Any other business

## 10. Governance KPIs

Reported monthly by the Data Governance Manager, mostly measured automatically from BigQuery and the catalog.

| KPI | Target |
|---|---|
| Tables with owner and steward labels | 100% |
| Secret and Confidential columns correctly classified (vs. the column map) | 100% |
| Tables and columns with descriptions | ≥ 90% |
| Data-quality test pass rate | ≥ 98% |
| Open Critical/High issues older than target | 0 |
| Quarterly access reviews completed on time (Secret, Confidential) | 100% |
| Data subject requests closed within the legal deadline | 100% |

## 11. Initial issue backlog

These six disputes are planned for the council's first sessions. Each is backed by a defect **planted in the data**, so detection, decision and remediation can be shown end to end.

| ID | Issue | Departments | Planted evidence |
|---|---|---|---|
| GOV-001 | Rider deletion requests vs. marketing's historical segments | Privacy vs. Marketing | Deleted riders still present in segment and campaign tables |
| GOV-002 | Driver payouts don't reconcile with trip revenue | Finance vs. Operations | Payout totals differ from completed-trip fares for some drivers |
| GOV-003 | Classification of precise rider location data | Marketing vs. Governance and Security | Location columns tagged Internal in some tables |
| GOV-004 | Terminated employees still active as drivers | People vs. Driver Ops | HR shows terminated; fleet shows active driver and vehicle |
| GOV-005 | Two definitions of "revenue" | Finance vs. Operations | Conflicting calculations in ledger and fare tables |
| GOV-006 | Analyst request for row-level rider data | Analytics vs. Security | Access request on file; the masked alternative exists |

## 12. Review of this charter

Reviewed annually by the council. Amendments need a two-thirds majority of voting members.
