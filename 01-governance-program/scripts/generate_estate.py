#!/usr/bin/env python3
"""
Generate the synthetic Empire City Taxi Co. (ECT) data estate as CSV files.

These are the *sensitive* tables that surround the real NYC-taxi trip data:
riders, rider payment cards, trip surveys, drivers, employees, financials, and
marketing. They carry deliberately seeded classification traps and data-quality
issues. The real operational trips come from the public NYC TLC dataset via
pull_trip_sample.sql — the IDs here are designed to line up with it.

No external dependencies (standard library only). All data is fictional.
"""
import csv, os, random, hashlib, datetime as dt

random.seed(42)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(OUT, exist_ok=True)

# Shared with pull_trip_sample.sql — keep these in sync.
TRIP_SAMPLE_SIZE = 100000   # trips get trip_id 1..TRIP_SAMPLE_SIZE in the SQL
N_DRIVERS = 300
N_RIDERS = 2000

FIRST = ["Ava","Liam","Noah","Emma","Olivia","Mia","Lucas","Ethan","Sofia","Aria","James",
         "Isabella","Mateo","Harper","Elijah","Amara","Chen","Priya","Omar","Yuki","Dmitri","Fatima"]
LAST = ["Gray","Nguyen","Patel","Johnson","Garcia","Kim","Okafor","Rossi","Hassan","Silva","Walker",
        "Brooks","Castillo","Haddad","Lindqvist","Mbeki","Tanaka","Novak","Reyes","Cohen","Ivanov","Diallo"]
DEPTS = ["Engineering","Driver Operations","Finance","Support","Marketing","People Ops","Security"]
TITLES = ["Analyst","Manager","Engineer","Specialist","Lead","Coordinator","Director"]
CHANNELS = ["email","paid_social","search","referral","out_of_home"]
BG_STATUS = ["clear","pending","flagged"]

def phone(): return f"{random.randint(200,989)}-{random.randint(200,989)}-{random.randint(1000,9999)}"
def ssn(): return f"{random.randint(100,899):03d}-{random.randint(10,99):02d}-{random.randint(1000,9999):04d}"
def pan(): return " ".join(f"{random.randint(0,9999):04d}" for _ in range(4))
def rand_date(a=1460,b=0): return (dt.date.today()-dt.timedelta(days=random.randint(b,a))).isoformat()
def ts(d=400): return (dt.datetime.now()-dt.timedelta(days=random.randint(0,d),seconds=random.randint(0,86400))).strftime("%Y-%m-%d %H:%M:%S")
def write(name, header, rows):
    p = os.path.join(OUT, f"{name}.csv")
    with open(p,"w",newline="") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f"  {name:20s} {len(rows):5d} rows"); return len(rows)

seed = {}

# -------------------------------------------------------------- drivers (PII)
drivers=[]
seed["driver_bad_ssn"]=seed["driver_null_tlc"]=seed["driver_bad_payout"]=0
for i in range(1, N_DRIVERS+1):
    fn,ln=random.choice(FIRST),random.choice(LAST)
    s=ssn()
    if random.random()<0.04: s=s.replace("-",""); seed["driver_bad_ssn"]+=1          # SEED validity
    tlc=f"TLC{random.randint(100000,999999)}"
    if random.random()<0.03: tlc=""; seed["driver_null_tlc"]+=1                        # SEED completeness
    payout=f"{random.randint(10**8,10**9-1)}"                                          # 9-digit acct
    if random.random()<0.03: payout=payout[:5]; seed["driver_bad_payout"]+=1           # SEED validity (too short)
    bg=random.choice(BG_STATUS)
    if random.random()<0.15: bg=bg.upper() if random.random()<.5 else bg.capitalize()  # SEED consistency
    drivers.append([i,fn,ln,tlc,s,phone(),f"{random.randint(1,9999)} {random.choice(LAST)} Ave, NY",
                    payout,bg,rand_date(2200,60)])
write("drivers",["driver_id","first_name","last_name","tlc_license","ssn","phone",
                 "home_address","payout_bank_account","background_check_status","hired_at"],drivers)

# -------------------------------------------------------------- riders (PII)
riders=[]; used=set(); seed["rider_null_email"]=seed["rider_bad_email"]=seed["rider_dup_email"]=0
for i in range(1, N_RIDERS+1):
    fn,ln=random.choice(FIRST),random.choice(LAST)
    em=f"{fn.lower()}.{ln.lower()}{i}@example.com"
    r=random.random()
    if r<0.03: em=""; seed["rider_null_email"]+=1
    elif r<0.05: em=em.replace("@","."); seed["rider_bad_email"]+=1
    if used and random.random()<0.015: em=random.choice(list(used)); seed["rider_dup_email"]+=1
    if em: used.add(em)
    riders.append([i,fn,ln,em,phone(),f"{random.randint(1,9999)} {random.choice(LAST)} St, NY",rand_date()])
write("riders",["rider_id","first_name","last_name","email","phone","home_address","created_at"],riders)

# -------------------------------------------------------------- rider_cards (PCI)
cards=[]; seed["card_bad_len"]=0
for i in range(1, 1801):
    rid=random.randint(1,N_RIDERS)
    num=pan()
    if random.random()<0.03: num=num[:9]; seed["card_bad_len"]+=1                      # SEED validity (not 16 digits)
    exp=f"{random.randint(1,12):02d}/{random.randint(23,30)}"
    fn,ln=random.choice(FIRST),random.choice(LAST)
    cards.append([100000+i,rid,num,exp,f"{fn} {ln}"])
write("rider_cards",["card_id","rider_id","card_number","card_expiry","cardholder_name"],cards)

# -------------------------------------------------------------- trip_surveys (free-text PII trap)
surveys=[]; seed["survey_bad_rating"]=seed["survey_orphan_trip"]=seed["survey_pii_in_comment"]=0
good=["Great driver, smooth ride.","Clean car, on time.","Driver took a long route.","Friendly and quick.",
      "Car smelled of smoke.","Perfect, thank you!","A bit of a bumpy ride.","Excellent service."]
for i in range(1, 3001):
    tid=random.randint(1,TRIP_SAMPLE_SIZE)
    if random.random()<0.02: tid=TRIP_SAMPLE_SIZE+random.randint(1,5000); seed["survey_orphan_trip"]+=1  # SEED integrity
    rid=random.randint(1,N_RIDERS)
    rating=random.randint(1,5)
    if random.random()<0.02: rating=random.choice([0,6,9,-1]); seed["survey_bad_rating"]+=1  # SEED range
    c=random.choice(good)
    if random.random()<0.03:  # SEED free-text PII (DLP / classification trap)
        c=f"Call me at {phone()} or {random.choice(FIRST).lower()}@example.com about lost item."
        seed["survey_pii_in_comment"]+=1
    surveys.append([900000+i,tid,rid,rating,c,ts(300)])
write("trip_surveys",["survey_id","trip_id","rider_id","rating","comment","submitted_at"],surveys)

# -------------------------------------------------------------- employees (HR, Secret/Confidential)
emps=[]; used_e=set(); seed["emp_bad_ssn"]=seed["emp_neg_salary"]=seed["emp_dup_email"]=0
for i in range(1, 151):
    fn,ln=random.choice(FIRST),random.choice(LAST)
    em=f"{fn.lower()}.{ln.lower()}@empirecitytaxi.example"
    if used_e and random.random()<0.02: em=random.choice(list(used_e)); seed["emp_dup_email"]+=1
    used_e.add(em)
    s=ssn()
    if random.random()<0.03: s=s.replace("-","."); seed["emp_bad_ssn"]+=1
    sal=random.randint(55000,210000)
    if random.random()<0.02: sal=-sal; seed["emp_neg_salary"]+=1                       # SEED range
    emps.append([3000+i,fn,ln,em,s,random.choice(DEPTS),random.choice(TITLES),sal,
                 random.choice(["exceeds","meets","below","not_rated"]),rand_date(2500,30)])
write("employees",["employee_id","first_name","last_name","email","ssn","department","title",
                   "salary","performance_rating","hired_at"],emps)

# -------------------------------------------------------------- financial_ledger (Confidential)
ledger=[]; seed["ledger_null_account"]=0
accounts=["revenue_rider_fares","revenue_tips","cogs_driver_payouts","opex_marketing","opex_payroll","opex_cloud"]
for yr in (2024,2025):
    for mo in range(1,13):
        for acct in accounts:
            a=acct
            if random.random()<0.02: a=""; seed["ledger_null_account"]+=1
            amt=round(random.uniform(50000,900000),2)
            if a.startswith(("cogs","opex")): amt=-amt
            ledger.append([f"{yr}-{mo:02d}-{accounts.index(acct)}",f"{yr}-{mo:02d}",a,amt,"USD",ts(700)])
write("financial_ledger",["entry_id","period","account","amount","currency","recorded_at"],ledger)

# -------------------------------------------------------------- marketing
segs=[[i,n,d,random.randint(500,40000)] for i,(n,d) in enumerate(
    [("New riders","created_at < 30 days"),("Lapsed","no trip in 90 days"),("Airport frequent","3+ airport trips/mo"),
     ("Night owls","trips after midnight"),("High value","top 10% spend"),("Commuters","weekday AM/PM peaks"),
     ("Weekend","Sat/Sun only"),("Promo responders","redeemed a promo"),("Business","expense-tagged trips"),
     ("Tourists","out-of-state cards"),("Tippers","avg tip > 20%"),("At risk","declining frequency")],start=1)]
write("rider_segments",["segment_id","name","definition","size_estimate"],segs)

camp=[]; seed["campaign_bad_dates"]=0
for i in range(1,41):
    start=dt.date.today()-dt.timedelta(days=random.randint(0,500))
    end=start+dt.timedelta(days=random.randint(7,60))
    if random.random()<0.05: end=start-dt.timedelta(days=random.randint(1,10)); seed["campaign_bad_dates"]+=1  # SEED validity
    camp.append([i,f"Campaign {i}",random.choice(CHANNELS),start.isoformat(),end.isoformat(),
                 random.randint(2000,80000),random.randint(1,12)])
write("marketing_campaigns",["campaign_id","name","channel","start_date","end_date","budget","target_segment_id"],camp)

print("\nSeeded issues (what the DQ checks should catch):")
for k,v in seed.items(): print(f"  {k:24s} {v}")
print(f"\nDone. CSVs in {OUT}")
print(f"Trips come from the public NYC TLC data via pull_trip_sample.sql "
      f"(trip_id 1..{TRIP_SAMPLE_SIZE}, driver_id 1..{N_DRIVERS}, rider_id 1..{N_RIDERS}).")
