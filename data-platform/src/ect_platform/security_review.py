"""Automated daily security review (POL-09 statement 15; alerts in POL-09 Appendix A).

    uv run ect-security-review                   # review every UTC day since the last review (normally yesterday)
    uv run ect-security-review --day 2026-11-24  # review one day (local testing)
    uv run ect-security-review --check           # exit 1 if the last review raised alerts or didn't run

Reads Google Cloud audit logs through the Cloud Logging API (no BigQuery queries, so no query cost)
and writes output/security_review.json. `ect-record` puts the result in the run record, which is the
review record (POL-09 statement 19). The workflow's last step runs `--check`, so the run fails, and
GitHub emails the maintainer, only after the run record has been committed.

Signs in as the log reader account (`ect-monitor`, Private Logs Viewer only), never as the pipeline
it watches. In GitHub Actions the workflow passes that account's credentials file; locally it uses
your own gcloud sign-in.

Privacy: the repository is public. Results show role names (`maintainer`, `ect-pipeline`, role
accounts) or `unknown-identity-<hash>`, never a person's email, and never IP addresses.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .config import ACCESS_POLICY_PATH, GCP_PROJECT, OUTPUT_DIR, ROOT

RESULT_PATH = OUTPUT_DIR / "security_review.json"
RECORDS_DIR = ROOT / "run-records"
RUN_RESULTS_PATH = ROOT / "dbt" / "target" / "run_results.json"
ROLE_ACCOUNTS_PATH = ACCESS_POLICY_PATH.parent / "role_service_accounts.csv"
LOGGING_URL = "https://logging.googleapis.com/v2/entries:list"
LOG = f"projects/{GCP_PROJECT}/logs/cloudaudit.googleapis.com%2F"
SA_DOMAIN = f"@{GCP_PROJECT}.iam.gserviceaccount.com"
MAX_CATCH_UP_DAYS = 7
NY = ZoneInfo("America/New_York")

# Our own service accounts and the access role each holds in the access matrix (POL-02 Appendix A).
# Role accounts come from role_service_accounts.csv. The maintainer's personal account is supplied at
# run time (ECT_MAINTAINER_PRINCIPAL: a GitHub secret), so it never appears in the repository.
FIXED_IDENTITIES = {
    f"ect-pipeline{SA_DOMAIN}": ("ect-pipeline", "platform_admin"),
    f"ect-monitor{SA_DOMAIN}": ("ect-monitor", "log_reader"),
    f"ect-watchdog{SA_DOMAIN}": ("ect-watchdog", "watchdog"),
    f"ect-catalog{SA_DOMAIN}": ("ect-catalog", "catalog"),
}
# Pipeline sign-ins are accepted only from a workflow of this repository running on main
# (the repository and owner IDs GitHub adds are optional in the pattern).
WORKFLOW_SUBJECT = re.compile(r"^repo:2Wake(@\d+)?/empire-city-taxi-grc(@\d+)?:ref:refs/heads/main$")
GUARDED_ACCOUNTS = {f"ect-pipeline{SA_DOMAIN}", f"ect-monitor{SA_DOMAIN}"}
LEGACY_METHOD = re.compile(r"^[a-z]+service\.[a-z]+$")  # BigQuery's older duplicate audit format

ALERTS = {
    "IAM_CHANGED": ("IAM policy changed on the project or a dataset", "SEV3 (SEV2 if it grants unapproved privileged access)"),
    "SA_KEY_CREATED": ("Service account key created (banned by POL-02 statement 14)", "SEV2"),
    "RAW_UNAPPROVED": ("`raw` read by an identity not approved for it (POL-02 Appendix A)", "SEV2"),
    "LOGGING_CHANGED": ("Logging changed: routing, exclusions, bucket retention or Data Access settings", "SEV2"),
    "ACCESS_DENIALS": ("5 or more access denials for one identity within 1 hour", "SEV3"),
    "PIPELINE_SIGNIN": ("Pipeline or log-reader identity signed in from anywhere but the repository's workflow", "SEV2"),
    "ACC_FINDING": ("Daily access check finding, new or increased (ACC-01 to ACC-10)", "As POL-02 sets"),
}


# ---------- identities ----------

def load_identities(maintainer: str | None = None) -> dict[str, tuple[str, str]]:
    """principal (lower case) -> (display name, access role)."""
    ids = dict(FIXED_IDENTITIES)
    with open(ROLE_ACCOUNTS_PATH, newline="") as f:
        for row in csv.DictReader(f):
            ids[row["service_account"].lower()] = (row["service_account"].split("@")[0], row["access_role"])
    if maintainer:
        ids[maintainer.strip().lower()] = ("maintainer", "platform_admin")
    return ids


def raw_roles() -> set[str]:
    """Access roles the access matrix allows to read `raw`."""
    with open(ACCESS_POLICY_PATH, newline="") as f:
        return {r["access_role"] for r in csv.DictReader(f) if r["dataset"] == "raw"}


def display(principal: str, ids: dict) -> str:
    """A name safe for a public run record: never a person's email."""
    p = (principal or "").lower()
    if not p:
        return "unknown-identity"
    if p in ids:
        return ids[p][0]
    if p.startswith("principal://") and "/subject/" in p:
        subject = principal.split("/subject/", 1)[1]
        return "github-workflow (main)" if WORKFLOW_SUBJECT.match(subject) else f"federated-{_hash(p)}"
    if p.endswith(SA_DOMAIN):
        return p.split("@")[0]
    if "@gcp-sa-" in p:  # Google service agents: service-<project number>@gcp-sa-<service>.iam...
        return f"google-service-agent ({p.split('@gcp-sa-')[1].split('.')[0]})"
    if p.endswith(".gserviceaccount.com"):
        return "google-system-account"
    return f"unknown-identity-{_hash(p)}"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def _principal(entry: dict) -> str:
    auth = entry.get("protoPayload", {}).get("authenticationInfo", {})
    return auth.get("principalEmail") or auth.get("principalSubject") or ""


def _ok(entry: dict) -> bool:
    return not entry.get("protoPayload", {}).get("status", {}).get("code")


def _member(member: str, ids: dict) -> str:
    """An IAM binding member (user:..., serviceAccount:..., group:...) as a public-safe name."""
    kind, _, who = member.partition(":")
    if not who:
        return member  # allUsers, allAuthenticatedUsers
    if kind == "serviceAccount" or kind == "user":
        return display(who, ids)
    return f"{kind}-{_hash(who.lower())}"


def _binding_changes(p: dict, ids: dict) -> str:
    """'added roles/x to a; removed roles/y from b' from the audit entry's policy delta."""
    deltas = (p.get("serviceData", {}).get("policyDelta", {}).get("bindingDeltas")
              or p.get("metadata", {}).get("datasetChange", {}).get("bindingDeltas") or [])
    grouped = defaultdict(list)
    for d in deltas:
        action = "added" if d.get("action") == "ADD" else "removed"
        grouped[(action, _member(d.get("member", ""), ids))].append(d.get("role", "").removeprefix("roles/"))
    return "; ".join(f"{a} {', '.join(sorted(roles))} {'to' if a == 'added' else 'from'} {m}"
                     for (a, m), roles in sorted(grouped.items()))


def _alert(kind: str, identity: str, count: int, detail: str, first: str) -> dict:
    title, severity = ALERTS[kind]
    return {"alert": kind, "title": title, "severity": severity, "identity": identity,
            "count": count, "detail": detail, "first_seen": first}


def _group(rows):
    """[(kind, identity, detail, timestamp)] -> alerts, one per (kind, identity, detail)."""
    groups = defaultdict(list)
    for kind, identity, detail, ts in rows:
        groups[(kind, identity, detail)].append(ts)
    return [_alert(k, i, len(ts), d, min(ts)) for (k, i, d), ts in sorted(groups.items())]


# ---------- checks (pure functions over log entries, so they can be tested) ----------

def check_admin(entries: list[dict], ids: dict) -> list[dict]:
    """Admin Activity: IAM changes, service account keys, logging changes."""
    rows = []
    for e in entries:
        p = e.get("protoPayload", {})
        method, service = p.get("methodName", ""), p.get("serviceName", "")
        m = method.lower()  # Google's casing varies by service: SetIamPolicy (most) vs SetIAMPolicy (IAM)
        if LEGACY_METHOD.match(method) or not _ok(e):
            continue
        who, ts = display(_principal(e), ids), e.get("timestamp", "")
        resource = p.get("resourceName", "")
        mask = p.get("request", {}).get("updateMask", "")
        if m.endswith("createserviceaccountkey"):
            rows.append(("SA_KEY_CREATED", who, resource.split("/serviceAccounts/")[-1].split("/")[0], ts))
        elif service == "logging.googleapis.com" and ("configservicev2" in m or m.endswith("deletelog")):
            rows.append(("LOGGING_CHANGED", who, method.split(".")[-1], ts))
        elif m.endswith("setiampolicy") and "auditConfigs" in mask:
            rows.append(("LOGGING_CHANGED", who, "Data Access audit log settings", ts))
        elif m.endswith("setiampolicy"):
            changes = _binding_changes(p, ids)
            rows.append(("IAM_CHANGED", who, f"{method.split('.')[-1]} on {_short(resource)}"
                         + (f": {changes}" if changes else ""), ts))
        elif m.endswith("datasetservice.updatedataset"):
            rows.append(("IAM_CHANGED", who, f"dataset settings or permissions updated on {_short(resource)}", ts))
    return _group(rows)


def check_raw_reads(entries: list[dict], ids: dict, allowed_roles: set[str]) -> list[dict]:
    """BigQuery Data Access: table reads in `raw` by identities the access matrix doesn't allow."""
    rows = []
    for e in entries:
        p = e.get("protoPayload", {})
        if "tableDataRead" not in p.get("metadata", {}) or "/datasets/raw/" not in p.get("resourceName", ""):
            continue
        principal = _principal(e).lower()
        role = ids.get(principal, (None, None))[1]
        if role not in allowed_roles:
            table = p["resourceName"].split("/tables/")[-1]
            rows.append(("RAW_UNAPPROVED", display(principal, ids), f"raw.{table}", e.get("timestamp", "")))
    return _group(rows)


def check_denials(entries: list[dict], ids: dict, threshold: int = 5) -> list[dict]:
    """5 or more PERMISSION_DENIED entries for one identity within any 60-minute window."""
    times = defaultdict(list)
    for e in entries:
        if e.get("protoPayload", {}).get("status", {}).get("code") == 7:
            times[display(_principal(e), ids)].append(_ts(e["timestamp"]))
    alerts = []
    for who, ts in sorted(times.items()):
        ts.sort()
        start, worst, worst_start = 0, 0, None
        for end in range(len(ts)):
            while ts[end] - ts[start] > timedelta(hours=1):
                start += 1
            if end - start + 1 > worst:
                worst, worst_start = end - start + 1, ts[start]
        if worst >= threshold:
            alerts.append(_alert("ACCESS_DENIALS", who, worst, f"{len(ts)} denials that day",
                                 worst_start.isoformat().replace("+00:00", "Z")))
    return alerts


def check_signins(entries: list[dict], ids: dict) -> list[dict]:
    """Token exchanges must come from the repository's workflow on main; ect-pipeline and ect-monitor
    may only be impersonated by that workflow (or refresh their own token)."""
    rows = []
    for e in entries:
        p = e.get("protoPayload", {})
        method, ts = p.get("methodName", ""), e.get("timestamp", "")
        if not _ok(e):
            continue
        if method.lower().endswith("exchangetoken"):
            subject = p.get("authenticationInfo", {}).get("principalSubject", "")
            if not WORKFLOW_SUBJECT.match(subject):
                rows.append(("PIPELINE_SIGNIN", f"federated-{_hash(subject.lower())}", "token exchange from an unexpected workflow or branch", ts))
        elif method.lower().endswith("generateaccesstoken"):
            target = p.get("request", {}).get("name", "").split("/")[-1].lower()
            if target not in GUARDED_ACCOUNTS:
                continue
            caller = _principal(e)
            from_workflow = "/subject/" in caller and WORKFLOW_SUBJECT.match(caller.split("/subject/", 1)[1])
            if not (from_workflow or caller.lower() == target):
                rows.append(("PIPELINE_SIGNIN", display(caller, ids), f"impersonated {target.split('@')[0]}", ts))
    return _group(rows)


def check_access_findings(current: dict[str, int], previous: dict[str, int]) -> tuple[list[dict], list[dict]]:
    """ACC tests from this run's dbt results, compared with the previous run record.
    Returns (alerts for new or increased findings, known findings unchanged or lower)."""
    alerts, known = [], []
    for test, count in sorted(current.items()):
        before = previous.get(test)
        if before is None or count > before:
            change = "new" if before is None else f"up from {before}"
            alerts.append(_alert("ACC_FINDING", "access check", count, f"`{test}` ({change})", ""))
        else:
            known.append({"test": test, "count": count, "previous": before})
    return alerts, known


# ---------- inputs ----------

def _ts(value: str) -> datetime:
    value = value.replace("Z", "+00:00")
    if "." in value:  # Cloud Logging gives nanoseconds; Python handles 6 digits
        head, tail = value.split(".", 1)
        frac, _, offset = tail.partition("+")
        value = f"{head}.{frac[:6]}+{offset}"
    return datetime.fromisoformat(value)


def _short(resource: str) -> str:
    return resource.replace(f"projects/{GCP_PROJECT}", "project").replace("/datasets/", ": dataset ")


def acc_counts_from_results(path=RUN_RESULTS_PATH) -> dict[str, int] | None:
    if not path.exists():
        return None
    out = {}
    for r in json.loads(path.read_text())["results"]:
        name = r["unique_id"].split(".")[2]
        if name.startswith("acc_") and r["status"] in ("warn", "fail", "error"):
            out[name] = int(r.get("failures") or 0)
    return out


def records_newest_first(records_dir=RECORDS_DIR) -> list[str]:
    files = sorted(records_dir.glob("*.md"), reverse=True) if records_dir.exists() else []
    return [f.read_text() for f in files]


def latest(records: list[str], parse):
    """The first non-empty value of parse() over records, newest first: so a run that reviewed no
    days, or whose dbt step failed, doesn't hide the last real value."""
    for text in records:
        value = parse(text)
        if value:
            return value
    return None


def acc_counts_from_record(text: str) -> dict[str, int]:
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"^\| `(acc_\w+)` \| (?:warn|fail|error) \| (\d+) \|", text, re.M)}


def reviewed_through(text: str) -> date | None:
    m = re.search(r"^- Reviewed through: (\d{4}-\d{2}-\d{2})", text, re.M)
    return date.fromisoformat(m.group(1)) if m else None


def days_to_review(last: date | None, today: date) -> tuple[list[date], int]:
    """UTC days from the day after the last review up to yesterday (at most 7), and how many were skipped."""
    yesterday = today - timedelta(days=1)
    first = (last + timedelta(days=1)) if last else yesterday
    days = [first + timedelta(days=i) for i in range((yesterday - first).days + 1)]
    skipped = max(0, len(days) - MAX_CATCH_UP_DAYS)
    return days[-MAX_CATCH_UP_DAYS:], skipped


def fetch(session, log_filter: str) -> list[dict]:
    entries, token = [], None
    while True:
        body = {"resourceNames": [f"projects/{GCP_PROJECT}"], "filter": log_filter,
                "orderBy": "timestamp asc", "pageSize": 1000}
        if token:
            body["pageToken"] = token
        resp = session.post(LOGGING_URL, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        entries += data.get("entries", [])
        token = data.get("nextPageToken")
        if not token:
            return entries


def filters(day: date) -> dict[str, str]:
    window = (f'timestamp>="{day.isoformat()}T00:00:00Z" AND '
              f'timestamp<"{(day + timedelta(days=1)).isoformat()}T00:00:00Z"')
    return {
        "admin": f'logName="{LOG}activity" AND NOT protoPayload.methodName:"TableService" '
                 f'AND NOT protoPayload.methodName:"JobService" AND {window}',
        "raw_reads": f'logName="{LOG}data_access" AND protoPayload.metadata.tableDataRead:* '
                     f'AND protoPayload.resourceName:"/datasets/raw/tables/" AND {window}',
        "denials": f'logName:"cloudaudit.googleapis.com" AND protoPayload.status.code=7 AND {window}',
        "signins": f'logName="{LOG}data_access" AND protoPayload.serviceName=("sts.googleapis.com" OR '
                   f'"iamcredentials.googleapis.com") AND {window}',
    }


# ---------- run ----------

def review(days: list[date], session, ids: dict, allowed: set[str]) -> tuple[list[dict], dict]:
    alerts, counts = [], defaultdict(int)
    for day in days:
        f = filters(day)
        got = {name: fetch(session, flt) for name, flt in f.items()}
        for name, rows in got.items():
            counts[name] += len(rows)
        alerts += check_admin(got["admin"], ids)
        alerts += check_raw_reads(got["raw_reads"], ids, allowed)
        alerts += check_denials(got["denials"], ids)
        alerts += check_signins(got["signins"], ids)
    return alerts, dict(counts)


def _session():
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/logging.read"])
    return AuthorizedSession(creds)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--day", type=date.fromisoformat, help="review this UTC day only")
    ap.add_argument("--check", action="store_true", help="exit 1 if the last review raised alerts or didn't run")
    args = ap.parse_args(argv)
    if args.check:
        return check_result()

    today = datetime.now(timezone.utc).date()
    records = records_newest_first()
    last_reviewed = latest(records, reviewed_through)
    result = {"status": "ok", "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "days": [], "skipped_days": 0, "alerts": [], "known_findings": [], "entries_checked": {}, "notes": []}
    if args.day:
        days, skipped = [args.day], 0
    else:
        days, skipped = days_to_review(last_reviewed, today)
    result["days"], result["skipped_days"] = [d.isoformat() for d in days], skipped
    if skipped:
        result["notes"].append(f"{skipped} earlier day(s) were not reviewed (more than {MAX_CATCH_UP_DAYS} days behind).")

    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    if in_actions and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        result["status"] = "not_run"
        result["notes"].append("The log reader account isn't set up, so the logs weren't read (setup step O6).")
    else:
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") == "":
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  # empty means "not set"; use the local sign-in
        ids = load_identities(os.environ.get("ECT_MAINTAINER_PRINCIPAL"))
        if not os.environ.get("ECT_MAINTAINER_PRINCIPAL"):
            result["notes"].append("ECT_MAINTAINER_PRINCIPAL isn't set, so the maintainer shows as an unknown identity.")
        try:
            alerts, counts = review(days, _session(), ids, raw_roles())
            result["alerts"], result["entries_checked"] = alerts, counts
        except Exception as e:  # noqa: BLE001 - recorded, and --check fails the run
            result["status"] = "not_run"
            result["notes"].append(f"The logs couldn't be read: {type(e).__name__}.")

    current = acc_counts_from_results()
    if current is None:
        result["notes"].append("No dbt results, so the access check findings weren't compared.")
    else:
        acc_alerts, known = check_access_findings(current, latest(records, acc_counts_from_record) or {})
        result["alerts"] += acc_alerts
        result["known_findings"] = known

    reviewed = days if result["status"] == "ok" and not args.day else []
    through = reviewed[-1] if reviewed else last_reviewed
    result["reviewed_through"] = through.isoformat() if through else None
    OUTPUT_DIR.mkdir(exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2))
    print(f"Security review: {result['status']}, {len(result['alerts'])} alert(s), days {result['days']}. "
          f"Wrote {RESULT_PATH}")
    return 0


def _when(first_seen: str) -> str:
    """'2026-11-27 09:23 UTC (04:23 New York)' from an ISO timestamp."""
    if not first_seen:
        return "this run (from today's dbt results)"
    t = _ts(first_seen)
    return f"{t:%Y-%m-%d %H:%M} UTC ({t.astimezone(NY):%H:%M} New York)"


TRIAGE_STEPS = [
    "How to triage (POL-09 statement 15: within 1 business day of this run):",
    "  1. For each alert, ask: was this change expected? Expected means planned work with a",
    "     Jira ticket, a setup step, or Google changing its own accounts automatically.",
    "  2. Expected: record each alert and why in a Jira triage ticket (GOV), then close it.",
    "  3. Not expected, or you can't tell: treat it as a possible incident and open a",
    "     Security Incidents (SI) ticket (POL-08).",
]


def check_lines(r: dict, record: str | None = None) -> list[str]:
    """The step log text: each alert with when, who and what changed, then how to triage it."""
    days = r.get("days") or []
    span = (days[0] if len(days) == 1 else f"{days[0]} to {days[-1]}") if days else "no days"
    n = len(r["alerts"])
    if not n:
        return [f"Security review of {span} (UTC): no alerts."]
    lines = [f"Security review of {span} (UTC): {n} alert{'s' if n > 1 else ''} to triage.", ""]
    for i, a in enumerate(r["alerts"], 1):
        times = f"; {a['count']} times" if a["count"] > 1 else ""
        lines += [f"ALERT {i} of {n}: {a['severity']}",
                  f"  What:   {a['title']}",
                  f"  When:   {_when(a['first_seen'])}{' (first)' if times else ''}{times}",
                  f"  Who:    {a['identity']}",
                  f"  Change: {a['detail']}", ""]
    lines += TRIAGE_STEPS
    if record:
        lines.append(f"Full details: {record}, section 'Security review (POL-09)'.")
    return lines


def _summary_markdown(r: dict, record: str | None) -> str:
    """The same, as a table for the run's summary page on GitHub."""
    out = ["## Security review: alerts to triage", "",
           "| # | Severity | What | When (first) | Who | Change | Count |", "|---|---|---|---|---|---|---|"]
    for i, a in enumerate(r["alerts"], 1):
        out.append(f"| {i} | {a['severity']} | {a['title']} | {_when(a['first_seen'])} | {a['identity']} | "
                   f"{a['detail']} | {a['count']} |")
    out += ["", *[s.strip() for s in TRIAGE_STEPS]]
    if record:
        out.append(f"\nFull details: `{record}`.")
    return "\n".join(out) + "\n"


def check_result(path=RESULT_PATH, records_dir=RECORDS_DIR) -> int:
    if not path.exists():
        print("Security review didn't run: no result file.")
        return 1
    r = json.loads(path.read_text())
    if r["status"] != "ok":
        print("Security review didn't run: " + " ".join(r["notes"]))
        return 1
    newest = sorted(records_dir.glob("*.md"))[-1:] if records_dir.exists() else []
    record = f"data-platform/run-records/{newest[0].name}" if newest else None
    print("\n".join(check_lines(r, record)))
    if r["alerts"]:
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
                f.write(_summary_markdown(r, record))
        return 1
    return 0


def record_lines(path=RESULT_PATH) -> list[str]:
    """The run record section (called by ect-record)."""
    if not path.exists():
        return ["## Security review (POL-09)", "", "Did not run: no result file.", ""]
    r = json.loads(path.read_text())
    lines = ["## Security review (POL-09)", "",
             f"- Status: {r['status']}",
             f"- Days reviewed (UTC): {', '.join(r['days']) or 'none'}"]
    if r.get("reviewed_through"):
        lines.append(f"- Reviewed through: {r['reviewed_through']}")
    checked = r.get("entries_checked") or {}
    if checked:
        lines.append("- Log entries checked: " + ", ".join(f"{k} {v:,}" for k, v in checked.items()))
    lines.append(f"- Alerts: {len(r['alerts'])}")
    lines += [f"- Note: {n}" for n in r["notes"]]
    lines.append("")
    if r["alerts"]:
        lines += ["| Alert | Severity | Identity | Detail | Count | First seen (UTC) |", "|---|---|---|---|---|---|"]
        for a in r["alerts"]:
            lines.append(f"| {a['title']} | {a['severity']} | {a['identity']} | {a['detail']} | {a['count']} | {a['first_seen'] or '—'} |")
        lines.append("")
    if r["known_findings"]:
        lines.append("Known access check findings, unchanged or lower since the last run (no alert): " +
                     ", ".join(f"`{k['test']}` {k['count']}" for k in r["known_findings"]) + ".")
        lines.append("")
    return lines


if __name__ == "__main__":
    sys.exit(main())
