"""Daily run: generate and load every day not yet in BigQuery, through yesterday.

    uv run ect-daily              # catch up through yesterday (New York time)
    uv run ect-daily --dry-run    # show which days would be generated and loaded

Finds the newest day already loaded (latest _batch_date in raw.app_trips), then generates
and loads each missing day in order. If a run fails or is skipped, the next run catches up.
Re-running is safe: each day replaces only its own partition.

Writes output/last_run.json (days loaded and row counts) for the run record.
"""
import argparse
import json
from datetime import timedelta

from .config import EPOCH, GCP_PROJECT, LOCATION, MAX_BYTES_BILLED, OUTPUT_DIR, RAW_DATASET
from .generate import generate, yesterday
from .load import load_day


def last_loaded_day(client, bigquery):
    sql = f"SELECT MAX(_batch_date) AS d FROM `{GCP_PROJECT}.{RAW_DATASET}.app_trips`"
    config = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED,
                                     labels={"component": "ect-daily"})
    return next(iter(client.query(sql, job_config=config).result()))["d"]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    from google.cloud import bigquery
    client = bigquery.Client(project=GCP_PROJECT, location=LOCATION)
    last = last_loaded_day(client, bigquery)
    start = (last + timedelta(days=1)) if last else EPOCH
    end = yesterday()
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    print(f"Last loaded day: {last}. Days to run: {len(days)}"
          + (f" ({days[0]} .. {days[-1]})" if days else ""))

    summary = {"last_loaded_before": str(last), "days": [], "dry_run": args.dry_run}
    if days and not args.dry_run:
        manifests = generate(days)
        for day in days:
            print(f"{day}:")
            load_day(client, bigquery, day, dry_run=False)
            summary["days"].append({"batch_date": day.isoformat(),
                                    "rows": {t: m["rows"] for t, m in manifests[day]["tables"].items()}})
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "last_run.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
