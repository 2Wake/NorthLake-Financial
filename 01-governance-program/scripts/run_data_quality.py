#!/usr/bin/env python3
"""
Run data-quality checks against the NorthLake CSV estate and write a
remediation log. Mirrors the rules documented in
governance/data-quality-rules.md (and the BigQuery SQL versions there).

Runs on the generated CSVs so the repo has committed evidence without needing
a live warehouse. Standard library only.

Output: ../data/remediation_log.csv  and a console summary.
"""
import csv, os, re, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CANON_STATUS = {"active", "closed", "suspended"}

def load(name):
    with open(os.path.join(DATA, f"{name}.csv"), newline="") as f:
        return list(csv.DictReader(f))

findings = []
def record(rule_id, dimension, table, column, severity, failed, total, sample, action):
    pct = round(failed / total * 100, 2) if total else 0
    findings.append({
        "rule_id": rule_id, "dimension": dimension, "table": table, "column": column,
        "severity": severity, "failed_rows": failed, "total_rows": total, "fail_pct": pct,
        "sample_offending_value": sample, "recommended_action": action,
    })

cust = load("customers")
acct = load("accounts")
apps = load("lending_applications")

# DQ-01 Completeness: customer email must be present
miss = [r for r in cust if not r["email"].strip()]
record("DQ-01","Completeness","customers","email","High",len(miss),len(cust),
       "(empty)","Backfill from source of record; make email required at intake.")

# DQ-02 Validity: email format
bad = [r for r in cust if r["email"].strip() and not EMAIL_RE.match(r["email"])]
record("DQ-02","Validity","customers","email","Medium",len(bad),len(cust),
       bad[0]["email"] if bad else "-","Add format validation at capture; correct existing malformed values.")

# DQ-03 Uniqueness: duplicate emails
seen, dups = {}, []
for r in cust:
    e = r["email"].strip()
    if not e: continue
    if e in seen: dups.append(e)
    seen[e] = seen.get(e, 0) + 1
record("DQ-03","Uniqueness","customers","email","High",len(dups),len(cust),
       dups[0] if dups else "-","De-duplicate; enforce unique constraint / identity resolution.")

# DQ-04 Validity (range): date_of_birth not in the future
today = dt.date.today()
future = [r for r in cust if r["date_of_birth"] and dt.date.fromisoformat(r["date_of_birth"]) > today]
record("DQ-04","Validity","customers","date_of_birth","High",len(future),len(cust),
       future[0]["date_of_birth"] if future else "-","Reject future DOB at entry; investigate and correct records.")

# DQ-05 Referential integrity: accounts.customer_id must exist in customers
cust_ids = {r["customer_id"] for r in cust}
orphan = [r for r in acct if r["customer_id"] not in cust_ids]
record("DQ-05","Integrity","accounts","customer_id","High",len(orphan),len(acct),
       orphan[0]["customer_id"] if orphan else "-","Enforce FK; reconcile orphaned accounts to a valid customer.")

# DQ-06 Consistency: account status must be one of the canonical lowercase values
inconsistent = [r for r in acct if r["status"] not in CANON_STATUS]
record("DQ-06","Consistency","accounts","status","Medium",len(inconsistent),len(acct),
       inconsistent[0]["status"] if inconsistent else "-","Normalize casing; constrain to a controlled vocabulary.")

# DQ-07 Validity (range): credit_score within 300-850
def as_int(v):
    try: return int(v)
    except: return None
badscore = [r for r in apps if (as_int(r["credit_score"]) is None) or not (300 <= as_int(r["credit_score"]) <= 850)]
record("DQ-07","Validity","lending_applications","credit_score","High",len(badscore),len(apps),
       badscore[0]["credit_score"] if badscore else "-","Range-validate 300-850; quarantine and re-pull invalid scores.")

# DQ-08 Completeness: annual_income present on lending applications
missinc = [r for r in apps if not str(r["annual_income"]).strip()]
record("DQ-08","Completeness","lending_applications","annual_income","Medium",len(missinc),len(apps),
       "(empty)","Require income at application; backfill where lawful.")

# ---- write log + summary
out = os.path.join(DATA, "remediation_log.csv")
cols = ["rule_id","dimension","table","column","severity","failed_rows","total_rows","fail_pct","sample_offending_value","recommended_action"]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(findings)

print(f"{'RULE':7} {'DIMENSION':13} {'TABLE.COLUMN':34} {'SEV':7} {'FAIL':>5} {'PCT':>6}")
print("-"*78)
total_fail = 0
for r in findings:
    total_fail += r["failed_rows"]
    print(f"{r['rule_id']:7} {r['dimension']:13} {r['table']+'.'+r['column']:34} {r['severity']:7} {r['failed_rows']:5} {r['fail_pct']:5}%")
print("-"*78)
print(f"{len(findings)} rules run, {total_fail} total failing rows. Log -> {out}")
