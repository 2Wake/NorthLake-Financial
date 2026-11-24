"""The raw tables: schema, description and labels (per the Labeling Standard).

Column descriptions are intentionally not filled in yet. They are a separate backlog
item (descriptions with deliberate, tracked gaps).
"""

# Domain register: owner and steward role slugs (labeling-standard.md)
DOMAINS = {
    "rider": ("vp-rider-experience", "rider-data-steward"),
    "driver": ("vp-driver-operations", "driver-data-steward"),
    "trips": ("vp-operations", "ops-data-steward"),
    "finance": ("cfo", "finance-data-steward"),
    "people": ("vp-people", "hr-data-steward"),
    "marketing": ("vp-marketing", "marketing-data-steward"),
    "governance": ("data-governance-manager", "data-governance-manager"),
    "reference": ("data-governance-manager", "ops-data-steward"),
}

META_COLUMNS = [("_batch_date", "DATE"), ("_generator_version", "STRING")]


def _labels(domain, classification, source_system, *, pii, pci=False, retention, origin="synthetic"):
    owner, steward = DOMAINS[domain]
    return {
        "domain": domain, "layer": "raw", "data_owner": owner, "data_steward": steward,
        "classification": classification, "source_system": source_system, "data_origin": origin,
        "contains_pii": str(pii).lower(), "pci_scope": str(pci).lower(), "retention": retention,
    }


TABLES = {
    "hris_employees": {
        "description": "HR system extract: one row per employee each time the record is created or changed. "
                       "Drivers are employees too (department Driver Operations).",
        "labels": _labels("people", "secret", "hris", pii=True, retention="7y"),
        "columns": [
            ("employee_id", "STRING"), ("first_name", "STRING"), ("last_name", "STRING"),
            ("email", "STRING"), ("ssn", "STRING"), ("department", "STRING"), ("title", "STRING"),
            ("pay_type", "STRING"), ("salary", "INT64"), ("performance_rating", "STRING"),
            ("hired_at", "DATE"), ("employment_status", "STRING"), ("terminated_at", "DATE"),
            ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "fleet_drivers": {
        "description": "Fleet system extract: one row per driver each time the record is created or changed.",
        "labels": _labels("driver", "secret", "fleet", pii=True, retention="7y"),
        "columns": [
            ("driver_id", "STRING"), ("employee_id", "STRING"), ("first_name", "STRING"),
            ("last_name", "STRING"), ("tlc_license", "STRING"), ("ssn", "STRING"), ("phone", "STRING"),
            ("home_address", "STRING"), ("payout_bank_account", "STRING"),
            ("background_check_status", "STRING"), ("driver_status", "STRING"), ("hired_at", "DATE"),
            ("status_changed_at", "TIMESTAMP"), ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "app_riders": {
        "description": "Rider app extract: one row per rider account each time it is created or changed.",
        "labels": _labels("rider", "confidential", "app", pii=True, retention="3y"),
        "columns": [
            ("rider_id", "STRING"), ("first_name", "STRING"), ("last_name", "STRING"), ("email", "STRING"),
            ("phone", "STRING"), ("home_address", "STRING"), ("created_at", "TIMESTAMP"),
            ("account_status", "STRING"), ("closed_at", "TIMESTAMP"), ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "payments_rider_cards": {
        "description": "Payments system extract: rider payment cards, one row each time a card is added or changed.",
        "labels": _labels("finance", "secret", "payments", pii=True, pci=True, retention="3y"),
        "columns": [
            ("card_id", "STRING"), ("rider_id", "STRING"), ("card_number", "STRING"),
            ("card_expiry", "STRING"), ("cardholder_name", "STRING"), ("card_status", "STRING"),
            ("added_at", "TIMESTAMP"), ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "app_trips": {
        "description": "Dispatch extract: completed trips. Trip details are real NYC TLC 2022 yellow-taxi trips "
                       "shifted to the simulated date; driver and rider assignments are synthetic.",
        "labels": _labels("trips", "confidential", "app", pii=True, retention="7y"),
        "columns": [
            ("trip_id", "STRING"), ("driver_id", "STRING"), ("rider_id", "STRING"),
            ("pickup_datetime", "DATETIME"), ("dropoff_datetime", "DATETIME"), ("passenger_count", "INT64"),
            ("trip_distance", "NUMERIC"), ("rate_code", "STRING"), ("payment_type", "STRING"),
            ("fare_amount", "NUMERIC"), ("extra", "NUMERIC"), ("mta_tax", "NUMERIC"),
            ("tip_amount", "NUMERIC"), ("tolls_amount", "NUMERIC"), ("improvement_surcharge", "NUMERIC"),
            ("airport_fee", "NUMERIC"), ("total_amount", "NUMERIC"), ("pickup_location_id", "STRING"),
            ("dropoff_location_id", "STRING"), ("tlc_source_key", "STRING"),
        ],
    },
    "app_trip_surveys": {
        "description": "Rider app extract: post-trip surveys with a 1–5 rating and a free-text comment.",
        "labels": _labels("rider", "confidential", "app", pii=True, retention="3y"),
        "columns": [
            ("survey_id", "STRING"), ("trip_id", "STRING"), ("rider_id", "STRING"), ("rating", "INT64"),
            ("comment", "STRING"), ("submitted_at", "DATETIME"),
        ],
    },
    "payments_financial_ledger": {
        "description": "General ledger postings, one row per account per month, posted on the 3rd of the following month.",
        "labels": _labels("finance", "sensitive", "payments", pii=False, retention="7y"),
        "columns": [
            ("entry_id", "STRING"), ("period", "STRING"), ("account", "STRING"), ("amount", "NUMERIC"),
            ("currency", "STRING"), ("recorded_at", "TIMESTAMP"),
        ],
    },
    "app_marketing_campaigns": {
        "description": "Marketing campaigns, one row each time a campaign is created or changed.",
        "labels": _labels("marketing", "sensitive", "app", pii=False, retention="3y"),
        "columns": [
            ("campaign_id", "STRING"), ("name", "STRING"), ("channel", "STRING"), ("start_date", "DATE"),
            ("end_date", "DATE"), ("budget", "INT64"), ("target_segment_id", "STRING"),
            ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "app_rider_segments": {
        "description": "Rider marketing segments; size estimates refresh on the 1st of each month.",
        "labels": _labels("marketing", "internal", "app", pii=False, retention="3y"),
        "columns": [
            ("segment_id", "STRING"), ("name", "STRING"), ("definition", "STRING"),
            ("size_estimate", "INT64"), ("record_updated_at", "TIMESTAMP"),
        ],
    },
    "gov_planted_defects": {
        "description": "ANSWER KEY. Every data-quality defect the generator planted on purpose. Used to score "
                       "how many planted defects the data-quality checks catch; checks must not read it.",
        "labels": _labels("governance", "internal", "governance", pii=False, retention="indefinite"),
        "columns": [
            ("defect_id", "STRING"), ("table_name", "STRING"), ("record_id", "STRING"),
            ("column_name", "STRING"), ("defect_code", "STRING"),
        ],
    },
}


def columns(table: str) -> list[tuple[str, str]]:
    return TABLES[table]["columns"] + META_COLUMNS
