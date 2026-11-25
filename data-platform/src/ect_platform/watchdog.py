"""Watchdog: alert if the daily run hasn't completed by 12:00 New York time (POL-09 statement 18).

    python3 data-platform/src/ect_platform/watchdog.py   # as the watchdog workflow runs it (no install needed)
    uv run ect-watchdog                                    # the same, from data-platform/

Looks for today's run record (New York date) in data-platform/run-records/. If it's missing, exits 1,
so the workflow fails and GitHub emails the maintainer. Severity follows POL-09 Appendix A: SEV4,
or SEV3 if yesterday's record is missing too. Standard library only: it must still work when
installing the project is what broke.

GitHub's schedule uses UTC, so the workflow fires at 16:05 and 17:05 UTC. SCHEDULE (the cron that
fired) decides which one counts: 16:05 in summer (EDT), 17:05 in winter (EST); the other exits quietly.
A manual run (no SCHEDULE) always checks.
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
RECORDS_DIR = Path(__file__).resolve().parents[2] / "run-records"
CRON_BY_UTC_OFFSET = {-4: "5 16 * * *", -5: "5 17 * * *"}  # EDT, EST


def has_record(day, records_dir=RECORDS_DIR) -> bool:
    return any(records_dir.glob(f"{day.isoformat()}*.md"))


def evaluate(now: datetime, schedule: str | None, records_dir=RECORDS_DIR) -> tuple[int, str]:
    """Return (exit code, message) for a watchdog run at `now` (New York time)."""
    if schedule:
        offset = int(now.utcoffset().total_seconds() // 3600)
        if CRON_BY_UTC_OFFSET.get(offset) != schedule.strip():
            return 0, f"Skipped: the {schedule!r} schedule isn't the 12:05 New York one at this time of year."
    if now.hour < 12:
        return 0, f"Skipped: it's {now:%H:%M} in New York, before the 12:00 deadline."
    today, yesterday = now.date(), now.date() - timedelta(days=1)
    if has_record(today, records_dir):
        return 0, f"OK: the daily run for {today} has a run record."
    severity = "SEV3" if not has_record(yesterday, records_dir) else "SEV4"
    return 1, (f"ALERT {severity}: no run record for {today} by 12:00 New York"
               f"{' (and none for ' + yesterday.isoformat() + ' either)' if severity == 'SEV3' else ''}. "
               "The daily run didn't start or didn't finish. Respond within 1 business day (POL-09 statement 18): "
               "check the Actions tab, run the daily refresh by hand, and record the cause, the gap and the fix in Jira.")


def main() -> int:
    code, message = evaluate(datetime.now(NY), os.environ.get("SCHEDULE") or None)
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
