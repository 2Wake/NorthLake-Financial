"""Day-by-day simulation of Empire City Taxi.

The simulation always replays from EPOCH, so the state on any date (who is employed,
which riders are active, ...) is fixed. Each day's batch holds only the records created
or changed that day, like an incremental extract from each source system. Nothing is
ever deleted: terminations, closures and removals arrive as changed rows.

Each part of the business (HR, riders, marketing, ...) draws from its own random stream
keyed by date, so adding a feature to one part doesn't shift the data of the others.
"""
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from . import fakes
from .config import (APP_BOOKED_SHARE, DEFECT_RATES as DR, EPOCH, RATES, SURVEY_SHARE,
                     tlc_date_for)
from .fakes import poisson, rng

NY = ZoneInfo("America/New_York")

CORP_DEPARTMENTS = ["Engineering", "Finance", "Customer Support", "Marketing", "People",
                    "Security", "Operations", "Data & Analytics"]
TITLES = ["Analyst", "Specialist", "Engineer", "Coordinator", "Manager", "Lead", "Director"]
RATINGS = ["exceeds", "meets", "meets", "meets", "below", "not_rated"]
CHANNELS = ["email", "paid_social", "search", "referral", "out_of_home", "push"]
CAMPAIGN_THEMES = ["Airport Express", "Late Night Safe Ride", "Commuter Saver", "Weekend Out",
                   "Welcome Back", "Refer a Friend", "Rainy Day", "Holiday Travel", "Business Rides"]
SEGMENTS = [
    ("New riders", "created_at < 30 days"), ("Lapsed", "no trip in 90 days"),
    ("Airport frequent", "3+ airport trips/mo"), ("Night owls", "trips after midnight"),
    ("High value", "top 10% spend"), ("Commuters", "weekday AM/PM peaks"),
    ("Weekend", "Sat/Sun only"), ("Promo responders", "redeemed a promo"),
    ("Business", "expense-tagged trips"), ("Tourists", "out-of-state cards"),
    ("Tippers", "avg tip > 20%"), ("At risk", "declining frequency"),
]
LEDGER_ACCOUNTS = ["revenue_rider_fares", "revenue_tips", "cogs_driver_payouts",
                   "opex_marketing", "opex_payroll", "opex_cloud"]
SURVEY_COMMENTS = ["Great driver, smooth ride.", "Clean car, on time.", "Driver took a long route.",
                   "Friendly and quick.", "Car smelled of smoke.", "Perfect, thank you!",
                   "A bit of a bumpy ride.", "Excellent service.", "", ""]


class Simulation:
    def __init__(self):
        self.employees: dict[str, dict] = {}
        self.drivers: dict[str, dict] = {}
        self.riders: dict[str, dict] = {}
        self.cards: dict[str, dict] = {}
        self.campaigns: dict[str, dict] = {}
        self.segments: dict[str, dict] = {}
        self.seq = defaultdict(int)
        self.agenda = defaultdict(list)       # date -> [(action, id)] scheduled follow-ups
        self.rider_emails: list[str] = []
        self.employee_emails: list[str] = []
        self.day: date | None = None
        self._out = None
        self._defects = None

    # ------------------------------------------------------------------ plumbing
    def _next_id(self, prefix: str, base: int) -> str:
        self.seq[prefix] += 1
        return f"{prefix}{base + self.seq[prefix]}"

    def _ts(self, r, day: date | None = None, lo: int = 6, hi: int = 22) -> str:
        """A random NYC-local timestamp on `day` (default: today), as ISO 8601 with offset."""
        moment = datetime.combine(day or self.day, time()) + timedelta(seconds=r.randint(lo * 3600, hi * 3600 - 1))
        return moment.replace(tzinfo=NY).isoformat()

    def _touch(self, table: str, key: str, rec: dict) -> None:
        """Record that `rec` was created or changed today (latest image wins)."""
        if self._out is not None:
            self._out[table][key] = {k: v for k, v in rec.items() if not k.startswith("_")}

    def _plant(self, r, defect: str) -> bool:
        return r.random() < DR[defect]

    def _log_defect(self, table: str, record_id: str, column: str, code: str) -> None:
        if self._defects is not None:
            self._defects.append({"table_name": table, "record_id": record_id,
                                  "column_name": column, "defect_code": code})

    @staticmethod
    def _active(records: dict, field: str, value: str = "active") -> list[str]:
        return [k for k, v in records.items() if v[field] == value]

    # ------------------------------------------------------------------ one day
    def step(self, day: date, emit: bool = False, tlc_rows: list[dict] | None = None):
        """Advance the simulation through `day`. If `emit`, return that day's batch."""
        self.day = day
        self._out = defaultdict(dict) if emit else None
        self._defects = [] if emit else None
        if day == EPOCH:
            self._initial_population()
        else:
            self._run_agenda()
            self._people(rng("people", day))
            self._riders(rng("riders", day))
            self._marketing(rng("marketing", day))
            self._finance(rng("finance", day))
        if not emit:
            return None
        if tlc_rows is not None:
            self._trips(tlc_rows)
        batch = {table: list(rows.values()) for table, rows in self._out.items()}
        stamp = f"{day:%Y%m%d}"
        batch["gov_planted_defects"] = [
            {"defect_id": f"DEF{stamp}{i:04d}", **d} for i, d in enumerate(self._defects, 1)]
        return batch

    # ------------------------------------------------------------------ people (HR + fleet)
    def _new_employee(self, r, hired: date, driver: bool) -> dict:
        eid = self._next_id("EMP", 10000)
        first, last = fakes.person(r)
        email = f"{first}.{last}@empirecitytaxi.example".lower().replace(" ", "").replace("'", "")
        if email in self.employee_emails:
            email = email.replace("@", f"{self.seq['EMP']}@")
        defects = []
        if self.employee_emails and self._plant(r, "employee_email_duplicate"):
            email = r.choice(self.employee_emails)
            defects.append(("email", "employee_email_duplicate"))
        self.employee_emails.append(email)
        clean_ssn = fakes.ssn(r)
        ssn = clean_ssn
        if self._plant(r, "employee_ssn_dots"):
            ssn = clean_ssn.replace("-", ".")
            defects.append(("ssn", "employee_ssn_dots"))
        if driver:
            department, title, pay_type, salary = "Driver Operations", "Driver", "commission", None
        else:
            department, title, pay_type = r.choice(CORP_DEPARTMENTS), r.choice(TITLES), "salaried"
            salary = r.randint(55, 210) * 1000 + r.randint(0, 999)
            if self._plant(r, "employee_salary_negative"):
                salary = -salary
                defects.append(("salary", "employee_salary_negative"))
        rec = {
            "employee_id": eid, "first_name": first, "last_name": last, "email": email, "ssn": ssn,
            "department": department, "title": title, "pay_type": pay_type, "salary": salary,
            "performance_rating": "not_rated" if hired >= self.day - timedelta(days=90) else r.choice(RATINGS),
            "hired_at": hired.isoformat(), "employment_status": "active", "terminated_at": None,
            "record_updated_at": self._ts(r), "_clean_ssn": clean_ssn,
        }
        self.employees[eid] = rec
        self._touch("hris_employees", eid, rec)
        for column, code in defects:
            self._log_defect("hris_employees", eid, column, code)
        return rec

    def _terminate_employee(self, r, eid: str, ts: str) -> None:
        emp = self.employees[eid]
        emp.update(employment_status="terminated", terminated_at=self.day.isoformat(), record_updated_at=ts)
        self._touch("hris_employees", eid, emp)

    def _background_status(self, r, did: str, status: str) -> str:
        if self._plant(r, "driver_background_status_case"):
            self._log_defect("fleet_drivers", did, "background_check_status", "driver_background_status_case")
            return status.upper() if r.random() < 0.5 else status.capitalize()
        return status

    def _hire_driver(self, r, hired: date, onboarded: bool) -> None:
        emp = self._new_employee(r, hired, driver=True)
        did = self._next_id("DRV", 10000)
        ssn = emp["_clean_ssn"]
        if self._plant(r, "driver_ssn_no_dashes"):
            ssn = ssn.replace("-", "")
            self._log_defect("fleet_drivers", did, "ssn", "driver_ssn_no_dashes")
        tlc = f"TLC{r.randint(100000, 999999)}"
        if self._plant(r, "driver_tlc_license_missing"):
            tlc = None
            self._log_defect("fleet_drivers", did, "tlc_license", "driver_tlc_license_missing")
        payout = str(r.randint(10**8, 10**9 - 1))
        if self._plant(r, "driver_payout_account_short"):
            payout = payout[:5]
            self._log_defect("fleet_drivers", did, "payout_bank_account", "driver_payout_account_short")
        ts = emp["record_updated_at"]
        if onboarded:
            background, status = self._background_status(r, did, "clear"), "active"
        else:
            background, status = "pending", "onboarding"
            self.agenda[self.day + timedelta(days=r.randint(3, 12))].append(("background_result", did))
        self.drivers[did] = {
            "driver_id": did, "employee_id": emp["employee_id"], "first_name": emp["first_name"],
            "last_name": emp["last_name"], "tlc_license": tlc, "ssn": ssn, "phone": fakes.phone(r),
            "home_address": fakes.nyc_address(r), "payout_bank_account": payout,
            "background_check_status": background, "driver_status": status, "hired_at": hired.isoformat(),
            "status_changed_at": ts, "record_updated_at": ts,
        }
        self._touch("fleet_drivers", did, self.drivers[did])

    def _set_driver_status(self, r, did: str, status: str, **changes) -> str:
        drv = self.drivers[did]
        ts = self._ts(r)
        drv.update(driver_status=status, status_changed_at=ts, record_updated_at=ts, **changes)
        self._touch("fleet_drivers", did, drv)
        return ts

    def _run_agenda(self) -> None:
        r = rng("agenda", self.day)
        for action, did in self.agenda.pop(self.day, []):
            drv = self.drivers[did]
            if action == "background_result" and drv["driver_status"] == "onboarding":
                if r.random() < 0.9:
                    self._set_driver_status(r, did, "active",
                                            background_check_status=self._background_status(r, did, "clear"))
                else:
                    ts = self._set_driver_status(r, did, "inactive",
                                                 background_check_status=self._background_status(r, did, "flagged"))
                    self._terminate_employee(r, drv["employee_id"], ts)
            elif action == "reinstate" and drv["driver_status"] == "suspended":
                self._set_driver_status(r, did, "active")

    def _people(self, r) -> None:
        for _ in range(poisson(r, RATES["corporate_hires"])):
            self._new_employee(r, self.day, driver=False)
        for _ in range(poisson(r, RATES["corporate_terminations"])):
            corporate = [k for k, v in self.employees.items()
                         if v["employment_status"] == "active" and v["pay_type"] != "commission"]
            if corporate:
                self._terminate_employee(r, r.choice(corporate), self._ts(r))
        for _ in range(poisson(r, RATES["driver_hires"])):
            self._hire_driver(r, self.day, onboarded=False)
        for _ in range(poisson(r, RATES["driver_terminations"])):
            active = self._active(self.drivers, "driver_status")
            if active:
                did = r.choice(active)
                ts = self._set_driver_status(r, did, "inactive")
                self._terminate_employee(r, self.drivers[did]["employee_id"], ts)
        for _ in range(poisson(r, RATES["driver_suspensions"])):
            active = self._active(self.drivers, "driver_status")
            if active:
                did = r.choice(active)
                self._set_driver_status(r, did, "suspended")
                self.agenda[self.day + timedelta(days=r.randint(7, 30))].append(("reinstate", did))
        if (self.day.month, self.day.day) == (3, 1):  # annual review: new ratings and merit raises
            for eid, emp in self.employees.items():
                if emp["employment_status"] == "active" and emp["pay_type"] == "salaried":
                    emp["performance_rating"] = r.choice(RATINGS)
                    emp["salary"] = round(emp["salary"] * (1 + r.choice([0, 0.02, 0.03, 0.04, 0.06])))
                    emp["record_updated_at"] = self._ts(r)
                    self._touch("hris_employees", eid, emp)

    # ------------------------------------------------------------------ riders and cards
    def _new_rider(self, r, created_ts: str) -> str:
        rid = self._next_id("RDR", 100000)
        first, last = fakes.person(r)
        email = f"{first}.{last}{self.seq['RDR']}@example.com".lower().replace(" ", "").replace("'", "")
        roll = r.random()
        if roll < DR["rider_email_missing"]:
            email, code = None, "rider_email_missing"
        elif roll < DR["rider_email_missing"] + DR["rider_email_invalid"]:
            email, code = email.replace("@", "."), "rider_email_invalid"
        elif self.rider_emails and roll < sum(DR[k] for k in ("rider_email_missing", "rider_email_invalid",
                                                              "rider_email_duplicate")):
            email, code = r.choice(self.rider_emails), "rider_email_duplicate"
        else:
            code = None
        if email and "@" in email:
            self.rider_emails.append(email)
        self.riders[rid] = {
            "rider_id": rid, "first_name": first, "last_name": last, "email": email,
            "phone": fakes.phone(r), "home_address": fakes.nyc_address(r), "created_at": created_ts,
            "account_status": "active", "closed_at": None, "record_updated_at": self._ts(r),
        }
        self._touch("app_riders", rid, self.riders[rid])
        if code:
            self._log_defect("app_riders", rid, "email", code)
        return rid

    def _add_card(self, r, rid: str, added_ts: str | None = None) -> None:
        cid = self._next_id("CRD", 100000)
        number = fakes.card_number(r)
        if self._plant(r, "card_number_truncated"):
            number = number[:9]
            self._log_defect("payments_rider_cards", cid, "card_number", "card_number_truncated")
        rider = self.riders[rid]
        holder = (f"{rider['first_name']} {rider['last_name']}" if r.random() < 0.9
                  else " ".join(fakes.person(r)))
        ts = added_ts or self._ts(r)
        self.cards[cid] = {
            "card_id": cid, "rider_id": rid, "card_number": number,
            "card_expiry": f"{r.randint(1, 12):02d}/{self.day.year % 100 + r.randint(1, 5)}",
            "cardholder_name": holder, "card_status": "active", "added_at": ts,
            "record_updated_at": self._ts(r),
        }
        self._touch("payments_rider_cards", cid, self.cards[cid])

    def _remove_card(self, r, cid: str) -> None:
        card = self.cards[cid]
        card.update(card_status="removed", record_updated_at=self._ts(r))
        self._touch("payments_rider_cards", cid, card)

    def _riders(self, r) -> None:
        for _ in range(poisson(r, RATES["rider_signups"])):
            rid = self._new_rider(r, self._ts(r, lo=0, hi=24))
            if r.random() < 0.85:
                self._add_card(r, rid)
        active = self._active(self.riders, "account_status")
        for _ in range(poisson(r, RATES["rider_closures"])):
            rid = r.choice(active)
            rider = self.riders[rid]
            ts = self._ts(r)
            rider.update(account_status="closed", closed_at=ts, record_updated_at=ts)
            self._touch("app_riders", rid, rider)
            for cid, card in self.cards.items():
                if card["rider_id"] == rid and card["card_status"] == "active":
                    self._remove_card(r, cid)
        active = self._active(self.riders, "account_status")
        for _ in range(poisson(r, RATES["rider_profile_updates"])):
            rider = self.riders[r.choice(active)]
            if r.random() < 0.5:
                rider["phone"] = fakes.phone(r)
            else:
                rider["home_address"] = fakes.nyc_address(r)
            rider["record_updated_at"] = self._ts(r)
            self._touch("app_riders", rider["rider_id"], rider)
        for _ in range(poisson(r, RATES["extra_cards"])):
            self._add_card(r, r.choice(active))
        active_cards = self._active(self.cards, "card_status")
        for _ in range(poisson(r, RATES["card_removals"])):
            self._remove_card(r, r.choice(active_cards))

    # ------------------------------------------------------------------ marketing and finance
    def _new_campaign(self, r, start: date) -> None:
        cid = self._next_id("CMP", 1000)
        end = start + timedelta(days=r.randint(7, 60))
        if self._plant(r, "campaign_end_before_start"):
            end = start - timedelta(days=r.randint(1, 10))
            self._log_defect("app_marketing_campaigns", cid, "end_date", "campaign_end_before_start")
        self.campaigns[cid] = {
            "campaign_id": cid, "name": f"{r.choice(CAMPAIGN_THEMES)} {start:%b %Y}",
            "channel": r.choice(CHANNELS), "start_date": start.isoformat(), "end_date": end.isoformat(),
            "budget": r.randint(20, 800) * 100, "target_segment_id": r.choice(list(self.segments)),
            "record_updated_at": self._ts(r),
        }
        self._touch("app_marketing_campaigns", cid, self.campaigns[cid])

    def _marketing(self, r) -> None:
        for _ in range(poisson(r, RATES["new_campaigns"])):
            self._new_campaign(r, self.day + timedelta(days=r.randint(3, 20)))
        if self.day.day == 1:
            for sid, seg in self.segments.items():
                seg["size_estimate"] = max(100, round(seg["size_estimate"] * r.uniform(0.92, 1.12)))
                seg["record_updated_at"] = self._ts(r)
                self._touch("app_rider_segments", sid, seg)

    def _post_ledger(self, r, year: int, month: int, recorded_ts: str) -> None:
        for i, account in enumerate(LEDGER_ACCOUNTS, 1):
            entry_id = f"JE{year}{month:02d}{i:02d}"
            amount = Decimal(r.randint(5_000_000, 90_000_000)) / 100
            if account.startswith(("cogs", "opex")):
                amount = -amount
            if self._plant(r, "ledger_account_missing"):
                account = None
                self._log_defect("payments_financial_ledger", entry_id, "account", "ledger_account_missing")
            self._touch("payments_financial_ledger", entry_id, {
                "entry_id": entry_id, "period": f"{year}-{month:02d}", "account": account,
                "amount": str(amount), "currency": "USD", "recorded_at": recorded_ts})

    def _finance(self, r) -> None:
        if self.day.day == 3:
            prior = self.day.replace(day=1) - timedelta(days=1)
            self._post_ledger(r, prior.year, prior.month, self._ts(r, lo=9, hi=18))

    # ------------------------------------------------------------------ starting population
    def _initial_population(self) -> None:
        r = rng("initial", EPOCH)
        for _ in range(150):
            self._new_employee(r, EPOCH - timedelta(days=r.randint(30, 2500)), driver=False)
        for _ in range(300):
            self._hire_driver(r, EPOCH - timedelta(days=r.randint(60, 2200)), onboarded=True)
        for _ in range(2000):
            self._new_rider(r, self._ts(r, EPOCH - timedelta(days=r.randint(1, 1460)), lo=0, hi=24))
        rider_ids = list(self.riders)
        for _ in range(1800):
            rid = r.choice(rider_ids)
            self._add_card(r, rid, added_ts=max(self.riders[rid]["created_at"], self._ts(r, EPOCH - timedelta(days=r.randint(1, 900)))))
        for i, (name, definition) in enumerate(SEGMENTS, 1):
            sid = f"SEG{i:02d}"
            self.segments[sid] = {"segment_id": sid, "name": name, "definition": definition,
                                  "size_estimate": r.randint(500, 40000), "record_updated_at": self._ts(r)}
            self._touch("app_rider_segments", sid, self.segments[sid])
        for _ in range(40):
            self._new_campaign(r, EPOCH - timedelta(days=r.randint(0, 500)))
        for year in (2024, 2025):
            for month in range(1, 13 if year == 2024 else 12):  # Dec 2025 posts on 2026-01-03
                posted = date(year + (month == 12), month % 12 + 1, 3)
                self._post_ledger(r, year, month, self._ts(r, posted, lo=9, hi=18))

    # ------------------------------------------------------------------ trips (real TLC + synthetic people)
    def _trips(self, tlc_rows: list[dict]) -> None:
        r = rng("trips", self.day)
        shift = self.day - tlc_date_for(self.day)
        drivers = self._active(self.drivers, "driver_status")
        riders = self._active(self.riders, "account_status")
        stamp = f"{self.day:%Y%m%d}"
        survey_no = 0
        rows = sorted(tlc_rows, key=lambda t: (t["pickup_datetime"], t["tlc_sample_key"]))
        for i, t in enumerate(rows, 1):
            trip_id = f"TRP{stamp}{i:05d}"
            pickup = datetime.fromisoformat(t["pickup_datetime"]) + shift
            dropoff = datetime.fromisoformat(t["dropoff_datetime"]) + shift
            booked = t["payment_type"] == "1" and r.random() < APP_BOOKED_SHARE
            rider_id = r.choice(riders) if booked else None
            self._touch("app_trips", trip_id, {
                "trip_id": trip_id, "driver_id": r.choice(drivers), "rider_id": rider_id,
                "pickup_datetime": pickup.isoformat(sep=" "), "dropoff_datetime": dropoff.isoformat(sep=" "),
                "passenger_count": t["passenger_count"], "trip_distance": t["trip_distance"],
                "rate_code": t["rate_code"], "payment_type": t["payment_type"],
                "fare_amount": t["fare_amount"], "extra": t["extra"], "mta_tax": t["mta_tax"],
                "tip_amount": t["tip_amount"], "tolls_amount": t["tolls_amount"],
                "improvement_surcharge": t["imp_surcharge"], "airport_fee": t["airport_fee"],
                "total_amount": t["total_amount"], "pickup_location_id": t["pickup_location_id"],
                "dropoff_location_id": t["dropoff_location_id"], "tlc_source_key": t["tlc_sample_key"],
            })
            if rider_id and r.random() < SURVEY_SHARE:
                submitted = dropoff + timedelta(minutes=r.randint(2, 90))
                if submitted.date() != self.day:
                    continue
                survey_no += 1
                self._survey(r, f"SRV{stamp}{survey_no:04d}", trip_id, rider_id, submitted)

    def _survey(self, r, sid: str, trip_id: str, rider_id: str, submitted: datetime) -> None:
        rating = r.choices([1, 2, 3, 4, 5], weights=[4, 4, 10, 30, 52])[0]
        comment = r.choice(SURVEY_COMMENTS) or None
        if self._plant(r, "survey_orphan_trip"):
            trip_id = f"TRP{self.day:%Y%m%d}{r.randint(90000, 99999)}"
            self._log_defect("app_trip_surveys", sid, "trip_id", "survey_orphan_trip")
        if self._plant(r, "survey_rating_out_of_range"):
            rating = r.choice([0, 6, 9, -1])
            self._log_defect("app_trip_surveys", sid, "rating", "survey_rating_out_of_range")
        if self._plant(r, "survey_comment_contains_pii"):
            name = fakes.person(r)[0].lower()
            comment = f"Left my bag in the cab, call me at {fakes.phone(r)} or {name}@example.com"
            self._log_defect("app_trip_surveys", sid, "comment", "survey_comment_contains_pii")
        self._touch("app_trip_surveys", sid, {
            "survey_id": sid, "trip_id": trip_id, "rider_id": rider_id, "rating": rating,
            "comment": comment, "submitted_at": submitted.isoformat(sep=" ")})
