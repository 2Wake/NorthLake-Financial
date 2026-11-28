"""ECT Data & Governance Portal (GOV-179): assembly and page build, without BigQuery."""
from datetime import date, datetime, timezone
from urllib.parse import parse_qs, urlparse

from ect_platform import portal

TODAY = date(2026, 11, 28)
RUN = datetime(2026, 11, 28, 11, 43, tzinfo=timezone.utc)


def reg(table, col, tier, approved_on="2026-11-20", layer="staging"):
    return {"layer": layer, "table_name": table, "column_name": col, "classification": tier,
            "data_category": "x", "treatment": "inherited", "data_owner": "vp-hr", "data_steward": "hr-data-steward",
            "status": "approved", "approved_by": "vp-hr", "approved_on": approved_on, "rationale": "r"}


def fake_bq(findings=(), accuracy=(5, 5)):
    return {
        "columns": [{"layer": "staging", "table_name": "stg_emp", "column_name": c, "data_type": "STRING",
                     "ordinal_position": i} for i, c in enumerate(["employee_id", "ssn_last4", "notes"])],
        "labels": {"staging.stg_emp": portal.parse_labels(
            '[STRUCT("domain", "hr"), STRUCT("layer", "staging"), STRUCT("data_owner", "vp-hr"), '
            'STRUCT("data_steward", "hr-data-steward"), STRUCT("classification", "confidential")]')},
        "tables": [{"layer": "staging", "table_name": "stg_emp", "row_count": 10, "size_bytes": 100,
                    "last_modified": RUN, "kind": "view"}],
        "findings": list(findings),
        "accuracy": {"correct": accuracy[0], "total": accuracy[1]},
    }


def finding(rule, col="notes"):
    return {"rule_id": rule, "layer": "staging", "table_name": "stg_emp", "column_name": col, "detail": "d",
            "evaluated_at": RUN}


REGISTER = [reg("stg_emp", "employee_id", "Internal"), reg("stg_emp", "ssn_last4", "Confidential")]
MANIFEST = {"generated_at": None, "docs": {"staging.stg_emp": {"table": "Employees", "columns": {"notes": "Free text"}}}}


def statement(snap, n):
    return next(s for s in snap["statements"] if s["number"] == n)


def test_parse_labels():
    assert portal.parse_labels('[STRUCT("domain", "trips"), STRUCT("pci_scope", "false")]') == {
        "domain": "trips", "pci_scope": "false"}
    assert portal.parse_labels(None) == {}


def test_assemble_joins_register_labels_and_findings():
    snap = portal.assemble(fake_bq([finding("CLS-01")]), REGISTER, MANIFEST, TODAY)
    t = snap["tables"][0]
    assert t["description"] == "Employees"
    assert t["missing_labels"] == ["source_system", "data_origin"]
    notes = next(c for c in t["columns"] if c["name"] == "notes")
    assert notes["classification"] == "" and notes["findings"] == ["CLS-01"]
    assert notes["steward"] == "hr-data-steward"  # falls back to the table label
    assert snap["rule_counts"]["CLS-01"] == 1


def test_statements_follow_their_checks():
    snap = portal.assemble(fake_bq([finding("CLS-01"), finding("CLS-06")]), REGISTER, MANIFEST, TODAY)
    assert statement(snap, 1)["status"] == "findings"
    assert statement(snap, 2)["status"] == "pass"
    assert statement(snap, 11)["status"] == "findings"
    assert statement(snap, 10)["status"] == "manual"
    assert statement(snap, 15)["status"] == "pass"   # checks ran today
    assert statement(snap, 16)["status"] == "pass"   # 5 of 5


def test_review_age_secret_and_accuracy():
    register = REGISTER + [reg("stg_cards", "card_number", "Secret", approved_on="2025-10-01")]
    snap = portal.assemble(fake_bq(accuracy=(4, 5)), register, MANIFEST, TODAY)
    assert statement(snap, 9)["status"] == "findings"
    assert statement(snap, 14)["status"] == "attention"
    assert "staging.stg_cards.card_number" in statement(snap, 14)["note"]
    assert statement(snap, 16)["status"] == "findings"
    assert statement(snap, 15)["status"] == "findings"  # no check results at all


def test_edit_link_is_a_prefilled_gov_task():
    q = parse_qs(urlparse(portal.edit_link("staging.stg_emp.notes classification", "not classified",
                                           "hr-data-steward", "vp-hr")).query)
    assert q["pid"] == ["10000"] and q["issuetype"] == ["10004"] and q["labels"] == ["catalog-edit-request"]
    for section in ("Description", "Why it matters", "Potential blockers", "Intended outcome"):
        assert f"h2. {section}" in q["description"][0]


def test_page_escapes_script_breakout():
    bq = fake_bq([dict(finding("CLS-08"), detail="</script><img src=x onerror=alert(1)>")])
    page = portal.build_html(portal.assemble(bq, REGISTER, MANIFEST, TODAY))
    assert "</script><img" not in page
    assert page.count("</script>") == 1
