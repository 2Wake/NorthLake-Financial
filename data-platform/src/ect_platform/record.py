"""Write a run record: a short Markdown file kept in the repo as evidence of each daily run.

    uv run ect-record

Reads output/last_run.json (from ect-daily) and dbt/target/run_results.json (from dbt build),
and writes run-records/<run date>.md: days loaded, row counts, and every test result.
Contains counts and test names only, never data values.
"""
import json
from datetime import datetime

from .config import OUTPUT_DIR, ROOT
from .sim import NY

RECORDS_DIR = ROOT / "run-records"


def main(argv=None):
    run_path = OUTPUT_DIR / "last_run.json"
    run = (json.loads(run_path.read_text()) if run_path.exists()
           else {"last_loaded_before": "unknown (generate/load step failed)", "days": []})
    results_path = ROOT / "dbt" / "target" / "run_results.json"
    results = json.loads(results_path.read_text())["results"] if results_path.exists() else []

    now = datetime.now(NY)
    lines = [f"# Run record — {now:%Y-%m-%d}", "",
             f"- Run at: {now:%Y-%m-%d %H:%M %Z}",
             f"- Last day loaded before this run: {run['last_loaded_before']}",
             f"- Days loaded this run: {len(run['days'])}", ""]
    if run["days"]:
        lines += ["## Rows loaded into `raw`", "", "| Day | Table | Rows |", "|---|---|---|"]
        for day in run["days"]:
            for table, rows in day["rows"].items():
                lines.append(f"| {day['batch_date']} | `{table}` | {rows:,} |")
        lines.append("")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines += ["## dbt build", "",
              ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "dbt did not run", ""]
    flagged = [r for r in results if r["status"] in ("warn", "fail", "error")]
    if flagged:
        lines += ["| Check | Status | Failing records |", "|---|---|---|"]
        for r in sorted(flagged, key=lambda r: r["unique_id"]):
            name = r["unique_id"].split(".")[2]
            lines.append(f"| `{name}` | {r['status']} | {r.get('failures') if r.get('failures') is not None else '—'} |")
        lines.append("")

    RECORDS_DIR.mkdir(exist_ok=True)
    path = RECORDS_DIR / f"{now:%Y-%m-%d}.md"
    path.write_text("\n".join(lines))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
