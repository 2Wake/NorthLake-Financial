"""Guarantees the platform depends on. Run: uv run pytest"""
import random
import re
from datetime import date, timedelta

from ect_platform import fakes
from ect_platform.config import EPOCH, TLC_CYCLE_START, TLC_LAST_DAY, tlc_date_for
from ect_platform.generate import generate
from ect_platform.registry import TABLES, columns
from ect_platform.sim import Simulation


def _fake_tlc_rows(day, n=200):
    r = random.Random(day.toordinal())
    rows = []
    for i in range(n):
        pickup = f"{day} {r.randint(0, 22):02d}:{r.randint(0, 59):02d}:00"
        rows.append({
            "tlc_sample_key": str(i), "vendor_id": "1", "pickup_datetime": pickup,
            "dropoff_datetime": pickup[:-5] + "59:59", "passenger_count": "1", "trip_distance": "2.1",
            "rate_code": "1", "payment_type": r.choice(["1", "1", "2"]), "fare_amount": "12.5", "extra": "0.5",
            "mta_tax": "0.5", "tip_amount": "2", "tolls_amount": "0", "imp_surcharge": "0.3",
            "airport_fee": None, "total_amount": "15.8", "pickup_location_id": "161", "dropoff_location_id": "237",
        })
    return rows


def _run(days, with_trips=False):
    sim, out, day = Simulation(), {}, EPOCH
    while day <= max(days):
        rows = _fake_tlc_rows(tlc_date_for(day)) if with_trips and day in days else None
        out[day] = sim.step(day, emit=day in days, tlc_rows=rows)
        day += timedelta(days=1)
    return {d: out[d] for d in days}


def test_same_date_same_data_regardless_of_what_else_is_generated():
    target = date(2026, 6, 15)
    alone = _run([target], with_trips=True)[target]
    with_others = _run([date(2026, 2, 1), target, date(2026, 7, 1)], with_trips=True)[target]
    assert alone == with_others


def test_written_files_are_byte_identical(tmp_path):
    a = generate([date(2026, 3, 1)], with_trips=False, out_dir=tmp_path / "a")
    b = generate([date(2026, 3, 1)], with_trips=False, out_dir=tmp_path / "b")
    assert a == b  # manifests include SHA-256 of every file


def test_tlc_mapping_keeps_weekday_and_stays_in_available_data():
    for offset in range(0, 800):
        day = EPOCH + timedelta(days=offset)
        src = tlc_date_for(day)
        assert src.weekday() == day.weekday()
        assert TLC_CYCLE_START <= src <= TLC_LAST_DAY


def test_ids_are_prefixed():
    batch = _run([date(2026, 5, 5)], with_trips=True)[date(2026, 5, 5)]
    patterns = {"app_trips": ("trip_id", r"TRP\d{13}"), "fleet_drivers": ("driver_id", r"DRV\d{5}"),
                "hris_employees": ("employee_id", r"EMP\d{5}"), "app_riders": ("rider_id", r"RDR\d{6}")}
    for table, (col, pattern) in patterns.items():
        for row in batch.get(table, []):
            assert re.fullmatch(pattern, row[col]), (table, row[col])


def test_trips_use_only_active_drivers():
    sim, day = Simulation(), EPOCH
    target = date(2026, 4, 10)
    while day < target:
        sim.step(day)
        day += timedelta(days=1)
    batch = sim.step(target, emit=True, tlc_rows=_fake_tlc_rows(tlc_date_for(target)))
    for trip in batch["app_trips"]:
        assert sim.drivers[trip["driver_id"]]["driver_status"] == "active"


def test_every_batch_column_is_in_the_schema():
    batch = _run([EPOCH], with_trips=True)[EPOCH]
    for table, rows in batch.items():
        names = {c for c, _ in columns(table)}
        for row in rows:
            assert set(row) <= names, (table, set(row) - names)


def test_every_table_has_required_labels():
    required = {"domain", "layer", "data_owner", "data_steward", "classification", "source_system", "data_origin"}
    for table, spec in TABLES.items():
        assert required <= set(spec["labels"]), table


def test_card_numbers_pass_luhn():
    r = random.Random(1)
    for _ in range(100):
        digits = [int(c) for c in fakes.card_number(r).replace(" ", "")]
        total = sum(d if i % 2 == 0 else (d * 2 - 9 if d * 2 > 9 else d * 2)
                    for i, d in enumerate(reversed(digits)))
        assert total % 10 == 0


def test_answer_key_never_stores_values():
    batch = _run([EPOCH])[EPOCH]
    for row in batch["gov_planted_defects"]:
        assert set(row) == {"defect_id", "table_name", "record_id", "column_name", "defect_code"}


def _simulate_through(target):
    sim, day, planted = Simulation(), EPOCH, set()
    while day <= target:
        batch = sim.step(day, emit=True)
        planted |= {(d["record_id"], d["defect_code"]) for d in batch["gov_planted_defects"]}
        day += timedelta(days=1)
    return sim, planted


def test_named_roster_has_stable_ids_and_managers():
    sim, _ = _simulate_through(EPOCH)
    assert sim.roster["marcus.delgado"] == "EMP10001"
    assert sim.employees[sim.roster["jordan.ellis"]]["manager_id"] == sim.roster["renee.okonkwo"]
    assert sim.role_holders["ciso"] == sim.roster["victor.hale"]


def test_unplanted_grants_follow_the_access_policy():
    from ect_platform.sim import POLICY
    sim, planted = _simulate_through(date(2026, 6, 30))
    flagged = {gid for gid, _ in planted}
    for gid, g in sim.grants.items():
        if gid in flagged:
            continue
        assert (g["access_role"], g["dataset"]) in POLICY, g
        assert g["approved_by"] and g["approved_by"] != g["employee_id"], g


def test_business_users_and_drivers_have_no_warehouse_access():
    sim, _ = _simulate_through(EPOCH)
    support = sim.roster["monique.harris"]
    with_access = {g["employee_id"] for g in sim.grants.values()}
    assert support not in with_access
    assert not any(sim.employees[e]["title"] == "Driver" for e in with_access)


def test_roster_correction_arrives_on_its_day_and_leaves_history_unchanged():
    fix_day = date(2026, 11, 24)
    out = _run([EPOCH, fix_day - timedelta(days=1), fix_day])
    arjun = lambda batch: [e for e in batch.get("hris_employees", []) if e["last_name"] == "Mehta"]
    assert arjun(out[EPOCH])[0]["role_code"] is None                 # as originally loaded
    assert arjun(out[fix_day - timedelta(days=1)]) == []              # no change emitted before the fix
    assert arjun(out[fix_day])[0]["role_code"] == "vp-engineering"   # HR correction on fix_day
