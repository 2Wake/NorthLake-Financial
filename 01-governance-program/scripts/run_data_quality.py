#!/usr/bin/env python3
"""
Run data-quality checks against the ECT synthetic CSV estate and write a
remediation log. Mirrors governance/data-quality-rules.md (which also has the
BigQuery SQL, including rules for the real `trips` table). Standard library only.

Output: ../data/remediation_log.csv  and a console summary.
"""
import csv, os, re, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SSN_RE = re.compile(r"^\d{3}-\d{2}-\d{4}$")
PHONE_RE = re.compile(r"\d{3}-\d{3}-\d{4}")
EMAIL_ANY = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
TRIP_SAMPLE_SIZE = 100000
BG_CANON = {"clear","pending","flagged"}

def load(n):
    with open(os.path.join(DATA,f"{n}.csv"),newline="") as f: return list(csv.DictReader(f))

findings=[]
def rec(rid,dim,tbl,col,sev,failed,total,sample,action):
    findings.append({"rule_id":rid,"dimension":dim,"table":tbl,"column":col,"severity":sev,
        "failed_rows":failed,"total_rows":total,"fail_pct":round(failed/total*100,2) if total else 0,
        "sample_offending_value":sample,"recommended_action":action})

riders=load("riders"); drivers=load("drivers"); cards=load("rider_cards")
surveys=load("trip_surveys"); emps=load("employees"); camp=load("marketing_campaigns")

# riders.email
miss=[r for r in riders if not r["email"].strip()]
rec("DQ-01","Completeness","riders","email","High",len(miss),len(riders),"(empty)","Require email at signup; backfill from source.")
bad=[r for r in riders if r["email"].strip() and not EMAIL_RE.match(r["email"])]
rec("DQ-02","Validity","riders","email","Medium",len(bad),len(riders),bad[0]["email"] if bad else "-","Validate format at capture; correct existing.")
seen={}; dups=[]
for r in riders:
    e=r["email"].strip()
    if e: dups.append(e) if e in seen else None; seen[e]=1
rec("DQ-03","Uniqueness","riders","email","High",len(dups),len(riders),dups[0] if dups else "-","De-duplicate; enforce unique constraint.")

# drivers
bs=[d for d in drivers if not SSN_RE.match(d["ssn"])]
rec("DQ-04","Validity","drivers","ssn","High",len(bs),len(drivers),bs[0]["ssn"] if bs else "-","Enforce SSN format; quarantine and correct.")
nt=[d for d in drivers if not d["tlc_license"].strip()]
rec("DQ-05","Completeness","drivers","tlc_license","High",len(nt),len(drivers),"(empty)","TLC license is mandatory to drive; block activation until present.")
bg=[d for d in drivers if d["background_check_status"] not in BG_CANON]
rec("DQ-06","Consistency","drivers","background_check_status","Medium",len(bg),len(drivers),bg[0]["background_check_status"] if bg else "-","Normalize to controlled vocabulary {clear,pending,flagged}.")

# rider_cards
bl=[c for c in cards if len(c["card_number"].replace(" ",""))!=16]
rec("DQ-07","Validity","rider_cards","card_number","High",len(bl),len(cards),"(masked)","Validate PAN length/Luhn; this is PCI data — handle via the processor, do not store raw.")

# trip_surveys
br=[s for s in surveys if not s["rating"].lstrip("-").isdigit() or not (1<=int(s["rating"])<=5)]
rec("DQ-08","Validity","trip_surveys","rating","Medium",len(br),len(surveys),br[0]["rating"] if br else "-","Constrain rating to 1-5 at capture.")
orf=[s for s in surveys if not (1<=int(s["trip_id"])<=TRIP_SAMPLE_SIZE)]
rec("DQ-09","Integrity","trip_surveys","trip_id","High",len(orf),len(surveys),orf[0]["trip_id"] if orf else "-","Enforce FK to trips; reconcile orphaned surveys.")
pii=[s for s in surveys if EMAIL_ANY.search(s["comment"]) or PHONE_RE.search(s["comment"])]
rec("DQ-10","Privacy (DLP)","trip_surveys","comment","High",len(pii),len(surveys),"(PII redacted)","Free-text contains PII — classify Confidential; add DLP scan/redaction; restrict access.")

# employees
def i_(v):
    try: return int(v)
    except: return None
ns=[e for e in emps if (i_(e["salary"]) is None) or i_(e["salary"])<=0]
rec("DQ-11","Validity","employees","salary","Medium",len(ns),len(emps),ns[0]["salary"] if ns else "-","Salary must be positive; correct payroll feed.")

# campaigns
bd=[c for c in camp if c["end_date"]<c["start_date"]]
rec("DQ-12","Validity","marketing_campaigns","end_date","Low",len(bd),len(camp),bd[0]["end_date"] if bd else "-","End date must be >= start date.")

out=os.path.join(DATA,"remediation_log.csv")
cols=["rule_id","dimension","table","column","severity","failed_rows","total_rows","fail_pct","sample_offending_value","recommended_action"]
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(findings)

print(f"{'RULE':7} {'DIMENSION':14} {'TABLE.COLUMN':38} {'SEV':7} {'FAIL':>5} {'PCT':>6}")
print("-"*82); tot=0
for r in findings:
    tot+=r["failed_rows"]
    print(f"{r['rule_id']:7} {r['dimension']:14} {r['table']+'.'+r['column']:38} {r['severity']:7} {r['failed_rows']:5} {r['fail_pct']:5}%")
print("-"*82); print(f"{len(findings)} rules, {tot} failing rows. Log -> {out}")
print("\nThe real `trips` table (public NYC TLC data) is checked separately via the BigQuery SQL in data-quality-rules.md.")
