# Empire City Taxi GRC — Work Log

Running log of all work, decisions and open items. It's the source for progress summaries and status updates. Newest entries at the top. Updated after every meaningful step (see [`CLAUDE.md`](CLAUDE.md)).

---

## 📋 Backlog

- [x] **Phase 0: generator framework.** Built, tested, and backfilled into `raw` (2026-01-01 → 2026-11-23).
- [ ] **Reference-data issue:** raise REF-01 to REF-03 as a governance issue (reference domain owner: Data Governance Manager) in the issue register.
- [ ] **Remediate the classification scenarios** (S01–S12) through the council process, starting with GV-003 (S01). Watch KPI #2 rise from 72.5%.
- [ ] **Push classifications out:** Collate column tags from the register; optionally BigQuery policy tags on Secret columns (UI, user).
- [ ] **Table and column descriptions.** Raw-table schema files, plus dbt `.yml` with `persist_docs`. Leave about 10–15% blank on purpose, tracked in a documentation-gap register, and fill them in a later remediation sprint.
- [ ] **Labels on tables:** applied in code on `raw`, `staging` and `marts`. **Remaining:** planted label gaps, tracked in the gap register.
- [ ] **Council operations.** Issue register (`GV-###`) and decision log (`GV-D-###`) as dbt seeds; minutes in `governance/council/minutes/`.
- [ ] **Phases 1–4 tables** (see the 2026-11-23 design review entry below).
- [x] **GitHub Actions daily refresh:** live since 2026-11-24. Runs daily at 05:30 New York, keyless, and writes run records to `data-platform/run-records/`.
- [ ] **Access control:** simulated access live (ACC-01–07). The 79 unclassified new columns stay as an audit finding (don't fix). Real role accounts and the daily access check built (2026-11-24); access logs come with Phase 2.
- [x] **Atlassian (Jira + Confluence):** site, MCP and docs/tickets split all done (2026-11-24).
- [ ] **Policy set (SOC 2 + ISO 27001 + PCI DSS) + policy register:** tracked in Jira epic GOV-1. Then a **Common Control Framework** (CCF) as dbt seeds mapping policies → controls → frameworks → automated checks.
- [ ] **DQ rule ownership:** add `proposed_by` (steward), `approved_by` (owner) and `approval_status` to `dq_rules.csv`. The 23 current rules are hub-drafted proposals awaiting steward and owner sign-off.
- [ ] **Council roles and responsibilities (federated model):** flesh out each council member's duties, decision rights and time commitment; hub vs. domain (spoke) responsibilities; steward duties including DQ rule authoring.
- [ ] **Collate:** sign up, connect to BigQuery read-only, evaluate its AI settings.
- [ ] **Knowledge Catalog:** free-tier discovery and glossary only; compare it with Collate.
- [ ] **Clean up merged branches** on GitHub (`five-tier-classification`, `governance-council`). The user asked to keep them for now.

---

## 2026-11-24 — 6 follow-up tickets created (GOV-75 to GOV-80)

### Done
Owner approved all 6 drafts. Created as Tasks with no epic:
- **GOV-75** Security incident reporting channel. Blocks GOV-55 (POL-01) and GOV-62 (POL-08).
- **GOV-76** Approved tools list (software and AI, by data tier). Blocks GOV-59 (POL-05).
- **GOV-77** Protect `main` with a GitHub ruleset (owner UI change; it's the POL-07 5.9 change record).
- **GOV-78** Retire the repo `access-control-policy.md` (pointer to POL-02).
- **GOV-79** Line up ACC-02/ACC-03 with POL-02's 24-hour and 5-day deadlines.
- **GOV-80** Move the Classification and Labeling standards to Confluence as STD-02 and STD-03.

### Risks
- PR #3 was created with the blank template, not the prepped description, so it didn't meet POL-07 5.3 (description complete at creation). It's closed unmerged and replaced by a new PR from the prepped link. This is the first recorded use of the control catching a miss.

---

## 2026-11-24 — POL-07 small-team allowance rewritten for one maintainer; PR #2 reviewed

### Done
- **PR #2** (created by the owner, the first under the new rule) reviewed by Claude as a PR comment: ready to merge.
- **POL-07** (page v3, still document v0.9), owner change after review:
  - The section 6 small-team allowance now describes the real flow: PR drafted by the author or Claude; the maintainer creates it; Claude posts a written review before merge; the maintainer merges (the merge is the approval); every use counts in the quarterly sample. It's labeled a compensating control, not separation of duties, and still never covers IAM, security or cardholder-data changes.
  - 5.3 now requires the PR description at creation.
  - The gaps panel says PRs started with PR #1.
  - Noted in the 0.9 change-history row and in a GOV-10 comment for the approver.

### Decisions
- No simulated re-review: it's an owner change, flagged for the approver (GOV-61) instead, the same way DOC-01's in-cab addition was handled.

---

## 2026-11-24 — Pull-request workflow; council IDs renamed GOV → GV

### Done
- **Council IDs renamed** at the owner's request: issues `GOV-###` → `GV-###`, decisions `GOV-D-###` → `GV-D-###` (charter, classification register, CLAUDE.md, this log). The charter now says why: `GV` is the council register, `GOV` is the Jira project. No Confluence page or Jira ticket used the old IDs (searched).
- **Pull-request workflow** (owner decision): every change reaches `main` through a PR. **Refined the same day (owner chose option 2): Claude preps the PR and gives a pre-filled link; the owner clicks Create.** PR #1 was opened by Claude before this refinement. Each PR gets a full description at creation (new `.github/pull_request_template.md`, aligned with POL-07: change type, DOC-01 scope check, testing, rollback) and posts a review comment. CLAUDE.md agreement #3 and memory updated.

### Decisions
- **Claude can review but not approve in GitHub.** Claude acts through the owner's account (2Wake), and GitHub blocks authors from approving their own PRs. So the owner is the approver (by merging or explicitly telling Claude to merge). An AI review is evidence a review happened; it isn't segregation of duties between two people. That's the honest compensating control for a one-person repo.

### Next steps
- POL-07's small-team allowance should describe this workflow before approval (owner to confirm).
- Proposed tickets (incl. protecting `main` with a ruleset, owner UI change), then the audit findings.

---

## 2026-11-24 — Policies POL-01 to POL-08 drafted and reviewed to v0.9 (parallel)

### Done
- New Confluence folder **Policies** (458802) under Policy Management.
- **POL-01 Information Security Policy** (491531) written first as a v0.1 frame, so the 7 topic policies could cite it. Then 7 parallel agents each drafted one policy from the approved template, ran its simulated review (dated today, marked [Simulated], ≥1 accepted and ≥1 rejected-with-reason) and closed its draft + review sub-tasks with closing comments.
  | ID | Page | Story | Approval sub-task |
  |---|---|---|---|
  | POL-01 Information Security | 491531 | GOV-4 | GOV-55 (CEO) |
  | POL-02 Access Control | 557061 | GOV-5 | GOV-56 |
  | POL-03 Data Classification & Handling | 426094 | GOV-6 | GOV-57 |
  | POL-04 Cardholder Data Protection | 557113 | GOV-7 | GOV-58 (CFO + CISO) |
  | POL-05 Acceptable Use | 426073 | GOV-8 | GOV-59 (VP People + CISO) |
  | POL-06 Risk Management | 557136 | GOV-9 | GOV-60 |
  | POL-07 Change Management | 557087 | GOV-10 | GOV-61 |
  | POL-08 Incident Response | 458805 | GOV-11 | GOV-62 |
- POL-01 v0.2 folded in the agents' findings (card data → POL-04, risk acceptance roles, yearly acknowledgment, security reporting channel, change management, monitoring notice, CFO/GC roles, POL-04 exceptions need CFO+CISO, links). Leadership review (GOV-40) → v0.9: accepted classification-drives-controls and lawful monitoring with §52-c notice; rejected CDO co-ownership (one accountable owner, STD-01 s8). GOV-25, GOV-40 Done.
- Register page v6 + extract: POL-01 to POL-08 `in_review`, 0.9, page IDs.
- Approval sub-tasks (GOV-55 to GOV-62) untouched, waiting for the owner.

### Decisions
- Draft the umbrella first, approve it first or same day (owner agreed). Shared files (register, CSV, WORKLOG, git) kept with the main session so parallel agents can't collide.

### Found (audit material; not fixed)
- No security incident reporting channel exists (POL-01 s7, POL-08 s1 point to it). Blocks approval of POL-01 and POL-08.
- No approved tools list (software/AI by data tier) for POL-05. Blocks GOV-59.
- POL-07 walk-through: today's merges went straight to `main` (no PR, no second reviewer); `main` has no branch protection; console changes recorded only in WORKLOG.
- SOC 2 control matrix marks IR-01/IR-02 "Implemented" but no IR plan exists; evidence tracker PBC-002 says Q1–Q4 risk register exports "Collected" but no register exists.
- Council charter's issue IDs clashed with Jira GOV keys. **Resolved 2026-11-24 at the owner's request:** council IDs renamed to `GV-###` / `GV-D-###`.
- Card-data stewardship unclear (register says Rider steward, table owner label is CFO); referred to council in POL-03.
- `01-governance-program/governance/access-control-policy.md` superseded by POL-02; ACC-02/ACC-03 have no 24h / 5-day allowance matching POL-02 s6–7.
- Classification & Labeling standards still repo-only (DRAFT v0.1); proposed to move to Confluence as STD-02/STD-03.

### Next steps
- Owner decides on proposed tickets, then approvals in order: POL-01 (CEO) first.

---

## 2026-11-24 — GOV-2 closed: DOC-01 approved v1.0; observations story GOV-70

### Done
- **DOC-01 approved v1.0** *[Simulated]*: CFO consulted comment (Confluence 458789), CISO "Approved version 1.0" comment (491527) with next scope confirmation 2027-11-24 and scope-reduction ideas as follow-ups. Page v4: banner, version, status, approval date, next confirmation, 1.0 change-history row, section 5 links to GOV-70–74. Register page v5 + extract: `approved,1.0,2026-11-24,2027-11-24`.
- **GOV-70 (Story, not under an epic; owner decision)** "PCI scope observations: plan remediation by policy", linked Relates → GOV-2 and to DOC-01. Sub-tasks bucketed by governing policy:
  - GOV-71 encryption (obs. 1, POL-11/GOV-14)
  - GOV-72 access need-to-know (obs. 2, POL-02/GOV-5)
  - GOV-73 retention & disposal (obs. 3, 5, POL-13/GOV-16)
  - GOV-74 card-data location inventory (obs. 4, POL-04/GOV-7)
- Closing comments posted, then Done: **GOV-21**, **GOV-2** (GOV-2's comment lists all 5 observations with their sub-task, plus the 3.5 unknowns).

### Decisions
- Section 3.5 unknowns (processor, app TLS, in-cab provider) are questions, not remediation: they stay with GOV-15, not GOV-70.
- Observations stay unremediated until their governing policy is approved (audit material).

### Risks
- GOV-73: `raw` is append-only by design, which conflicts with deleting expired card data. Needs a design decision when POL-13 is written.

---

## 2026-11-24 — DOC-01 in-cab payments added; atlassian-setup merged to main

### Done
- **DOC-01** (page v3, still document v0.9): owner asked to add in-cab card payments. Added to 3.5 *Not yet known* (provider, path, whether card data returns to ECT; Finance to confirm, vendor inventory GOV-15), as a second entry point on the data-flow diagram, and as a transfer-table row. Recorded in the 0.9 change-history row as an owner addition after review.
- **Merged `atlassian-setup` → `main`** (owner chose "Claude merges directly"). Fast-forward, no conflicts; main at 3831ec1. The Arjun roster correction (2026-11-24) is now on main before the next daily run (10:30 UTC Nov 25), which is the first run to generate Nov 24.

### Next steps
- Owner approves the drafted story + 4 sub-tasks for the DOC-01 observations (bucketed by policy: encryption, access, retention/disposal, cardholder data inventory).
- GOV-2 closing comment will list observations 1–5 and point to the new story; posted when GOV-21 sign-off is recorded.

---

## 2026-11-24 — How-To's folder: reading DOC-01 and running a PCI scoping exercise

### Done
- New Confluence folder **How-To's** (458756) under the ECTG home.
- **How to read DOC-01 PCI DSS Scope & Cardholder Data Flow** (458759): PCI DSS basics (PAN, CHD vs sensitive authentication data, 12 requirements, QSA vs SAQ) and a plain-language walkthrough of every DOC-01 section, mapping each observation to its PCI requirement and the policy that will handle it.
- **How to run a PCI DSS scoping exercise** (426044): 7-step method (set up → payment channels from Finance → follow the data with 5 questions → discovery scans → classify with decision table → draw and cross-check the flow → review, sign off, re-scope triggers), who does what, and a system-owner questionnaire.

### Risks / gaps found
- Applying the method's "payment channels" step to ECT shows **in-cab card payments are missing from DOC-01** (NYC taxis take cards in the cab, usually through a third-party terminal provider). Flagged to the owner; DOC-01 not yet changed.

---

## 2026-11-24 — GOV-2: DOC-01 PCI DSS scope drafted and reviewed (v0.9)

### Done
- **DOC-01 PCI DSS Scope & Cardholder Data Flow** created in ECTG (page 425996, under the space home). Linked from GOV-2.
  - **Inventory (GOV-19 → Done)** from read-only checks: BigQuery column scan and `pci_scope` labels across raw/staging/marts; current access records; access policy matrix; role service accounts; workflow; local `output/`.
    - In scope: S1 rider app card entry, S2 payments system (simulated by the generator), S3 Actions runner, S4 `raw.payments_rider_cards`, S5 `staging.stg_payments_rider_cards`, **S6 `staging.stg_payments_rider_cards_history`** (not in the ticket's starting list), **S7 laptop `data-platform/output/`** (327 days of full PAN in plain JSONL, 213 MB total, gitignored), S8 Google Cloud, S9 GitHub. Access: A1 `ect-pipeline`, A2 `ect-role-security`, A3 `ect-role-steward`, A4 36 people with raw/staging grants (dataset-level, includes 4 `data_analyst` grants on raw), A5 project owners.
    - Connected-to: C1 repo/workflow, C2 Workload Identity provider, C3 `marts.dim_rider_cards` (the last-4 step), C4 Cloud audit logging (added in review).
    - Out of scope: other marts, DQ/defect tables (IDs only), `ect-role-analyst`, Looker Studio, Atlassian, Collate (not connected; re-assess before connecting).
  - **Data flow (GOV-20 → Done):** text diagram with CDE boundary + transfer/protection table.
  - Observations recorded, not remediated: clear PAN in raw + 2 views; 36 readers via dataset-level access; laptop PAN files with no retention; S6 previously untracked; 3y retention label pending POL-13.
- **Simulated review, in the right order this time** (dated today): Mateo Silva (accepted: add C4), Owen Park (rejected with reason: move laptop to connected-to; agreed). Page → **v0.9, In review**. Register page + extract: DOC-01 `in_review`, 0.9, page 425996.
- GOV-2 → In Progress; GOV-21 (CISO sign-off) → In Review, **waiting for the owner's go-ahead**.

### Decisions
- Staging view name is `stg_payments_rider_cards` (earlier notes said `stg_rider_cards`).
- Scope follows the data: synthetic but real-format PANs are treated as real, so the laptop is in scope.

### Next steps
- Owner reviews DOC-01 → record CISO approval v1.0 (CFO consulted), next scope confirmation 2027-11-24, scope-reduction ideas as follow-ups (GOV-21). Then GOV-2 closes and GOV-7/14/15 unblock.

---

## 2026-11-24 — Roster fix: Arjun Mehta role_code (generator 0.3.0)

### Done
- **User asked to fix** the missing `role_code` for Arjun Mehta (VP Engineering, EMP10064). The register names `vp-engineering` as owner of POL-07.
- `org_roster.csv`: role_code `vp-engineering` added.
- **Applied as a dated HR correction, not a rewrite of history.** New `ROSTER_CORRECTIONS` in `config.py` (`arjun.mehta: 2026-11-24`). Before that day the record keeps a blank role_code exactly as loaded. On Nov 24 (the first day not yet loaded; raw is loaded through Nov 23) the simulation emits a new version of his HR record with the role code. It uses its own random stream, so nothing else changes.
- `GENERATOR_VERSION` 0.2.0 → **0.3.0** (output from Nov 24 on differs: his new record version, and he now counts as a role holder).
- **Verified:** batches for Jan 1, Jun 15, Nov 22 and Nov 23 hash-identical between the old code (0.2.0, checked out separately) and the new code. New test `test_roster_correction_arrives_on_its_day_and_leaves_history_unchanged`; pytest 13/13.

### Decisions
- Fix forward with a dated correction so `raw` stays append-only and `stg_hris_employees_history` shows the blank → `vp-engineering` change on Nov 24 (an honest record that HR data was corrected).

### Next steps
- Takes effect in BigQuery after `atlassian-setup` is merged to `main` and the daily run generates Nov 24. **If tonight's daily run (from `main`) generates Nov 24 before the merge, the correction must move to the next unloaded day.**

---

## 2026-11-24 — Single source of truth; STD-01 v2.0 after late review; acknowledgments seed

### Done
- **Option (b) for the STD-01 review gap: an honest late review, dated today.** On the STD-01 page:
  - *[Simulated]* comments from Elena Popescu (GRC Analyst) and Robert Feld (General Counsel), and author replies from Jordan Ellis.
  - Elena: remove repo copies (one source of truth) → **accepted**.
  - Robert: Legal sign-off on every exception → **rejected with reason** (section 10 already bars waiving legal/regulatory/PCI requirements); compromise accepted by Robert: owner must consult General Counsel on exceptions touching legal, regulatory or contractual obligations.
  - Changes a responsibility → **major change, v2.0** (STD-01 section 6). Sections 4, 10, 11 revised; change-history row explains the late review. *[Simulated]* "Approved version 2.0" comment from Victor Hale, CISO. Next review unchanged (2027-11-24).
  - The v1.0 approval comment relabeled *[Simulated]*.
- **Policy Register:** STD-01 → v2.0; intro now says the page is the only source of truth and the repo seed is an extract; change-log entry. `policy_register.csv` updated.
- **Space home page:** warning panel disclosing that ECT is fictional and staff reviews/approvals/acknowledgments are simulated, posted from the owner's account, never backdated.
- **Repo copies deleted:** `01-governance-program/policies/` removed (created earlier today).
- **New seed `policy_acknowledgments.csv` (simulated)**: one row per employee per approved document version (`ack_id`, `doc_id`, `doc_version`, `employee_id`, `basis`, `assigned_on`, `due_on`, `acknowledged_on`, `evidence`). STD-01 v2.0: 19 people (policy owners/approvers, policy admins, data stewards who author, named reviewers), due 2026-12-08 (10 business days). 4 acknowledged today through their review/approval comments (evidence = Confluence comment IDs); 15 pending. Tests: `ack_id` unique/not null, `doc_id` must exist in `policy_register`. All 19 employees confirmed active in `stg_hris_employees` (read-only, capped query). `dbt parse` OK, pytest 12/12.
- **Jira:** decision comment on epic GOV-1 withdrawing every "copy to the repo" step in its 29 open tickets (descriptions left as written, as history).

### Decisions
- **Confluence is the single source of truth for policy text (user).** No policy copies in the repo, no blog/announcement post: Confluence page history and Jira record what was published and when. Recorded in `CLAUDE.md` #5 and STD-01 v2.0.
- **Simulation rules (user agreed):** simulated staff responses are labeled *[Simulated]*, dated the day they're recorded, and never backdated to hide a gap.
- The `policy_register` seed stays as an *extract* (dbt can't read Confluence). A later automation (Project 3) could generate it from the page.
- Acknowledgments use employee IDs, not names (data rule).

### Risks / audit material (not fixed)
- STD-01 v1.0 was approved before review (late review recorded in v2.0).
- `01-governance-program/governance/access-control-policy.md` (Project 1) is a second access control policy outside Confluence; resolve when POL-02 is drafted.
- Org roster: Arjun Mehta (VP Engineering) has no `role_code`, but the register names `vp-engineering` as POL-07 owner.
- New seed columns not in the classification register (CLS-01).

### Next steps
- GOV-2: PCI DSS scope (DOC-01).
- Dec 1: record further STD-01 acknowledgments; leave some missing past the Dec 8 due date as a gap.

---

## 2026-11-24 — STD-01 and template approved; GOV-3 closed; closing-comment rule

### Done
- **User approved STD-01 Policy Management Standard and the Policy Template.** Recorded per STD-01 section 8 (three places):
  1. STD-01 page: status banner APPROVED v1.0, version 1.0, approval/effective date 2026-11-24, next review 2027-11-24, v1.0 change-history row (approver Victor Hale, CISO).
  2. "Approved version 1.0" footer comment on the STD-01 page.
  3. Policy Register page: STD-01 row Approved, v1.0, dates filled; change-log entry. `policy_register.csv` updated to match.
  - Policy Template page: green "Template status: APPROVED v1.0" banner added. The DRAFT placeholders stay, because they're for the new policy copied from it.
- **Repo copies of approved documents:** new folder `01-governance-program/policies/` with `README.md` (index), `STD-01-policy-management-standard.md`, `policy-template.md`. (The Confluence markdown export dropped dates; restored by hand.)
- **Jira:** GOV-24 and GOV-3 → Done. Closing comments added to GOV-22, GOV-23, GOV-24 and GOV-3.

### Decisions
- **New working rule (user):** every ticket gets a closing comment before Done: *What happened* + *Open items*. Added to `CLAUDE.md` agreement #5.
- The Policy Template is not a numbered register document; its approval is recorded on its page and in the register change log.

### Risks / audit material (not fixed)
- STD-01 went from v0.1 straight to v1.0: no recorded comments from the named reviewers (Elena Popescu, Robert Feld) and no v0.9, which STD-01 section 7 requires. Approval comment was posted from the site owner's account on the CISO's behalf.
- The staff announcement of STD-01 within 10 business days (section 11) is not yet sent.

### Next steps
- GOV-2: PCI DSS scope & cardholder data flow (DOC-01). Then tomorrow's 8 policies.

---

## 2026-11-24 — GOV-22 approved; GOV-23 Policy Register built

### Done
- **GOV-22 Done:** user approved STD-01 Policy Management Standard and the Policy Template ("look great").
- **GOV-23 Done: Policy Register built in two places.**
  - **Confluence:** *Policy Register* page (65685) in the Policy Management folder. One row per document (17: STD-01, DOC-01, POL-01 to POL-15) with type, owner, approver, status, version, approval date, next review, Jira key and page link. All start as Draft. Includes a change log.
  - **Repo:** `data-platform/dbt/seeds/governance/policy_register.csv` plus its entry in `seeds/_seeds.yml` (description, labels, tests: `doc_id` unique/not null, `doc_type` and `status` accepted values). `dbt parse` passes and the 5 new tests are registered; `pytest` 12/12 pass.
  - `dbt/README.md`: added `seeds/governance/` to the layout table and a note on keeping the CSV in sync with Confluence (Confluence wins; same-session update by pull request).
- **Space home page updated:** replaced the template's placeholder description with a real one, and added a *Key documents* section linking the register, STD-01 and the template.

### Decisions
- Seed columns: `doc_id, title, doc_type, owner_role, approver_roles, status, version, approval_date, next_review_date, jira_key, confluence_page_id`. Roles are org-roster role slugs (labels rule: no names in data); `approver_roles` is `;`-separated for joint approvals (POL-04 CFO+CISO, POL-05 VP People+CISO).
- **The seed is not loaded to BigQuery yet.** It loads on the first daily `dbt build` after this branch is merged to `main`; it wasn't run locally to avoid writing to the shared `staging` dataset from a feature branch.
- **Planted register gaps (overdue review, unapproved policy, etc.) are not in yet.** They go in when approvals are recorded, so the register first reflects real progress.

### Risks
- The new seed's 11 columns land in `staging` without classification register entries, so CLS-01 (unclassified columns) will count them, like the other governance seeds. Consistent with the existing open CLS-01 finding; not fixed, per the findings rule.

### Next steps
- GOV-24: STD-01 review and CISO approval (record approval in all three places).
- GOV-2: PCI DSS scope & cardholder data flow (DOC-01).

---

## 2026-11-24 — GOV-22 drafted; schedule compressed; dependencies linked

### Done
- **GOV-22 (policy management standard + template): drafted in Confluence.** New folder **Policy Management** in `ECTG`, with:
  - **STD-01 Policy Management Standard** (draft v0.1, page 327917). Covers document types, roles, numbering, versioning, lifecycle, who approves what, the 12-month review cycle, exceptions and where documents are published.
  - **Policy Template** (page 65668): document control table, 8 standard sections and a change history.
  - Both pages linked on GOV-22. GOV-22 → **In Review**; GOV-1 and GOV-3 → **In Progress**.
- **Schedule compressed (user: "everything will wrap quickly").** Working days are Tue Nov 24, Wed Nov 25 and Tue Dec 1 (off Thu/Fri for the holiday). All 69 tickets re-dated, verified by JQL:
  - **Nov 24:** GOV-3 (register & standard), GOV-2 (PCI scope).
  - **Nov 25:** GOV-4 Info Security, GOV-5 Access Control, GOV-6 Classification, GOV-7 Cardholder Data, GOV-8 Acceptable Use, GOV-9 Risk, GOV-10 Change, GOV-11 Incident Response.
  - **Dec 1:** GOV-12 Logging, GOV-13 Vulnerability, GOV-14 Encryption, GOV-15 Vendor, GOV-16 Retention, GOV-17 HR Security, GOV-18 BC/DR.
  - Epic GOV-1: Nov 24 – Dec 1.
- **22 "Blocks" links added** (show as dependency lines on the Timeline):
  - GOV-3 blocks every policy story (GOV-4 … GOV-18).
  - GOV-2 (PCI scope) blocks GOV-7, GOV-14, GOV-15.
  - GOV-7 (Cardholder Data) blocks GOV-14 (Encryption).
  - GOV-5 (Access Control) and GOV-8 (Acceptable Use) block GOV-17 (HR Security).
  - GOV-9 (Risk) blocks GOV-13 (Vulnerability; exceptions use risk ratings).

### Decisions
- **Document numbering set in STD-01:** POL-xx policies, STD-xx standards, PRC-xx procedures, DOC-xx supporting documents. Planned IDs: POL-01 Information Security, POL-02 Access Control, POL-03 Data Classification & Handling, POL-04 Cardholder Data Protection, POL-05 Acceptable Use, POL-06 Risk Management, POL-07 Change Management, POL-08 Incident Response, POL-09 Logging & Monitoring, POL-10 Vulnerability & Patch, POL-11 Encryption & Key Management, POL-12 Vendor & Third-Party Risk, POL-13 Data Retention & Disposal, POL-14 HR Security, POL-15 BC/DR; DOC-01 PCI DSS Scope & Cardholder Data Flow.
- **Approval evidence in three places** (document control table, approver comment on the page, register) so an auditor can cross-check.
- Exceptions are raised in Jira GOV, max 12 months, and can't waive PCI DSS requirements.
- Classic Confluence **pages** (not live docs) for policies, for version history and approvals.

### Risks
- A Jira automation moved GOV-23/24 to In Progress when GOV-3 moved; reset to To Do.

### Next steps
- User reviews STD-01 and the template. Then GOV-23 (Policy Register page + `policy_register` seed), GOV-24 (approval), and GOV-2 (PCI scope), all today.

---

## 2026-11-24 — Jira timeline: start and due dates on all 69 tickets

### Done
- Moved the uncommitted CLAUDE.md / WORKLOG changes off `main` to branch **`atlassian-setup`** and pushed it (user asked). Not merged.
- **Set Start date and Due date on every GOV ticket (69/69, verified by JQL)** so the Jira Timeline tab shows the plan. Field: `Start date` = `customfield_10015`; due = `duedate`.

  | Wave | Stories | Dates |
  |---|---|---|
  | Foundation | GOV-3 Register & standard | Nov 30 – Dec 11 |
  | Foundation | GOV-2 PCI scope | Dec 7 – Dec 23 |
  | Wave 1 | GOV-4 Info Sec, GOV-5 Access, GOV-6 Classification, GOV-9 Risk | Dec 14 – Jan 22 |
  | Wave 2 (needs PCI scope) | GOV-7 Cardholder Data | Jan 4 – Feb 5 |
  | | GOV-14 Encryption, GOV-15 Vendor | Jan 11 – Feb 12 |
  | Wave 3 | GOV-8 Acceptable Use, GOV-17 HR Security | Jan 18 – Feb 19 |
  | | GOV-10 Change, GOV-11 Incident Response | Jan 25 – Feb 26 |
  | Wave 4 | GOV-12 Logging, GOV-13 Vulnerability | Feb 1 – Mar 5 |
  | | GOV-16 Retention, GOV-18 BC/DR | Feb 15 – Mar 19 |
  | Epic | GOV-1 | Nov 30, 2026 – Mar 19, 2027 |

### Decisions
- **Standard rhythm per policy:** draft 2 weeks → review 2 weeks → approval & publish 1 week. Wave 1 drafts are shortened to Dec 14–23, then review resumes Jan 4 (no work scheduled Dec 24 – Jan 1).
- **Dependencies built into the dates:** policy template approved (Dec 11) before any policy draft starts; PCI scope approved (Dec 23) before card-data policies start; Cardholder Data approved (Feb 5) before Encryption approval (Feb 8–12); Access Control approved (Jan 22) before HR Security review (Feb 1).
- At most 4 policies in review at once, to spread approver load.

### Risks
- Dependencies are only in the dates, not Jira links; a slip won't move dependent tickets automatically.
- Approver availability (CISO approves 9 policies) is the biggest schedule risk.

### Next steps
- Start GOV-22 (policy template & standard) on Nov 30.

---

## 2026-11-24 — Jira: policy-set epic created (GOV-1 to GOV-69)

### Done
- **Created 69 tickets in Jira project `GOV`** (user approved the format and said "create the tickets"):
  - **GOV-1 (Epic):** Information Security Policy Set (SOC 2 · ISO 27001 · PCI DSS).
  - **GOV-2 to GOV-18 (Stories, 17):** GOV-2 PCI DSS scope & cardholder data flow; GOV-3 Policy Register & policy management standard; then one per policy: GOV-4 Information Security (umbrella), GOV-5 Access Control, GOV-6 Data Classification & Handling, GOV-7 Cardholder Data Protection, GOV-8 Acceptable Use, GOV-9 Risk Management, GOV-10 Change Management, GOV-11 Incident Response, GOV-12 Logging & Monitoring, GOV-13 Vulnerability & Patch, GOV-14 Encryption & Key Management, GOV-15 Vendor & Third-Party Risk, GOV-16 Data Retention & Disposal, GOV-17 HR Security, GOV-18 BC/DR.
  - **GOV-19 to GOV-69 (Subtasks, 51):** 3 per story. GOV-2: inventory → data-flow diagram → CISO scope sign-off. GOV-3: standard & template → register page + `policy_register` seed → CISO approval. Policy stories: **draft** (GOV-25–39) → **review** (GOV-40–54) → **owner approval & publish** (GOV-55–69).
- Every ticket has Description (with steps), Why it matters, Potential blockers, Intended outcome. Owners, approvers and reviewers are named people from the org roster. Labels: `policy-set` on all, `pci` where card data is involved.

### Decisions
- **Combined policy set** for SOC 2, ISO 27001 and PCI DSS (user confirmed).
- **No framework mapping in the policy tickets** (user): mapping comes later in a separate **Common Control Framework (CCF)** project.
- **Jira hierarchy convention (user):** Epic = large project; Story = medium piece within it; Subtask = daily/weekly task.
- Planted policy gaps are **not** visible in tickets; the answer key stays in the repo.

### Next steps
- Start GOV-3 (policy management standard + register), then GOV-2 (PCI scope), then the policies.
- Later epic: Common Control Framework.

---

## 2026-11-24 — PCI DSS added to the policy scope; Jira structure

### Done
- The user asked whether payment data means PCI DSS applies, not just SOC 2. **Yes.** The README already says ECT must meet PCI DSS. Also, `raw.payments_rider_cards` and `staging.stg_rider_cards` hold **full card numbers, expiry dates and cardholder names**, so BigQuery `raw` and `staging` (and the pipeline that writes them) are in the cardholder data environment (CDE). Only `marts.dim_rider_cards` (last 4 digits) is out of scope.
- The control matrix (`02-soc2-iso-audit/control-matrix.csv`) maps to SOC 2, ISO 27001 and NIST only. **It has no PCI DSS column.**

### Decisions (proposed, awaiting the user)
- **One policy set mapped to SOC 2 + ISO 27001 + PCI DSS v4.0.1**, not a separate PCI set. PCI Req 12.1 needs an information security policy anyway, and each PCI requirement asks for documented policies. Add PCI-specific content: CDE scoping and card-data flow, a Cardholder Data Protection policy, targeted risk analyses (12.3.1), service-provider management (12.8).
- **Jira structure (user's rule):** Epic = large project; Story = medium piece within it (e.g. one policy); Subtask = daily/weekly task (drafting, mapping, review, approval).

### Risks / findings (left open for the audit)
- **Full card numbers stored in clear in the warehouse.** BigQuery's default encryption is storage-level, which PCI DSS 4.0.1 (3.5.1 / 3.5.1.2) doesn't accept on its own for non-removable storage. Storing card numbers in an analytics warehouse also conflicts with data minimization (3.2.1). Not planted, but realistic. Not fixed, per the findings rule.

---

## 2026-11-24 — Atlassian connected; split confirmed

### Done
- **Atlassian MCP connected** (official Rovo MCP, user sign-in). Site `empire-city-taxi.atlassian.net`.
- **User set up the workspace in the UI:** renamed the Jira project key from the default `KAN` to `GOV` (project "ECT GRC", no issues yet). Created the Confluence space **Empire City Taxi Governance** (`ECTG`). Claude verified both with read-only checks.
- **The default "My first space" (`MFS`) is still on the site.** It's unused; the user can delete or archive it in the UI if they want.

### Decisions
- **Split confirmed by the user:** Confluence holds policy text, minutes and process docs. Jira holds planning, findings, remediation and audit requests. The repo holds what the pipeline reads plus a copy of each published policy, because the Atlassian site is private and the repo is the public portfolio. WORKLOG stays the decision log. Recorded in `CLAUDE.md` working agreement #5.

### Next steps
- SOC 2 policy set (~14 policies) in Confluence, with planted gaps, plus the policy register seed in the repo.

---

## 2026-11-24 — Plan: Jira + Confluence, then SOC 2 policies and a controls framework

### Decisions (direction agreed with the user; details to confirm)
- **Policies before more data work.** Project 2's control GOV-01 claims an information security policy set that doesn't exist; an auditor's first request would expose it. Plan: ~12–14 policies scoped to Security, Availability and Confidentiality, plus a **policy register** seed (owner role, approver, version, approval date, next review). Plant gaps for the audit: an overdue review, an unapproved policy, a control with no policy, a policy with no control, and a policy the data contradicts (e.g. leaver revocation within 24h vs. ACC-02). Full set vs. core 8: not yet decided.
- **Then a controls framework as data:** move `02-soc2-iso-audit/control-matrix.csv` into dbt seeds linking policy → control → SOC 2 / ISO 27001 / NIST → owner (roster role; "GRC Lead" and "IT Manager" don't exist in the roster) → automated check (ACC / CLS / DQ) → evidence. This is the start of Project 3 (continuous control monitoring).
- **Atlassian for planning and documents:** the user is creating a free Atlassian Cloud site (Jira + Confluence). Site addresses can't be renamed on the free plan, so pick a company-style name once. Connection through Atlassian's official remote MCP server (Rovo MCP; one server for both products; browser sign-in; nothing installed locally).
- **Proposed split (to confirm):** Confluence holds policy text, minutes and process docs. Jira holds planning, findings, remediation and audit requests. The repo keeps everything the pipeline reads (policy register, control framework, issue register) and a copy of each published policy, because the Atlassian site is private and the repo is the public portfolio. WORKLOG stays the decision log.

### Risks
- Two places for documents can drift; the policy register in the repo records each Confluence page's link and version to keep them tied.

- **Confirmed by the user:** Claude creates Confluence pages directly (with a summary in chat); Jira tickets are drafted for approval and always have Description / Why it matters / Potential blockers / Intended outcome. **Full policy set** (not core 8), written once the MCP is connected. Recorded in `CLAUDE.md` working agreement #5.

### Next steps
- User: create the site, add the MCP (`claude mcp add --transport http --scope user atlassian https://mcp.atlassian.com/v2/mcp`, then `/mcp`).
- Confirm whether Claude may create pages and tickets directly or drafts them for approval.
- Start the policy set.

---

## 2026-11-24 — Real role accounts and the daily access check

### Done
- **User created three role service accounts in the console** (no keys): `ect-role-analyst`, `ect-role-steward`, `ect-role-security`. Each has BigQuery Job User on the project and Data Viewer on its datasets. `ect-pipeline` holds Service Account Token Creator on each of the three (granted per account, not project-wide). Verified with read-only checks.
- **Explained "borrowing" (impersonation)** at the user's request: the pipeline acting as a role account gets only that account's read-only access, so it can't widen its own. It's needed because a keyless service account can't sign in by itself, and only a real query proves enforcement.
- **Misconfigurations kept as audit findings** (user's decision): `ect-role-steward` on `raw` (deliberate), and `ect-role-analyst` on `raw` instead of `ect-role-security` (a setup slip the user chose to keep). Recorded in `seeds/governance/role_account_answer_key.csv`.
- **Built `uv run ect-access-check`** and added it to the daily workflow after `ect-daily`. For each account × dataset it records **config** (on the permission list?) and **enforcement** (acting as the account, does a dry-run query get accepted?). Results go to the new observed table `raw.iam_role_access_tests`, then `marts.fct_role_access_tests` (ACC-08 excess, ACC-09 missing, ACC-10 check failed) and `marts.fct_role_access_scorecard`. The run record gets an access table.
- Policy doc updated: `access-control-policy.md` → *Enforcement (real)*.

### Decisions
- **Design vs. operating effectiveness:** both checks are kept because they can disagree, and that disagreement is itself audit evidence.
- **Expected access comes from the policy matrix**, not from a separate list, so changing the policy changes the test.
- **Enforcement probes use what a user needs:** `raw.hris_employees`, `staging.stg_hris_employees` (a view), `marts.dim_employees`.
- The check never fails the daily run; problems are recorded as `error` (ACC-10).

### Risks
- **Expected first-run surprise:** staging models are *views* over `raw`. In BigQuery, querying a view also needs access to its source tables, unless the view's dataset is authorized on `raw`. So `staging` access probably only works for accounts that also have `raw`. If confirmed, that's a real design gap (the policy gives stewards staging without raw), fixable with an authorized dataset. Leave it as a finding.
- The enforcement path can't be tested locally (impersonation from the laptop is blocked), so the first GitHub Actions run is the real test.

### First run (2026-11-24, run 45437194376, started by Claude at the user's request): green
- 18 checks loaded into `raw.iam_role_access_tests`. dbt: 66 pass, 39 warn, 0 errors.
- **Scorecard: all 3 planted misconfigurations caught by both checks** (analyst on `raw`, steward on `raw`, security missing `raw`).
- **One unplanted finding, as predicted:** `ect-role-security` is *on* the `staging` permission list (config passes), but BigQuery refuses its query (enforcement fails, ACC-09). The refusal names `raw.hris_employees`, the table under the `staging` view. **Design gap:** staging views need `raw` access unless `staging` is authorized on `raw`, so the policy's "staging without raw" (stewards) can't work as built. Left open as an audit finding; the fix would be an authorized dataset.
- The steward's `staging` check passes only because of its (planted) `raw` access, so fixing that misconfiguration alone would expose the same gap for stewards.
- Small fix: refusal messages now keep only BigQuery's reason, not the request URL.

### Next steps
- Open findings for the audit: ACC-08/09 role accounts, the staging-view design gap, CLS-01 unclassified columns.

---

## 2026-11-24 — Org build-out and access control (simulated)

### Done
- **Merged to `main` directly** at the user's request (`612fad6`), and **`raw` rebuilt** with the user's approval: deleted the 10 generated tables (TLC sample and zones kept), regenerated 2026-01-01 → 2026-11-23 with v0.2.0 and bulk-loaded them. New `raw.iam_access_grants`: 214 rows (grant versions).
- **Full dbt build:** 143 nodes, 106 pass, 37 warn, 0 errors.
- **Access scorecard:** ACC-01 to ACC-07 caught **34 of 34** planted problems (100%), **0 false alarms**.
- **CLS-01 now flags 79 unclassified columns** (the new IAM table across raw/staging/marts and the new HR columns), as expected until the steward proposes classifications.
- **Decision (user, 2026-11-24):** the 79 unclassified columns are **left unclassified on purpose** as a finding for a future audit ("we need to have things to fix"). Don't remediate them.
- Active corporate staff per department now range from 8 (Legal & Privacy) to 28 (Customer Support).
- **Decision logged (user, 2026-11-24):** for classification changes, *"stewards propose and owners approve. Draft the changes as a steward would and I approve them."* Claude drafts as the steward; the user approves as owner.
- **Named roster** `data-platform/src/ect_platform/data/org_roster.csv`: 68 named people across 12 departments plus the CEO (the leaders and stewards from `governance-org-structure.md` plus 3–5 staff per department), each with a title, manager, role slug and access role. They are the first employees generated, so the CEO is `EMP10001` and Jordan Ellis is `EMP10003`.
- **HR data:** departments now match the org doc (12 departments). New columns `manager_id` and `role_code`. New lifecycle event: **transfers** between departments (movers).
- **Access policy matrix** `dbt/seeds/governance/access_policy.csv` (role × dataset → privilege, max classification, time limit, approver) and the policy doc `01-governance-program/governance/access-control-policy.md`. Analysts get `marts` only; security gets `raw` for 14 days per investigation; privacy gets rider `raw` for data subject requests.
- **New raw table `iam_access_grants`** (domain `risk`): grants on joining, revoked on leaving or transfer, expiring time-bound grants. 
- **Planted access scenarios ACC-01 to ACC-07** (analyst with raw, leaver not revoked, mover creep, self-approval, expired still active, no approval, wrong approver). Simulated through 2026-11-23: 183 grants, 27 planted defects across all 7 rules.
- **dbt:** `stg_iam_access_grants` (+ `_history`), ACC rules in `fct_dq_findings` and `dq_rules.csv`, `marts.fct_access_grants` (access review list) and `marts.dim_access_policy`; `dim_employees` gains `manager_id` and `role_code`.
- Generator version **0.2.0**. Tests: 12 pass (3 new: stable roster IDs and managers, unplanted grants follow the policy, business users and drivers have no access).

### Decisions
- **Roster inside the generator, not a separate seed:** named people must exist in HR data so grants, approvers and managers join to real employee IDs.
- **Named people never leave or transfer**, and employees carrying a planted access defect are protected from later random events, so a defect can't be cleaned up by accident.
- **`raw` needs a one-time rebuild**: departments and IDs change for all history, so v0.1 and v0.2 rows can't be mixed. All raw data is regenerable from the deterministic generator. Waiting for the user's go-ahead.

### Risks
- The scheduled run (05:30 New York) on `main` must not run between the merge and the rebuild, or it will fail on the new columns. Do both together.
- New columns are not yet in the classification register, so CLS-01 will flag them until the steward proposes classifications.

### Next steps
- Real role service accounts (3–4), set up by the user in the console, plus a verification test.

---

## 2026-11-24 — Column classification register (single source of truth)

### Done
- First fully green scheduled-style run confirmed earlier today; this work follows the user's question: *where is column classification held?*
- **Found:** column-level classification lived only in the stale Project 1 CSV (old table names, 27 of 96 raw columns missing, not loaded or used). Table labels were set in three places, and the marts cap test used a hard-coded column list.
- **Built** (approach approved by the user, who also asked for more wrongly-mapped scenarios):
  - **Register** `seeds/governance/column_classification_register.csv`: 500 rows covering every column in `raw`, `staging` and `marts`, with classification, category, treatment, owner, steward, status, proposed/approved by, and date.
  - **Answer key** `seeds/governance/column_classification_answer_key.csv`: 508 rows (18 Secret, 33 Confidential, 58 Sensitive, 361 Internal, 38 Public). Built from the Project 1 map, decisions for the new columns, and lineage (staging inherits from raw; marts follow masking, generalization and aggregation). It agrees with every table label and the marts cap.
  - **Checks** `marts.fct_classification_findings`: CLS-01 to CLS-08 (coverage, orphans, approval, table-label consistency, lineage drift, marts cap, steward mismatch, invalid tier), each a dbt warning test.
  - **Scorecard** `marts.fct_classification_scorecard`: register vs. answer key per column, plus which check flagged it.
  - **Process doc** `01-governance-program/governance/classification-register.md`.
- **12 planted scenarios (S01–S12), 36 register rows:** location (GV-003), free-text PII, partial cardholder data, regulated ID, consistent HR under-classification, lineage drift, over-classification, masked value, unclassified new columns, approval backlog, wrong steward, retired tier name.
- **First scorecard:** 27 of 508 columns wrong or missing; **24 flagged by checks**; the 3 unflagged are S05, a deliberate blind spot. **KPI #2 (high-risk columns correct): 72.5%** (37 of 51).
- Full dbt build: 126 nodes, 96 pass, 30 warn, 0 errors.

### Decisions
- **The register is the single source of truth**, kept in the repo and changed by pull request: steward proposes, owner approves, CISO or Privacy review Secret and Confidential changes. That is the federated model, and PR history is the audit trail. Collate and BigQuery tags will be fed from it later.
- **Operational register vs. answer key:** the register can be wrong, like real life; the answer key is used only to score it.
- **Register rows are per layer**, because classification can legitimately change between layers (masked, generalized, aggregated in marts).
- **CLS-05 flags both sides** of a raw/staging disagreement, since either could be the mistake.
- **The marts cap test stays on its fixed column list** as an independent safety net, because the register itself may contain mistakes.
- The Project 1 `column-classification-map.csv` is superseded but kept as a Project 1 artifact.
- The one-off bootstrap script was not committed; the CSVs are now maintained by hand through PRs.

### Next steps
- Remediation through the council (GV-003 first), council roles (federated), and DQ rule ownership columns.

---

## 2026-11-24 — Daily run (GitHub Actions); DQ rule ownership; federated model

### Done
- Merged `marts` to `main` from the CLI at the user's request (`8accce2`).
- **`uv run ect-daily`:** finds the newest loaded day (`MAX(_batch_date)` of `raw.app_trips`, ~3 MB read), then generates and loads every missing day through yesterday. A failed or skipped run is caught up the next day. Tested with a dry run: last loaded 2026-11-23, 0 days due.
- **`uv run ect-record`:** writes `data-platform/run-records/<date>.md` with the days loaded, row counts per table, and the dbt results (every warning or failure with its failing-record count). Counts and test names only, never data values.
- **Workflow** `.github/workflows/daily-refresh.yml`:
  - Runs daily at 10:30 UTC (5:30 am New York), plus a manual "Run workflow" button.
  - Steps: keyless Google sign-in → install → generator tests → `ect-daily` → `dbt build` → run record → commit.
- **Setup guide** `data-platform/docs/github-actions-setup.md`: console steps A–G for the user (APIs, service account, dataset access, Workload Identity pool and provider, impersonation grant, GitHub variables, test run).
- Read-only check: the IAM, IAM Credentials and Security Token Service APIs are **not enabled** yet. That's step A.

### Decisions
- **DQ rule ownership (the user's point):** data quality rules should be **written by data stewards, with the data owner's approval**, because they are closest to the data and its use. The 23 rules in `dq_rules.csv` are **drafts proposed by the governance hub**, pending each domain's sign-off. The hub owns the framework (catalog, findings, scorecard, controls); the domains own the rule content.
- **Leaning toward a federated (hub-and-spoke) governance model** over a centralized one. The hub (Data Governance Manager) sets standards, tooling, the scorecard and reporting. Domain owners and stewards (the spokes) make and enforce decisions for their data. Roles and responsibilities to be fleshed out (backlog).
- **Keyless sign-in** (Workload Identity Federation): restricted to this repository by an attribute condition; one service account, `ect-pipeline`.
- **Least privilege:** BigQuery Job User (project) plus BigQuery Data Editor on `raw`, `staging` and `marts` only. No service-account key is ever created.
- **Catch-up design:** the pipeline works out what's missing from BigQuery itself rather than trusting the schedule, so missed days heal themselves.
- **Run records are committed to the repo:** audit evidence for each run (Project 3 control monitoring), and the commits keep GitHub from pausing the schedule after 60 days of inactivity. **Open question:** commit them straight to `main`, which needs the user's OK, or to a separate branch.

- Pushing the workflow needed the GitHub CLI's `workflow` permission. The user granted it with `gh auth refresh -s workflow`; in `!` commands use the full path `/opt/homebrew/bin/gh`.
- **The user completed console setup steps A–F.** Merged `daily-refresh` to `main` from the CLI at the user's request. Run records go to `main` by default, since the user hasn't chosen otherwise.

- **First run failed (403 `iam.serviceAccounts.getAccessToken`).** Cause: in the provider's attribute mapping, the OIDC side read `attribute.repository` instead of `assertion.repository` (same for `repository_owner`), so the step E impersonation grant never matched. Found with read-only `gcloud` checks; **the user fixed it in the console.**
- **Re-run:** sign-in, catch-up, load and `dbt build` all **succeeded**. Only the run-record push failed, because `main` had moved ahead (the first run had committed its own failure record). **Fixed:** the workflow now rebases before pushing, and records are named `<date>_<time>.md` so same-day runs never clash.

- Merged `run-record-fix` to `main` from the CLI at the user's request (`1ff4423`).
- **First fully green run** (run 45425307173, manual, 1m35s): 9 generator tests passed; catch-up found 2026-11-23 loaded (0 days due); dbt 91 pass, 23 warn, 0 errors; run record `run-records/2026-11-24_1026.md` committed by the bot (`93216de`).

### Next steps
1. Check tomorrow's scheduled run (05:30 New York), the first to load a new day (2026-11-24).

---

## 2026-11-24 — Marts, rule catalog and data-quality scorecard

### Done
- Merged `dbt-project` to `main` from the CLI at the user's request (`e412f30`).
- **Answered the user's questions:**
  - *Where are the reference rules?* Before this step there was only REF-01, a staging test. Now **all rules live in one catalog** (`seeds/dq_rules.csv`, 23 rules): DQ-01 to DQ-16 (planted), T1 to T4 (real trip data), REF-01 to REF-03 (reference data).
  - *How is `gov_planted_defects` used?* As the **answer key** for scoring the checks. `fct_dq_scorecard` compares the findings with it per record.
- **Rule logic in one place:** `marts.fct_dq_findings` lists every failing record (rule, table, record ID, column; never values). One dbt test per rule warns when there are findings. The old per-column DQ tests in staging were removed.
- **Scorecard** `marts.fct_dq_scorecard`: **100% detection on all 16 planted rules and 0 false positives**, scored record by record. Real-data findings: T1 2,492, T2 19,306, T3 5,011, T4 138, REF-01 2, REF-02 4,993, REF-03 3,879.
- **Two governance controls run on every build:**
  - `scorecard_every_planted_defect_caught` (error if a rule misses any planted defect);
  - `assert_marts_classification_cap` (error if a marts table is labeled above Sensitive, or has a Secret/Confidential column). **Both pass.**
- **14 marts tables** in `marts`, all labeled (layer `marts`, classification sensitive / internal / public):
  - Dimensions: `dim_employees`, `dim_drivers`, `dim_riders`, `dim_rider_cards`, `dim_taxi_zones`, `dim_campaigns`, `dim_rider_segments`, `dim_dq_rules`.
  - Facts: `fct_trips` (357k, partitioned by pickup date, clustered by driver), `fct_daily_zone_trips` (24.6k), `fct_trip_surveys`, `fct_ledger_entries`, `fct_dq_findings` (37.1k), `fct_dq_scorecard`.
- Full build: **114 nodes; 91 pass, 23 warn (the rules), 0 errors.** The heaviest query processed 75 MB.

### Decisions
- **How the Sensitive cap is applied in marts:**
  - **Removed:** SSN, bank account, card number, expiry and cardholder (Secret); salary, rating, contact details, licence, background check (Confidential).
  - **Masked:** card number → last 4 digits; survey comment → phone numbers and emails `[REDACTED]`.
  - **Generalized:** in `fct_trips`, pickup and dropoff zone → **borough**, because zone plus rider_id would reveal a person's movements. Zone-level demand is in `fct_daily_zone_trips`, aggregated with no rider or driver IDs.
- **`dim_rider_cards` is out of PCI scope** (last 4 digits only), so it's labeled `pci_scope: false`.
- **Reference data is corrected in marts, not staging.** `dim_taxi_zones` collapses duplicate IDs and adds zones 57, 104, 105, 264 and 265 from a documented supplement seed (`zone_source` shows which). Staging keeps the public data as published, so REF-01 stays visible.
- **Duplicate rules flag only the later copies** (by ID order), not the first holder of a value. That matches how the defect arises.
- **T5 dropped** (total ≠ components): the public table lacks the congestion surcharge, so it would flag almost every trip. T6 (bad driver/rider IDs) is now covered by the relationship tests.
- Marts are full-rebuild tables for now (small data). Switch `fct_trips` to incremental if build cost grows.

### Next steps
- GitHub Actions daily run (generate → load → `dbt build`), which needs a Workload Identity setup by the user in the console.
- Looker Studio: a DQ scorecard and trips dashboard on `marts`.

---

## 2026-11-24 — dbt project: staging layer and data-quality tests

### Done
- Merged `bulk-backfill` to `main` from the CLI at the user's request (`7c4b94e`).
- Built **`data-platform/dbt/`** (dbt 1.12, BigQuery). It uses the user's Google sign-in with no keys, a 1 GB cap per query, and job labels for cost tracing.
  - **16 staging views** in `staging`:
    - a current-version view (`stg_*`) for each raw table;
    - full-history views (`stg_*_history`, with `valid_from`, `valid_to`, `is_current`) for employees, drivers, riders, cards and segments;
    - trips, surveys, ledger, taxi zones, and the answer key.
  - Each view carries its description and **10 labels** (layer `staging`).
  - **Tests:**
    - 42 structural tests (unique IDs, plus links between tables: trips→drivers, drivers→HR, cards→riders, campaigns→segments). **All pass.**
    - The **16 data-quality rules DQ-01 to DQ-16**, as warnings. DQ-13 to DQ-16 are new, so every planted defect type has a rule.
  - **Freshness checks** on the daily-changing raw tables (warn after 2 days without a load, error after 4).
- **First scorecard:** every rule catches exactly the number planted, with no false positives. Uniqueness and allowed-values rules count distinct values rather than rows. The table is in `data-quality-rules.md`.
- **Verified history:** 647 employees and 470 drivers, each with exactly one current version. DRV10200 shows active → suspended → reinstated → inactive.

### Decisions
- **Revised:** history comes from **`raw` change logs** through dbt views, **not dbt snapshots**. Raw already stores every version, so history covers 2026-01-01 onward and can be rebuilt. Snapshots would only start recording from their first run and couldn't be rebuilt. Snapshots stay available for sources that aren't change logs.
- **Staging keeps defects as they are:** no clean-up, so the tests can find problems. Fixes happen only after an owner or council decision, which makes the remediation demo.
- **Data-quality rules are warnings, not failures.** Structural tests are errors.
- **dbt writes only to existing datasets** (`staging`, later `marts`). A schema-name macro stops dbt from creating new datasets.
- Staging is views, not tables: no storage cost, and always up to date with `raw`.

### Real-data findings (not planted)
- **REF-01:** the public taxi zone table has duplicate IDs. Zone 57 (Corona) is filed under 56, and 104/105 (the harbor islands) under 103. This explains why zone 57 trips have no match.

### Next steps
- Marts (`dim_*`, `fct_*`, capped at Sensitive) and a per-record DQ scorecard; or the GitHub Actions daily run.

---

## 2026-11-24 — Backfill loaded into BigQuery `raw`

### Done
- Merged `tlc-december-fix` to `main` from the CLI at the user's request (`5088859`).
- Added **bulk backfill** to the loader (`--bulk`): one load job per table for a whole date range, instead of one job per table per day (~2,300 jobs). It refuses to run if any of those days is already loaded, and it checks row counts.
- **Loaded 2026-01-01 → 2026-11-23** in about 1.5 minutes (loads are free). All 10 tables were created with their descriptions and 10 labels each, partitioned by `_batch_date`:

  | Table | Rows |
  |---|---|
  | `app_trips` | 357,049 (91 MB) |
  | `app_trip_surveys` | 10,908 |
  | `app_riders` | 4,645 |
  | `payments_rider_cards` | 3,894 |
  | `gov_planted_defects` | 1,237 |
  | `hris_employees` | 954 |
  | `fleet_drivers` | 783 |
  | `payments_financial_ledger` | 204 |
  | `app_rider_segments` | 132 |
  | `app_marketing_campaigns` | 62 |

- **Verified:**
  - Every row count matches the generator's manifests.
  - All 12 `raw` tables carry 10 labels.
  - **Re-loading 2026-11-23 left it at 1,090 trips**, so re-runs replace rather than duplicate.
  - Trip IDs are unique.

### Real-data findings (not planted)
- **5,000 trips have pickup zones that aren't in the zone reference table:** 264 "Unknown" (4,199), 265 "Outside NYC" (792), and zone 57 (2). That's a genuine reference-data gap, good material for a referential-integrity check and a reference-data issue.

### Risks / watch items
- Storage usage per table (`INFORMATION_SCHEMA.TABLE_STORAGE`) needs an extra permission the user's account doesn't have. Table details in the console show the sizes anyway.

### Next steps
- Suggested order: (1) dbt project (staging models and snapshots over `raw`), (2) GitHub Actions daily run, (3) column descriptions and the gap register, (4) Phase 1 tables.

---

## 2026-11-24 — TLC setup run; December gap fixed; backfill generated

### Done
- **The user ran `sql/01` and `sql/02` in the BigQuery console.** Verified read-only:
  - `raw.tlc_yellow_trips_sample`: **362,834 trips**, 76 MB, partitioned by day, 10 labels, no duplicate keys.
  - `raw.tlc_taxi_zones`: 263 zones, 10 labels.
- **Found:** the public 2022 table stops on **2022-11-30** (no December). **Fixed:** simulated dates that land in December now replay the trips from 5 weeks earlier, on the same weekday. The test now checks every day for two years.
- **Generated the backfill locally:** 2026-01-01 → 2026-11-23 (327 days). It contains 357,049 trips, 10,908 surveys, 4,645 rider records, 3,894 card records, 954 HR records, 783 fleet records, and 1,237 planted defects. Nothing is loaded yet.
- Checked a spurious alarm: every `tlc_sample_key` ends in "00". That is expected, because the 1% sample keeps only trips whose hash is divisible by 100.

### Real-data findings (not planted; future data-quality material)
- **2022-09-18 has only 36 trips** (normal is ~1,100), an apparent gap in the public data. It is replayed as **2026-09-13**, which makes a good test for a volume anomaly check.
- **2022-01-29 is low (339)** because of the real blizzard. That's a true dip, not an error.

### Next steps
- The user approves the backfill load into `raw` (loads are free).

---

## 2026-11-24 — Phase 0: daily data generator and loader

### Done
- Merged `project-context` (CLAUDE.md, public WORKLOG) to `main` from the CLI at the user's request (`fc55a41`).
- Built **`data-platform/`**: a Python package (uv, Python 3.12, Faker 37) with a generator, a loader, one-time SQL and tests.
  - **Generator** (`uv run ect-generate`): replays company life from **2026-01-01** day by day, and writes each day's new and changed records to `output/<date>/*.jsonl` with a manifest (row counts, SHA-256).
  - **Lifecycle:** hires and terminations; driver onboarding → background check → active; suspensions and reinstatements; a March 1 annual review; rider sign-ups, profile changes and closures; cards added and removed; new campaigns; monthly segment refresh; ledger postings on the 3rd.
  - **Drivers are now employees**, so every `DRV` has an `EMP` in HR. That is the foundation for GV-004 (terminated in HR, still active in fleet), which gets planted in Phase 3.
  - **Trips:** about 1,000 real 2022 NYC yellow-taxi trips a day, replayed on the same weekday (52-week cycle). Synthetic drivers are assigned; riders only on app-booked card trips, while street hails have no rider. Surveys go on about 6% of app trips.
  - **Planted defects:** the 16 Project 1 defect types carry over. Every one is logged in the answer key `gov_planted_defects` (record and column only, never the bad value). The epoch batch plants 292.
  - **Loader** (`uv run ect-load`): creates each `raw` table on first load with its schema, description and labels. Tables are partitioned by `_batch_date`, and each day replaces only its own partition, so history is append-only and re-runs can't duplicate.
  - **One-time SQL** (validated with dry runs; **not run yet**): `sql/01` copies a fixed 1% sample of 2022 TLC trips (~6.8 GB scan, ~360k rows), and `sql/02` copies the 263 taxi zones (~2 MB).
  - **Tests:** 9 passing. They cover same date → identical data, byte-identical files, weekday-aligned TLC mapping, prefixed IDs, trips only to active drivers, schema and label coverage, Luhn-valid cards, and an answer key with no values.
- Checked the simulated state on 2026-11-23: 331 active drivers, 494 active employees, 3,714 active riders, 3,385 active cards, 0 HR/fleet mismatches.

### Decisions
- **2023 TLC data is not usable.** The public 2023 table is empty, so 2022 is replayed in a 52-week cycle that keeps weekdays aligned. Trips repeat yearly, but driver and rider assignments differ.
- **Replay-from-start design:** state on any date is rebuilt from 2026-01-01 (under 1 second for a year), so no state files need storing. The trade-off is that changing generator code changes history; `_generator_version` on every row traces which code made it.
- **Incremental extracts:** raw holds full record images each time a record changes, not just events. That is the standard input for dbt snapshots.
- **Code lives in `data-platform/`** at the repo root, because it serves all four projects. The Project 1 generator and CSVs stay as they are, as Project 1 artifacts.
- **The answer key goes in the warehouse** (`raw.gov_planted_defects`), so a data-quality scorecard (caught vs. planted) can run in SQL. Checks must not read it.
- **Safe synthetic values:** 555 phone numbers, reserved email domains, a test-style `4000 00` card prefix. Card numbers are Luhn-valid, so Google Sensitive Data Protection will recognise them.
- Labels are applied when the loader creates each raw table (part of the "labels on tables" backlog item). Planted label gaps are still to come.

### Risks / watch items
- `trip_distance`, fares and other TLC values pass through untouched, including the real data's errors. That is intended.
- The epoch batch is about 4,900 records; later days are a few dozen records plus about 1,000 trips.

- Committed as `629742a` on branch `phase-0-generator`; **merged to `main` from the CLI** at the user's request.
- The user chose to **run the one-time SQL themselves in the BigQuery console**.

### Next steps
1. The user runs `sql/01` and `sql/02` in the BigQuery console (one-time; ~6.8 GB scanned).
2. Backfill: `ect-generate --backfill`, then `ect-load` for 2026-01-01 → yesterday.
3. Check the tables in the BigQuery console.

---

## 2026-11-23 — Governance org and council charter; repo housekeeping

### Done
- **Org structure** (`01-governance-program/governance/governance-org-structure.md`): reporting lines, fictional named role holders, owners and stewards per domain, custodian and consumer roles, and the department objectives that create governance tensions.
- **Council charter** (`01-governance-program/governance/data-governance-council-charter.md`): purpose, authority, membership and voting, meetings and quorum, decision rules, issue lifecycle with severity targets, escalation path, a RACI for 12 decision types, standing agenda, 7 KPIs, and the initial backlog GV-001 to GV-006, each tied to a defect planted in the data.
- Committed as `245c3e7` on branch `governance-council`; **merged to `main` from the CLI** at the user's request.
- Added `CLAUDE.md` (project context and working agreements) and moved this log into the repo as `WORKLOG.md`. The user chose to keep the log **public**. Committed as `8fe21bb` on branch `project-context`; **merged to `main` from the CLI** at the user's request.

### Decisions
- Council members get **fictional names**. Names appear in docs and minutes only; labels and data use role slugs.
- **The CDO (Renée Okonkwo) is the final escalation point**, as leader of the data organization. Vetoes and deadlocks go to the CDO, and the CEO receives a quarterly governance report.
- The **CISO and Privacy Officer keep their vetoes**. The Privacy Officer reports to General Counsel, which keeps privacy independent of the CDO.

---

## 2026-11-23 — Classification, labels, dataset layout

### Done
- **Label standard** (`01-governance-program/governance/labeling-standard.md`, v0.1): label keys for datasets and tables, a domain register, formatting rules, a planned automated compliance check, and deliberate label gaps.
- **Dataset labels** applied by the user in the console (`layer`, `classification`, `data_custodian`, `environment`, `managed_by`) and confirmed with a read-only check.
- **Datasets** `raw`, `staging` and `marts` created by the user (US location, no table expiry), with descriptions. Ownership is carried by labels, not descriptions.
- Committed as `f403b0f` (branch `five-tier-classification`) and **merged to `main`** with the user's approval.

### Decisions
- **Five-tier classification: Secret → Confidential → Sensitive → Internal → Public**, replacing Restricted → Confidential → Internal → Public. The user chose "Internal" over "Restricted" for tier 4, because "Restricted" usually signals a high tier. **SSN = Secret.**
  - **Secret:** SSN, cardholder data (card number, expiry, name), payout bank account, credentials.
  - **Confidential:** contact PII, TLC license, background check, salary, performance rating, pickup/dropoff locations, free-text comments.
  - **Sensitive:** names, employee work email, fares/tips/totals, ledger amounts, budgets.
  - Column map: 6 Secret, 12 Confidential, 12 Sensitive, 38 Internal, 1 Public.
  - Handling: Secret never goes to non-prod or `marts`. Confidential is masked or aggregated in `marts`. **`marts` is capped at Sensitive.**
  - Applied across 15 files. The vendor-risk tool keeps its 1–4 scoring, with the option labels updated.
  - Also fixed a glossary CSV bug: unquoted commas would have broken the catalog import.
- **Dataset layout: by layer** (`raw` / `staging` / `marts`). The domain is carried by labels. Raw tables get a source-system prefix (`hris_`, `fleet_`, `payments_`, `app_`, `tlc_`). dbt names its tables `stg_*` in staging and `dim_*`/`fct_*` in marts. Access control is set per layer (analysts get `marts` only).
- **Prefixed IDs** (`DRV10042`, `EMP10001`, `RDR…`, `VEH…`) replace integer IDs.

### Design review of the ChatGPT notes (tables, lifecycle, org, council)
- Adopted: department conflicts and the governance council; lifecycle data (hires, terminations, reassignments, no physical deletes); staged rollout; taxi data treated as one source system among several.
- Adjusted:
  - **`raw` is append-only.** History tables come from **dbt snapshots**, not UPDATEs to BigQuery.
  - **The daily generator is deterministic code** run by GitHub Actions, not Claude-in-the-loop. Claude/MCP write access is a gated Project 4 item.
  - **Governance records are repo files loaded as dbt seeds.**
  - **Real TLC taxi zones** are used for locations.
  - **Project 2's control matrix** is reused as `compliance_controls`.
- **Rule:** every conflict scenario is backed by a defect planted in the data.
- **Phased table plan:**

  | Phase | Scope |
  |---|---|
  | 0 | Framework and the existing tables |
  | 1 | `vehicles`, `vehicle_assignments`, `payment_transactions`, `driver_payouts`, org seeds |
  | 2 | `rider_consent`, `support_tickets`, `privacy_requests`, `data_access_logs` |
  | 3 | Council scenarios |
  | 4 | Clickstream (nested `app_events`) |

---

## 2026-11-23 — Tools, sign-ins, Google Cloud guardrails

### Done
- Installed:
  - Homebrew (by the user)
  - gh 2.105.0
  - uv 0.13.9 and Python 3.12
  - Google Cloud CLI 594.0.1
  - dbt-core 1.12.7 with dbt-bigquery 1.12.4
- Signed in to GitHub CLI (`2Wake`), gcloud, and application-default credentials.
- Fixed `command not found: gh`: added Homebrew's setup line to `~/.zshrc`.
- Cloned the repo to `~/empire-city-taxi-grc`. The repo's git identity uses the GitHub noreply email, so no personal email appears in commits.
- Google Cloud project **`empire-city-taxi`** (billing enabled) set as the default.
- **Cost guardrails:**
  - Budget **"ECT free-tier guardrail"**: $5/month, alerts at 5¢, $1, $2.50 and $5 actual, plus a forecast alert. Created by Claude through the CLI, before the UI-only agreement.
  - **BigQuery "Query usage per day" quota set to 0.03 TiB (~30 GB)** by the user in the console. This hard cap keeps a month of queries under the 1 TB free tier.
  - `maximum_bytes_billed` per query (in dbt) and date-partitioned tables are still to come.

### Working agreements established
- The user makes all cloud and account configuration changes **in the web UI**. Claude provides the steps and changes no settings without explicit approval.
- Commits go on a branch. **Claude always asks before merging anything.**
- Every step is logged here.

---

## 2026-11-23 — Migrated from Claude Chat to Claude Code; stack decided

### Done
- Brought the Claude Chat build log (Projects 1 and 2 complete, Projects 3 and 4 planned) into Claude Code.
- Connected the GitHub MCP. It's read-only, so writes go through `gh`.
- Checked the laptop: 8 GB RAM, which rules out running OpenMetadata, Airflow and Metabase locally.

### Decisions

| Area | Decision | Rationale |
|---|---|---|
| Warehouse | **BigQuery with billing on** (not the sandbox) | Removes the sandbox's 60-day table expiry. About 2–3 GB/yr expected, against 10 GB of free storage. |
| Cost control | Daily query quota, per-query byte limit, budget alerts, partitioning | The quota and per-query limits block spending; alerts only warn. |
| Catalog / governance | **Collate free tier** (hosted OpenMetadata) | Uses no laptop RAM. |
| Orchestration | **GitHub Actions** daily, keyless login through Workload Identity Federation | Free, runs off the laptop. Cloud Composer costs hundreds of dollars a month. Each run's committed record doubles as control evidence. |
| Transform / DQ | **dbt Core**; the full DQ rule set runs daily in dbt | Free within the BigQuery free tier. Collate's free tier allows only 10 tests. |
| PII detection | Google Sensitive Data Protection (sampled one-off jobs) plus manual tags checked against the answer key | Collate's PII auto-classification is paid only. SDP's first 1 GB/month is free. |
| Reporting | Looker Studio | Free, in the cloud. |
| Avoid | Cloud Composer, Cloud SQL, scheduled Dataplex DQ scans | Cost. Dataplex DQ isn't in the free tier or covered by the BigQuery quota. |

### Risks / watch items
- **Collate's free tier is reclaimed after 4 weeks without a login.** Log in every couple of weeks, and keep the governance artifacts in the repo as the backup.
- Collate free-tier limits: 5 users, 500 assets, weekly refresh and tests, 10 test cases, 5 alerts.
- Collate's AI behavior is undocumented (on by default? auto-applied? which LLM?). Evaluate it after sign-up; possible Project 4 material.
- GitHub pauses scheduled workflows in public repos after 60 days without activity. The daily run-record commit keeps the repo active.
- Collate reads BigQuery through a read-only service-account key. Record it in the vendor-risk tool.
