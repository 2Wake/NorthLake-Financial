#!/usr/bin/env bash
# Load the Empire City Taxi synthetic estate CSVs into a BigQuery dataset.
# Prereqs: gcloud + bq CLI installed and authenticated (`gcloud auth login`),
# and a BigQuery sandbox project. Run generate_estate.py first.
#
# Usage:  ./load_to_bigquery.sh YOUR_PROJECT_ID [DATASET] [LOCATION]
set -euo pipefail

PROJECT="${1:?Usage: ./load_to_bigquery.sh PROJECT_ID [DATASET] [LOCATION]}"
DATASET="${2:-ect}"
LOCATION="${3:-US}"
DATA_DIR="$(cd "$(dirname "$0")/../data" && pwd)"

echo "Project=$PROJECT  Dataset=$DATASET  Location=$LOCATION"
echo "Creating dataset (ok if it already exists)…"
bq --location="$LOCATION" mk --dataset --description "Empire City Taxi synthetic estate (fictional)" \
   "${PROJECT}:${DATASET}" 2>/dev/null || true

for csv in "$DATA_DIR"/*.csv; do
  table="$(basename "$csv" .csv)"
  # skip the DQ output if present
  [ "$table" = "remediation_log" ] && continue
  echo "Loading ${table}…"
  bq --location="$LOCATION" load \
     --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
     "${PROJECT}:${DATASET}.${table}" "$csv"
done

echo "Done. Tables loaded into ${PROJECT}:${DATASET}."
echo "Note: BigQuery sandbox applies a 60-day expiration to tables — re-run to refresh."
