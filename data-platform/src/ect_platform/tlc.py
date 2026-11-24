"""Fetch and cache the real NYC TLC trips that get replayed on each simulated day.

Reads only from our own sample table (raw.tlc_yellow_trips_sample, partitioned by pickup
date), so each read touches only the days it needs. Results are cached as one CSV per
2022 date in .cache/tlc/, so a date is fetched at most once per machine.
"""
import csv
from datetime import date

from .config import GCP_PROJECT, LOCATION, MAX_BYTES_BILLED, TLC_CACHE_DIR, TLC_SAMPLE_TABLE

FIELDS = ["tlc_sample_key", "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
          "trip_distance", "rate_code", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount",
          "tolls_amount", "imp_surcharge", "airport_fee", "total_amount", "pickup_location_id",
          "dropoff_location_id"]


def _path(tlc_day: date):
    return TLC_CACHE_DIR / f"{tlc_day.isoformat()}.csv"


def ensure_cached(tlc_days: set[date]) -> None:
    missing = sorted(d for d in tlc_days if not _path(d).exists())
    if not missing:
        return
    from google.cloud import bigquery  # imported here so offline runs don't need credentials

    client = bigquery.Client(project=GCP_PROJECT, location=LOCATION)
    sql = f"""
        SELECT {", ".join(FIELDS)}
        FROM `{TLC_SAMPLE_TABLE}`
        WHERE DATE(pickup_datetime) IN UNNEST(@days)
    """
    config = bigquery.QueryJobConfig(
        maximum_bytes_billed=MAX_BYTES_BILLED,
        query_parameters=[bigquery.ArrayQueryParameter("days", "DATE", missing)],
        labels={"component": "ect-generator", "purpose": "tlc-fetch"},
    )
    by_day: dict[date, list] = {d: [] for d in missing}
    for row in client.query(sql, job_config=config).result():
        by_day[row["pickup_datetime"].date()].append(row)
    TLC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for day, rows in by_day.items():
        with open(_path(day), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
            for row in rows:
                writer.writerow([_fmt(row[k]) for k in FIELDS])
    print(f"  fetched TLC trips for {len(missing)} day(s) from {TLC_SAMPLE_TABLE}")


def _fmt(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def read_day(tlc_day: date) -> list[dict]:
    with open(_path(tlc_day), newline="") as f:
        return [{k: (v if v != "" else None) for k, v in row.items()} for row in csv.DictReader(f)]
