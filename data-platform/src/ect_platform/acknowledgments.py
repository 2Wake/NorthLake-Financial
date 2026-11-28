"""Daily policy acknowledgment summary (owner decision 2026-11-28: one comment a day, not one per person).

    uv run ect-ack-summary            # count from marts.fct_policy_acknowledgments, write the summary
    uv run ect-ack-summary --post     # also post it as a comment on the announcement (once per day)

Counts PEOPLE, not documents: a person is done when every document they must acknowledge (the 15
policies and DOC-04) is acknowledged. On the first run after a deadline it adds the final count: how
many people due that day met it. Writes output/ack_summary.json; `ect-record` puts it in the run record.

Posting needs CONFLUENCE_USER and CONFLUENCE_API_TOKEN (GitHub secrets; setup part K). Without them the
summary is still written and recorded, and the record says it wasn't posted. Posting never fails the
run: a failure is recorded instead. Before posting it looks for today's comment, so a second run on the
same day doesn't post twice.

The acknowledgments are SIMULATED (generator 0.5.0), so every comment is marked [Simulated].
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta

from .config import GCP_PROJECT, LOCATION, MAX_BYTES_BILLED, OUTPUT_DIR
from .sim import NY

SUMMARY_PATH = OUTPUT_DIR / "ack_summary.json"
SITE = "https://empire-city-taxi.atlassian.net/wiki"
BLOG_ID = "950312"   # "Action needed: ... acknowledge by December 9" (DOC-04 and the 15 policies)

# A final count is given for a due date shared by a group (the announcement's deadline for everyone
# employed then: December 9 for the policies, December 14 for DOC-04), not for one new hire's own date.
GROUP_DEADLINE_MIN = 20

SQL = f"""
with people as (
    select employee_id,
           logical_and(ack_status = 'acknowledged') as done,
           logical_or(ack_status = 'overdue') as overdue,
           max(acknowledged_on) as last_ack
    from `{GCP_PROJECT}.marts.fct_policy_acknowledgments`
    group by 1
),
by_deadline as (
    select due_on, employee_id, logical_and(coalesce(on_time, false)) as met
    from `{GCP_PROJECT}.marts.fct_policy_acknowledgments`
    group by 1, 2
)
select
    (select count(*) from people) as people,
    (select countif(done) from people) as done,
    (select countif(overdue) from people) as overdue,
    (select countif(done and last_ack = @as_of) from people) as done_on_day,
    (select count(*) from `{GCP_PROJECT}.marts.fct_policy_acknowledgments`) as acks_required,
    (select countif(ack_status = 'acknowledged') from `{GCP_PROJECT}.marts.fct_policy_acknowledgments`) as acks_done,
    (select min(due_on) from `{GCP_PROJECT}.marts.fct_policy_acknowledgments` where due_on > @as_of) as next_due,
    array(select as struct due_on, count(*) as people, countif(met) as met
          from by_deadline where due_on = @as_of group by 1
          having count(*) >= {GROUP_DEADLINE_MIN}) as deadlines_today
"""


def _long(d: date) -> str:
    return f"{d:%A, %B} {d.day}, {d.year}"


def as_of_day(last_run_path=OUTPUT_DIR / "last_run.json") -> date:
    """The newest day loaded into raw: the data the counts describe (normally yesterday, New York)."""
    if last_run_path.exists():
        run = json.loads(last_run_path.read_text())
        if run.get("days"):
            return date.fromisoformat(run["days"][-1]["batch_date"])
        try:
            return date.fromisoformat(run.get("last_loaded_before", ""))
        except ValueError:
            pass
    return datetime.now(NY).date() - timedelta(days=1)


def summarize(c: dict, as_of: date) -> dict:
    """Counts -> the comment's lines (plain text) and the final lines for any deadline that was as_of."""
    people, done = c["people"], c["done"]
    left = people - done
    pct = round(100 * done / people) if people else 0
    lines = [f"{done} of {people} people have acknowledged everything ({pct}%). {left} still to go."]
    if c["done_on_day"]:
        lines.append(f"{c['done_on_day']} finished on {_long(as_of)}.")
    if c["overdue"]:
        lines.append(f"{c['overdue']} are past their due date. Their managers and the VP People are told "
                     "(POL-05 statement 5.11.2).")
    if c.get("next_due"):
        lines.append(f"Next due date: {_long(date.fromisoformat(str(c['next_due'])))}.")
    finals = []
    for d in c.get("deadlines_today") or []:
        missed = d["people"] - d["met"]
        pct_met = round(100 * d["met"] / d["people"]) if d["people"] else 0
        finals.append(f"Deadline {_long(date.fromisoformat(str(d['due_on'])))} has passed: {d['met']} of "
                      f"{d['people']} people due that day met it ({pct_met}%); {missed} did not.")
    return {"as_of": as_of.isoformat(), "counts": {k: v for k, v in c.items() if k != "deadlines_today"},
            "deadlines_today": c.get("deadlines_today") or [], "lines": lines, "final_lines": finals}


def comment_html(s: dict) -> str:
    as_of = date.fromisoformat(s["as_of"])
    title = f"Acknowledgment update for {_long(as_of)}"
    items = "".join(f"<li><p>{line}</p></li>" for line in s["final_lines"] + s["lines"])
    return (f"<p><em>[Simulated]</em> <strong>{title}</strong> (from the daily data run)</p><ul>{items}</ul>"
            "<p>Haven't acknowledged yet? Reply to this post with: \"I have read and agree to follow the "
            "policies and the Electronic Monitoring Notice.\" Drivers: use the ECT Driver app.</p>"
            "<p>Jordan Ellis, Data Governance Manager</p>")


def _request(method: str, path: str, body: dict | None = None) -> dict:
    token = base64.b64encode(f"{os.environ['CONFLUENCE_USER']}:{os.environ['CONFLUENCE_API_TOKEN']}".encode()).decode()
    req = urllib.request.Request(f"{SITE}{path}", method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Basic {token}", "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read() or b"{}")


def already_posted(title: str) -> str | None:
    path = f"/api/v2/blogposts/{BLOG_ID}/footer-comments?body-format=storage&limit=100"
    while path:
        page = _request("GET", path)
        for c in page.get("results", []):
            if title in c.get("body", {}).get("storage", {}).get("value", ""):
                return c["id"]
        nxt = page.get("_links", {}).get("next")
        path = nxt.removeprefix("/wiki") if nxt else None
    return None


def post(s: dict) -> str:
    """Post today's comment once. Returns a line for the run record."""
    if not (os.environ.get("CONFLUENCE_USER") and os.environ.get("CONFLUENCE_API_TOKEN")):
        return "Not posted: Confluence credentials aren't set up (setup part K)."
    title = f"Acknowledgment update for {_long(date.fromisoformat(s['as_of']))}"
    try:
        existing = already_posted(title)
        if existing:
            return f"Already posted today: comment {existing} on blog {BLOG_ID}."
        made = _request("POST", "/api/v2/footer-comments",
                        {"blogPostId": BLOG_ID, "body": {"representation": "storage", "value": comment_html(s)}})
        return f"Posted: comment {made.get('id')} on blog {BLOG_ID}."
    except Exception as e:  # noqa: BLE001 - recorded, never fails the run
        return f"Posting failed ({type(e).__name__}); post the text above by hand."


def record_lines(path=SUMMARY_PATH) -> list[str]:
    """The run record section (called by ect-record)."""
    head = ["## Policy acknowledgments (simulated)", ""]
    if not path.exists():
        return head + ["Not counted this run (dbt didn't finish).", ""]
    s = json.loads(path.read_text())
    c = s["counts"]
    out = head + [f"- Data through: {s['as_of']}",
                  f"- People: {c['done']} of {c['people']} done, {c['people'] - c['done']} left, {c['overdue']} overdue",
                  f"- Acknowledgments: {c['acks_done']:,} of {c['acks_required']:,}"]
    out += [f"- Final: {line}" for line in s["final_lines"]]
    out += [f"- Comment: {s.get('posted', 'not posted (run without --post)')}", "",
            "Comment text:", ""] + [f"> {line}" for line in s["final_lines"] + s["lines"]] + [""]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--post", action="store_true", help="post the summary on the announcement (once per day)")
    args = ap.parse_args(argv)

    from google.cloud import bigquery
    as_of = as_of_day()
    client = bigquery.Client(project=GCP_PROJECT, location=LOCATION)
    config = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED,
                                     query_parameters=[bigquery.ScalarQueryParameter("as_of", "DATE", as_of)])
    row = dict(next(iter(client.query(SQL, job_config=config).result())))
    row["deadlines_today"] = [dict(d) for d in row["deadlines_today"]]
    s = summarize(row, as_of)
    if args.post:
        s["posted"] = post(s)
    OUTPUT_DIR.mkdir(exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(s, indent=2, default=str))
    print("\n".join(s["final_lines"] + s["lines"] + ([s["posted"]] if "posted" in s else [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
