"""Access check: prove that BigQuery really enforces the access policy for the role accounts.

    uv run ect-access-check            # run both checks and load the results into raw.iam_role_access_tests
    uv run ect-access-check --dry-run  # list what would be tested, touch nothing

Unlike the rest of `raw`, these results are observed, not generated. For each role service account
(dbt/seeds/governance/role_service_accounts.csv) and each dataset, two checks are recorded:

  * config      (control design): is the account on the dataset's permission list?
  * enforcement (operating effectiveness): acting as the account, does a dry-run query of a probe
                table succeed or get refused? Dry runs read no data and cost nothing.

The pipeline acts as each role account through the Service Account Token Creator permission granted
on that account only. Whether a result is right or wrong is decided in dbt, against the access policy.
This script never fails the run: problems are recorded as observed = "error".
"""
import argparse
import csv
import json
from datetime import datetime

from .config import ACCESS_POLICY_PATH, GCP_PROJECT, GENERATOR_VERSION, LOCATION, OUTPUT_DIR
from .registry import OBSERVED_TABLES
from .sim import NY

ROLE_ACCOUNTS_PATH = ACCESS_POLICY_PATH.parent / "role_service_accounts.csv"
TABLE = "iam_role_access_tests"
# What each enforcement test tries to query: what a user of that dataset actually needs
PROBES = {"raw": "raw.hris_employees", "staging": "staging.stg_hris_employees", "marts": "marts.dim_employees"}
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def role_accounts() -> list[dict]:
    with open(ROLE_ACCOUNTS_PATH, newline="") as f:
        return list(csv.DictReader(f))


def config_check(client, account: str, dataset: str) -> tuple[str, str]:
    try:
        entries = client.get_dataset(f"{GCP_PROJECT}.{dataset}").access_entries
    except Exception as e:  # noqa: BLE001 - record, never fail the run
        return "error", f"could not read permissions: {type(e).__name__}"
    if not entries:  # an empty list means we couldn't see it, not that nobody has access
        return "error", "permission list came back empty"
    roles = sorted({e.role for e in entries if (e.entity_id or "").lower() == account.lower()})
    return ("allow", f"listed as {', '.join(roles)}") if roles else ("deny", "not on the permission list")


def enforcement_check(bigquery, source_credentials, account: str, dataset: str) -> tuple[str, str]:
    from google.api_core import exceptions
    from google.auth import impersonated_credentials

    try:
        creds = impersonated_credentials.Credentials(
            source_credentials=source_credentials, target_principal=account, target_scopes=SCOPES, lifetime=300)
        client = bigquery.Client(project=GCP_PROJECT, location=LOCATION, credentials=creds)
        sql = f"SELECT 1 FROM `{GCP_PROJECT}.{PROBES[dataset]}` LIMIT 1"
        client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)).result()
        return "allow", "dry-run query accepted"
    except (exceptions.Forbidden, exceptions.NotFound) as e:
        # keep BigQuery's reason only, e.g. "Access Denied: Table ...: User does not have permission ..."
        reason = (e.errors[0].get("message") if e.errors else None) or str(e).split("\n")[0]
        return "deny", reason[:300]
    except Exception as e:  # noqa: BLE001
        return "error", f"{type(e).__name__}: {str(e)[:250]}"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    accounts = role_accounts()
    if args.dry_run:
        for a in accounts:
            for ds in PROBES:
                print(f"would test {a['service_account']} ({a['access_role']}) on {ds}: config + enforcement")
        return

    import google.auth
    from google.cloud import bigquery

    now = datetime.now(NY)
    source_credentials, _ = google.auth.default(scopes=SCOPES)
    client = bigquery.Client(project=GCP_PROJECT, location=LOCATION, credentials=source_credentials)
    rows = []
    for a in accounts:
        for ds in PROBES:
            for method, (observed, detail) in (
                    ("config", config_check(client, a["service_account"], ds)),
                    ("enforcement", enforcement_check(bigquery, source_credentials, a["service_account"], ds))):
                rows.append({"run_date": now.date().isoformat(), "tested_at": now.isoformat(),
                             "service_account": a["service_account"], "dataset": ds, "probe_table": PROBES[ds],
                             "method": method, "observed": observed, "detail": detail,
                             "_batch_date": now.date().isoformat(), "_generator_version": GENERATOR_VERSION})
                print(f"{a['service_account']:<55} {ds:<8} {method:<12} {observed}")

    try:
        _load(client, bigquery, rows, now.date())
    except Exception as e:  # noqa: BLE001
        print(f"Could not load results: {type(e).__name__}: {e}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "access_check.json").write_text(json.dumps(rows, indent=2) + "\n")


def _load(client, bigquery, rows, day):
    from google.api_core.exceptions import NotFound

    spec = OBSERVED_TABLES[TABLE]
    schema = [bigquery.SchemaField(n, t) for n, t in spec["columns"]]
    table_id = f"{GCP_PROJECT}.raw.{TABLE}"
    try:
        client.get_table(table_id)
    except NotFound:
        t = bigquery.Table(table_id, schema=schema)
        t.description, t.labels = spec["description"], spec["labels"]
        t.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="_batch_date")
        client.create_table(t)
        print(f"created table {table_id}")
    config = bigquery.LoadJobConfig(schema=schema, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                                    labels={"component": "ect-access-check"})
    job = client.load_table_from_json(rows, f"{table_id}${day:%Y%m%d}", job_config=config)
    job.result()
    print(f"loaded {job.output_rows} rows -> {table_id} (partition {day})")


if __name__ == "__main__":
    main()
