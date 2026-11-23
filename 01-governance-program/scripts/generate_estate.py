#!/usr/bin/env python3
"""
Generate the synthetic NorthLake Financial data estate as CSV files.

Creates a small, realistic fintech dataset across several tables, with
*intentionally seeded* data-quality issues and sensitive columns so that the
data-governance exercise has real things to classify and real problems to find
and remediate. No external dependencies (standard library only).

Output: CSV files in ../data/ , one per table, plus a load-ready schema note.
All data is fictional and randomly generated.
"""
import csv, os, random, hashlib, datetime as dt

random.seed(42)  # reproducible
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(OUT, exist_ok=True)

FIRST = ["Ava","Liam","Noah","Emma","Olivia","Mia","Lucas","Ethan","Sofia","Aria",
         "James","Isabella","Mateo","Harper","Elijah","Amara","Chen","Priya","Omar","Yuki"]
LAST = ["Gray","Nguyen","Patel","Johnson","Garcia","Kim","Okafor","Rossi","Hassan","Silva",
        "Walker","Brooks","Castillo","Haddad","Lindqvist","Mbeki","Tanaka","Novak","Reyes","Cohen"]
MERCHANTS = ["Blue Bottle","Target","Shell","Delta Air","Whole Foods","Steam","Uber","CVS",
             "Home Depot","Netflix","Spotify","Costco","Apple","Kroger","Chevron"]
MCC = ["5812","5411","5541","4511","5912","5732","4121","5200","5815","5411"]
BANKS = ["Summit Credit Union","Harbor Community Bank","Cascade Savings","Meridian Trust",
         "Prairie State Bank","Gulf Coast FCU","Granite Mutual","Lakeside Bank"]
ACCT_TYPES = ["checking","savings","credit","loan"]
# Deliberately inconsistent casing is seeded below for the status field.
STATUSES = ["active","closed","suspended"]
ROLES = ["admin","analyst","viewer","config_manager"]

def email(fn, ln, i):
    return f"{fn.lower()}.{ln.lower()}{i}@example.com"

def phone():
    return f"{random.randint(200,989)}-{random.randint(200,989)}-{random.randint(1000,9999)}"

def ssn():
    return f"{random.randint(100,899):03d}-{random.randint(10,99):02d}-{random.randint(1000,9999):04d}"

def pan():
    # fake 16-digit card number (Restricted / cardholder data)
    return " ".join(f"{random.randint(0,9999):04d}" for _ in range(4))

def rand_date(start_days_ago=1460, end_days_ago=0):
    d = dt.date.today() - dt.timedelta(days=random.randint(end_days_ago, start_days_ago))
    return d.isoformat()

def ts(days_back=400):
    base = dt.datetime.now() - dt.timedelta(days=random.randint(0, days_back),
                                            seconds=random.randint(0, 86400))
    return base.strftime("%Y-%m-%d %H:%M:%S")

def write(name, header, rows):
    path = os.path.join(OUT, f"{name}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name:22s} {len(rows):5d} rows -> {path}")
    return len(rows)

# ------------------------------------------------------------------ customers
N_CUST = 500
customers, cust_ids = [], []
seeded = {"null_email":0,"bad_email":0,"future_dob":0,"dup_email":0}
used_emails = set()
for i in range(1, N_CUST+1):
    fn, ln = random.choice(FIRST), random.choice(LAST)
    cid = 10000 + i
    cust_ids.append(cid)
    em = email(fn, ln, i)
    # SEED: 3% null email (completeness), 2% malformed email (validity)
    r = random.random()
    if r < 0.03:
        em = ""; seeded["null_email"] += 1
    elif r < 0.05:
        em = em.replace("@", "."); seeded["bad_email"] += 1
    # SEED: 1.5% duplicate email (uniqueness)
    if used_emails and random.random() < 0.015:
        em = random.choice(list(used_emails)); seeded["dup_email"] += 1
    if em:
        used_emails.add(em)
    # SEED: 1% date_of_birth in the future (validity / range)
    if random.random() < 0.01:
        dob = (dt.date.today() + dt.timedelta(days=random.randint(30,900))).isoformat()
        seeded["future_dob"] += 1
    else:
        dob = rand_date(29000, 6570)  # ~18 to ~80 yrs
    customers.append([cid, fn, ln, em, phone(), ssn(), dob,
                      f"{random.randint(1,9999)} {random.choice(LAST)} St",
                      random.choice(["GA","CA","NY","TX","WA","IL","FL"]), rand_date()])
write("customers",
      ["customer_id","first_name","last_name","email","phone","ssn","date_of_birth",
       "street_address","state","created_at"], customers)

# ------------------------------------------------------------------ bank_clients
bank_ids = []
bank_rows = []
for i, bn in enumerate(BANKS, start=1):
    bid = 500 + i
    bank_ids.append(bid)
    api_key = hashlib.sha256(f"{bn}{i}".encode()).hexdigest()
    bank_rows.append([bid, bn, f"{random.randint(100000000,399999999)}",
                      random.choice(["standard","premium","enterprise"]), api_key])
write("bank_clients",
      ["bank_id","bank_name","routing_number","contract_tier","api_key_hash"], bank_rows)

# ------------------------------------------------------------------ accounts
accounts, acct_ids = [], []
seed_orphan = 0
for i in range(1, 801):
    aid = 700000 + i
    acct_ids.append(aid)
    # SEED: 2% orphaned customer_id (referential integrity)
    if random.random() < 0.02:
        cid = 999999; seed_orphan += 1
    else:
        cid = random.choice(cust_ids)
    bal = round(random.uniform(-500, 85000), 2)
    # SEED: inconsistent status casing (consistency)
    st = random.choice(STATUSES)
    if random.random() < 0.2:
        st = st.upper() if random.random() < 0.5 else st.capitalize()
    accounts.append([aid, cid, random.choice(bank_ids), random.choice(ACCT_TYPES),
                     bal, rand_date(), st])
write("accounts",
      ["account_id","customer_id","bank_id","account_type","balance","opened_at","status"],
      accounts)

# ------------------------------------------------------------------ cards
cards = []
for i in range(1, 601):
    aid = random.choice(acct_ids)
    fn = random.choice(FIRST); ln = random.choice(LAST)
    exp = f"{random.randint(1,12):02d}/{random.randint(26,31)}"
    cards.append([900000+i, aid, pan(), exp, f"{fn} {ln}"])
write("cards", ["card_id","account_id","card_number","card_expiry","cardholder_name"], cards)

# ------------------------------------------------------------------ transactions
txns = []
for i in range(1, 4001):
    aid = random.choice(acct_ids)
    amt = round(random.uniform(1.00, 2500.00), 2)
    # SEED: 0.5% negative amount on a 'purchase' (range/validity)
    if random.random() < 0.005:
        amt = -amt
    mi = random.randrange(len(MERCHANTS))
    txns.append([5_000_000+i, aid, amt, "USD", MERCHANTS[mi], MCC[mi % len(MCC)], ts(),
                 random.choice(["settled","pending","declined"])])
write("transactions",
      ["txn_id","account_id","amount","currency","merchant_name","merchant_category","txn_timestamp","status"],
      txns)

# ------------------------------------------------------------------ lending_applications
apps = []
seed_score = 0
for i in range(1, 701):
    cid = random.choice(cust_ids)
    # SEED: 1.5% credit_score out of valid 300-850 range (range check)
    if random.random() < 0.015:
        score = random.choice([0, 1200, -50, 999]); seed_score += 1
    else:
        score = random.randint(300, 850)
    income = random.choice([random.randint(25000, 240000), None]) if random.random() < 0.04 else random.randint(25000, 240000)
    apps.append([800000+i, cid, income if income is not None else "", score,
                 random.randint(2000, 75000),
                 random.choice(["approved","declined","manual_review"]), ts(900)])
write("lending_applications",
      ["app_id","customer_id","annual_income","credit_score","loan_amount","decision","decision_at"],
      apps)

# ------------------------------------------------------------------ console_users (workforce)
users = []
for i in range(1, 121):
    fn, ln = random.choice(FIRST), random.choice(LAST)
    users.append([4000+i, random.choice(bank_ids), f"{fn.lower()}.{ln.lower()}@bankclient.com",
                  random.choice(ROLES), ts(120)])
write("console_users", ["user_id","bank_id","email","role","last_login"], users)

# ------------------------------------------------------------------ audit_log
logs = []
actions = ["login","export_report","update_config","create_user","view_customer","api_call"]
for i in range(1, 2001):
    logs.append([7_000_000+i, random.choice([u[0] for u in users]), random.choice(actions),
                 random.choice(["customers","transactions","accounts","reports","settings"]), ts(120)])
write("audit_log", ["log_id","user_id","action","resource","event_timestamp"], logs)

print("\nSeeded data-quality issues (the ones the DQ checks should catch):")
for k, v in {**seeded, "orphan_accounts": seed_orphan, "bad_credit_score": seed_score}.items():
    print(f"  {k:20s} {v}")
print(f"\nDone. CSVs written to {OUT}")
