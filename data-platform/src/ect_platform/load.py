"""Load generated batches into BigQuery `raw`.

    uv run ect-load --date 2026-11-23
    uv run ect-load --start 2026-01-01 --end 2026-11-23
    uv run ect-load --date 2026-11-23 --dry-run     # show what would happen, change nothing
    uv run ect-load --start 2026-01-01 --end 2026-11-23 --bulk   # first-time backfill, one job per table

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
        # WRITE_TRUNCATE on a partition target replaces this day's partition only
        config = _load_config(bigquery, table, bigquery.WriteDisposition.WRITE_TRUNCATE)
        with open(folder / f"{table}.jsonl", "rb") as f:
            job = client.load_table_from_file(f, target, job_config=config)
        job.result()
        print(f"  loaded {job.output_rows:>6} rows -> {target}")


def _load_config(bigquery, table: str, disposition):
    return bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=[bigquery.SchemaField(n, ty) for n, ty in columns(table)],
        write_disposition=disposition, labels={"component": "ect-loader"})


def load_range_bulk(client, bigquery, days: list[date], dry_run: bool) -> list[date]:
    """Backfill: one load job per table for the whole range instead of one per day.

    Only used for tables where none of the range's days are loaded yet, so appending can't
    duplicate anything. Stops with an error if a batch is missing, a day is already loaded, or row counts differ.
    """
    import tempfile

    manifests = {}
    for day in days:
        path = OUTPUT_DIR / day.isoformat() / "manifest.json"
        if not path.exists():
            raise SystemExit(f"No batch for {day}. Run: uv run ect-generate --start {days[0]} --end {days[-1]}")
        manifests[day] = json.loads(path.read_text())
    wanted = {f"{d:%Y%m%d}" for d in days}
    for table in TABLES:
        files = [OUTPUT_DIR / d.isoformat() / f"{table}.jsonl" for d in days if table in manifests[d]["tables"]]
        rows = sum(manifests[d]["tables"][table]["rows"] for d in days if table in manifests[d]["tables"])
        if not files:
            continue
        target = f"{GCP_PROJECT}.{RAW_DATASET}.{table}"
        if dry_run:
            print(f"  [dry run] would bulk-load {rows:>7} rows from {len(files)} day(s) -> {target}")
            continue
        _ensure_table(client, bigquery, table)
        overlap = wanted & set(client.list_partitions(target))
        if overlap:
            raise SystemExit(f"{target} already has {len(overlap)} of these days; "
                             f"re-run without --bulk to replace them day by day.")
        with tempfile.TemporaryFile() as tmp:
            for path in files:
                tmp.write(path.read_bytes())
            tmp.seek(0)
            job = client.load_table_from_file(
                tmp, target, job_config=_load_config(bigquery, table, bigquery.WriteDisposition.WRITE_APPEND))
            job.result()
        print(f"  loaded {job.output_rows:>7} rows from {len(files)} day(s) -> {target}")
        if job.output_rows != rows:
            raise SystemExit(f"Row count mismatch for {table}: expected {rows}, loaded {job.output_rows}")
    return days


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", type=date.fromisoformat)
    p.add_argument("--start", type=date.fromisoformat)
    p.add_argument("--end", type=date.fromisoformat)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--bulk", action="store_true",
                   help="backfill a range with one job per table (only into days not yet loaded)")
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
    if args.bulk:
        print(f"{days[0]} .. {days[-1]} (bulk):")
        load_range_bulk(client, bigquery, days, args.dry_run)
        return
    for day in days:
        print(f"{day}:")
        load_day(client, bigquery, day, args.dry_run)


if __name__ == "__main__":
    main()
