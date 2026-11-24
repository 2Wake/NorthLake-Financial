"""Load generated batches into BigQuery `raw`.

    uv run ect-load --date 2026-11-23
    uv run ect-load --start 2026-01-01 --end 2026-11-23
    uv run ect-load --date 2026-11-23 --dry-run     # show what would happen, change nothing

Each raw table is partitioned by `_batch_date`. A day's batch is written into that day's
partition only (replacing that partition if it was loaded before), so:
  * history accumulates day by day and is never overwritten (append-only by day), and
  * re-running a day is safe: it can't create duplicates.
Tables are created on first load with their schema, description and labels.
Load jobs are free in BigQuery; they don't count against the query quota.
"""
import argparse
import json
from datetime import date, timedelta

from .config import GCP_PROJECT, LOCATION, OUTPUT_DIR, RAW_DATASET
from .registry import TABLES, columns


def _ensure_table(client, bigquery, table: str):
    from google.api_core.exceptions import NotFound

    table_id = f"{GCP_PROJECT}.{RAW_DATASET}.{table}"
    try:
        return client.get_table(table_id)
    except NotFound:
        spec = TABLES[table]
        t = bigquery.Table(table_id, schema=[bigquery.SchemaField(n, ty) for n, ty in columns(table)])
        t.description = spec["description"]
        t.labels = spec["labels"]
        t.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY,
                                                        field="_batch_date")
        print(f"  created table {table_id}")
        return client.create_table(t)


def load_day(client, bigquery, day: date, dry_run: bool) -> None:
    folder = OUTPUT_DIR / day.isoformat()
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No batch for {day}. Run: uv run ect-generate --date {day}")
    manifest = json.loads(manifest_path.read_text())
    for table, info in manifest["tables"].items():
        target = f"{GCP_PROJECT}.{RAW_DATASET}.{table}${day:%Y%m%d}"
        if dry_run:
            print(f"  [dry run] would load {info['rows']:>6} rows -> {target}")
            continue
        _ensure_table(client, bigquery, table)
        config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema=[bigquery.SchemaField(n, ty) for n, ty in columns(table)],
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # this day's partition only
            labels={"component": "ect-loader"},
        )
        with open(folder / f"{table}.jsonl", "rb") as f:
            job = client.load_table_from_file(f, target, job_config=config)
        job.result()
        print(f"  loaded {job.output_rows:>6} rows -> {target}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", type=date.fromisoformat)
    p.add_argument("--start", type=date.fromisoformat)
    p.add_argument("--end", type=date.fromisoformat)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    if args.start and args.end:
        days = [args.start + timedelta(days=i) for i in range((args.end - args.start).days + 1)]
    elif args.date:
        days = [args.date]
    else:
        p.error("give --date, or --start and --end")

    client = bigquery = None
    if not args.dry_run:
        from google.cloud import bigquery
        client = bigquery.Client(project=GCP_PROJECT, location=LOCATION)
    for day in days:
        print(f"{day}:")
        load_day(client, bigquery, day, args.dry_run)


if __name__ == "__main__":
    main()
