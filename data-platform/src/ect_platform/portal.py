"""ECT Data & Governance Portal: a private, read-only view of the catalog and compliance (GOV-179).

    uv run ect-portal              # collect, build and open the portal
    uv run ect-portal --no-open    # collect and build only

First slice: POL-03 Data Classification & Handling. For every POL-03 statement it shows the automated
check behind it (CLS-01 to CLS-08) and that check's latest result, plus an explorer of every table and
column in `raw`, `staging` and `marts` with its classification, owner, steward and labels.

It only reads (owner decision P2, 2026-11-28): the register, BigQuery metadata and
`marts.fct_classification_findings`. Changes are asked for with "Request an edit", which opens a
prefilled Jira task for the steward to propose and the owner to approve.

Private (decision P1): the output goes to output/portal/ (git-ignored) and must never be committed or
published. It holds metadata and findings only, never row-level data, and is Internal (POL-03).
"""
import argparse
import csv
import html
import json
import re
import sys
import webbrowser
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from .config import GCP_PROJECT, LOCATION, MAX_BYTES_BILLED, OUTPUT_DIR, ROOT

PORTAL_DIR = OUTPUT_DIR / "portal"
REGISTER_PATH = ROOT / "dbt" / "seeds" / "governance" / "column_classification_register.csv"
MANIFEST_PATH = ROOT / "dbt" / "target" / "manifest.json"
DATASETS = ("raw", "staging", "marts")
TIERS = ("Public", "Internal", "Sensitive", "Confidential", "Secret")
# Labeling Standard: required on every table
REQUIRED_LABELS = ("domain", "layer", "data_owner", "data_steward", "classification", "source_system", "data_origin")

JIRA = "https://empire-city-taxi.atlassian.net"
WIKI = f"{JIRA}/wiki/spaces/ECTG/pages"
GOV_PROJECT_ID = "10000"
TASK_TYPE_ID = "10004"
EDIT_LABEL = "catalog-edit-request"
POL03_URL = f"{WIKI}/426094"

RULES = {
    "CLS-01": "Column not classified",
    "CLS-02": "Register entry for missing column",
    "CLS-03": "Classification not approved",
    "CLS-04": "Table label inconsistent with columns",
    "CLS-05": "Classification changes between raw and staging",
    "CLS-06": "Above the marts cap",
    "CLS-07": "Register steward differs from table label",
    "CLS-08": "Invalid classification value",
}

# POL-03 v2.0 section 5. "rules" are the checks that test the statement; "kind" says how it's checked.
STATEMENTS = [
    (1, "Every data element has exactly one of the five tiers, spelled exactly. Cardholder data is Secret.",
     ["CLS-01", "CLS-08"], "auto"),
    (2, "Classified at column level; a table takes the highest classification of its columns.", ["CLS-04"], "auto"),
    (3, "The steward proposes and the owner approves before production; CISO and Privacy Officer review Secret "
        "and Confidential.", ["CLS-03"], "auto"),
    (4, "A column found unclassified is proposed within 5 and approved within 10 business days.",
     ["CLS-01", "CLS-03"], "partial"),
    (5, "Unclassified data is handled as Confidential (or Secret if it might hold cardholder or similar data).", [],
     "manual"),
    (6, "A column copied without change keeps its source classification.", ["CLS-05"], "auto"),
    (7, "Classifications are recorded in the register with owner, steward, approver and approval date.",
     ["CLS-03"], "auto"),
    (8, "Every dataset and table carries the required labels; the classification label equals its highest column.",
     ["CLS-04", "CLS-07"], "auto"),
    (9, "Owners review their domain's classifications at least every 12 months.", [], "review"),
    (10, "Data is handled by tier (store, share, print, analytics, dispose).", [], "manual"),
    (11, "`marts` is capped at Sensitive; tested on every daily run.", ["CLS-06"], "auto"),
    (12, "Cardholder data also follows POL-04 and DOC-01.", [], "manual"),
    (13, "No classified data in labels, tickets, pages, commits or chat; the public repository holds Public only.",
     [], "manual"),
    (14, "Secret data found in the data platform is an incident and removed within 5 business days.", [], "secret"),
    (15, "The CLS checks run on every daily run; findings are fixed within 10 business days.", [], "fresh"),
    (16, "Classification accuracy for Secret and Confidential is reported to the council; target 100%.", [],
     "accuracy"),
]


# ---------- collect ----------

def parse_labels(option_value: str) -> dict:
    """BigQuery's TABLE_OPTIONS labels text, e.g. [STRUCT("domain", "trips"), ...], as a dict."""
    return dict(re.findall(r'STRUCT\("([^"]+)", "([^"]*)"\)', option_value or ""))


def read_register(path: Path = REGISTER_PATH) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def read_manifest(path: Path = MANIFEST_PATH) -> dict:
    """Descriptions from the local dbt manifest, keyed (layer, table) -> {"table": str, "columns": {name: str}}."""
    if not path.exists():
        return {"generated_at": None, "docs": {}}
    m = json.loads(path.read_text())
    docs = {}
    for node in list(m.get("nodes", {}).values()) + list(m.get("sources", {}).values()):
        if node.get("resource_type") not in ("model", "seed", "source"):
            continue
        layer = node.get("schema")
        name = node.get("identifier") or node.get("alias") or node.get("name")
        docs[f"{layer}.{name}"] = {
            "table": node.get("description") or "",
            "columns": {c: v.get("description") or "" for c, v in node.get("columns", {}).items()},
        }
    return {"generated_at": m.get("metadata", {}).get("generated_at"), "docs": docs}


def query_bigquery() -> dict:
    """Metadata and findings only. Every query is capped by MAX_BYTES_BILLED."""
    from google.cloud import bigquery

    client = bigquery.Client(project=GCP_PROJECT, location=LOCATION)
    cfg = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED, labels={"pipeline": "ect-portal"})

    def rows(sql):
        return [dict(r.items()) for r in client.query(sql, job_config=cfg).result()]

    columns, labels, tables = [], {}, []
    for ds in DATASETS:
        columns += rows(f"select '{ds}' as layer, table_name, column_name, data_type, ordinal_position "
                        f"from `{GCP_PROJECT}.{ds}.INFORMATION_SCHEMA.COLUMNS`")
        for r in rows(f"select table_name, option_value from `{GCP_PROJECT}.{ds}.INFORMATION_SCHEMA.TABLE_OPTIONS` "
                      f"where option_name = 'labels'"):
            labels[f"{ds}.{r['table_name']}"] = parse_labels(r["option_value"])
        tables += rows(f"select '{ds}' as layer, table_id as table_name, row_count, size_bytes, "
                       f"timestamp_millis(last_modified_time) as last_modified, "
                       f"case type when 1 then 'table' when 2 then 'view' else 'other' end as kind "
                       f"from `{GCP_PROJECT}.{ds}.__TABLES__`")
    findings = rows(f"select rule_id, layer, table_name, column_name, detail, evaluated_at "
                    f"from `{GCP_PROJECT}.marts.fct_classification_findings`")
    accuracy = rows(f"select countif(verdict = 'correct') as correct, count(*) as total "
                    f"from `{GCP_PROJECT}.marts.fct_classification_scorecard` where is_high_risk")[0]
    return {"columns": columns, "labels": labels, "tables": tables, "findings": findings, "accuracy": accuracy}


# ---------- assemble ----------

def edit_link(subject: str, current: str, steward: str = "", owner: str = "") -> str:
    """A prefilled Jira task. The steward proposes the change and the owner approves it (POL-03 statement 3)."""
    description = (
        "h2. Description\n"
        f"Requested change to: {subject}\n"
        f"Current value: {current}\n"
        "Requested value: (fill in)\n\n"
        "h2. Why it matters\n(fill in)\n\n"
        "h2. Potential blockers\n(fill in)\n\n"
        "h2. Intended outcome\n"
        f"The steward ({steward or 'domain steward'}) proposes the change and the owner ({owner or 'data owner'}) "
        "approves it (POL-03 statement 3). It is then made in Knowledge Catalog, or in the repository register "
        "by pull request until the GOV-167 import.\n\n"
        "Raised from the ECT Data & Governance Portal."
    )
    return f"{JIRA}/secure/CreateIssueDetails!init.jspa?" + urlencode({
        "pid": GOV_PROJECT_ID, "issuetype": TASK_TYPE_ID, "labels": EDIT_LABEL,
        "summary": f"Catalog edit request: {subject}"[:250], "description": description,
    })


def _iso(v):
    return v.isoformat() if isinstance(v, (datetime, date)) else v


def assemble(bq: dict, register: list[dict], manifest: dict, today: date) -> dict:
    reg = {(r["layer"], r["table_name"], r["column_name"]): r for r in register}
    docs = manifest["docs"]
    findings = [{k: _iso(v) for k, v in f.items()} for f in bq["findings"]]
    by_col, by_table = {}, {}
    for f in findings:
        if f["column_name"] == "*":
            by_table.setdefault((f["layer"], f["table_name"]), []).append(f["rule_id"])
        else:
            by_col.setdefault((f["layer"], f["table_name"], f["column_name"]), []).append(f["rule_id"])

    tables = {}
    for t in bq["tables"]:
        key = f"{t['layer']}.{t['table_name']}"
        lab = bq["labels"].get(key, {})
        tables[key] = {
            "layer": t["layer"], "name": t["table_name"], "kind": t["kind"], "rows": t["row_count"],
            "bytes": t["size_bytes"], "last_modified": _iso(t["last_modified"]), "labels": lab,
            "missing_labels": [k for k in REQUIRED_LABELS if k not in lab],
            "description": docs.get(key, {}).get("table", ""),
            "findings": sorted(set(by_table.get((t["layer"], t["table_name"]), []))),
            "columns": [],
        }
    for c in sorted(bq["columns"], key=lambda c: (c["layer"], c["table_name"], c["ordinal_position"])):
        key = f"{c['layer']}.{c['table_name']}"
        if key not in tables:
            continue
        r = reg.get((c["layer"], c["table_name"], c["column_name"]), {})
        t = tables[key]
        steward = r.get("data_steward") or t["labels"].get("data_steward", "")
        owner = r.get("data_owner") or t["labels"].get("data_owner", "")
        t["columns"].append({
            "name": c["column_name"], "type": c["data_type"],
            "classification": r.get("classification", ""), "category": r.get("data_category", ""),
            "treatment": r.get("treatment", ""), "owner": owner, "steward": steward,
            "status": r.get("status", ""), "approved_by": r.get("approved_by", ""),
            "approved_on": r.get("approved_on", ""), "rationale": r.get("rationale", ""),
            "description": docs.get(key, {}).get("columns", {}).get(c["column_name"], ""),
            "findings": sorted(set(by_col.get((c["layer"], c["table_name"], c["column_name"]), []))),
            "edit": edit_link(f"{key}.{c['column_name']} classification",
                              r.get("classification") or "not classified", steward, owner),
        })

    counts = {rid: 0 for rid in RULES}
    for f in findings:
        counts[f["rule_id"]] = counts.get(f["rule_id"], 0) + 1
    last_eval = max((f["evaluated_at"] for f in findings), default=None)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "as_of": today.isoformat(),
        "manifest_generated_at": manifest["generated_at"],
        "tables": sorted(tables.values(), key=lambda t: (DATASETS.index(t["layer"]), t["name"])),
        "findings": findings,
        "rule_counts": counts,
        "statements": evaluate_statements(counts, register, last_eval, bq["accuracy"], today),
        "tier_counts": {tier: sum(1 for r in register if r["classification"] == tier) for tier in TIERS},
        "register_rows": len(register),
    }


def evaluate_statements(counts: dict, register: list[dict], last_eval, accuracy: dict, today: date) -> list[dict]:
    """One result per POL-03 statement: pass, findings, attention or manual, with a plain-language note."""
    out = []
    for num, text, rules, kind in STATEMENTS:
        n = sum(counts.get(r, 0) for r in rules)
        if kind == "auto":
            status = "findings" if n else "pass"
            note = f"{n} open finding(s) from {', '.join(rules)}" if n else f"No findings from {', '.join(rules)}"
        elif kind == "partial":
            status = "findings" if n else "pass"
            note = (f"{n} column(s) unclassified or unapproved ({', '.join(rules)}). The 5 and 10 business-day "
                    "clocks aren't measured yet: findings carry no first-found date.")
        elif kind == "review":
            stale = [r for r in register if r.get("approved_on") and
                     (today - date.fromisoformat(r["approved_on"])).days > 365]
            status = "findings" if stale else "pass"
            note = (f"{len(stale)} approved classification(s) older than 12 months" if stale else
                    "Every approved classification is less than 12 months old (computed from the register)")
        elif kind == "secret":
            secret = [f"{r['layer']}.{r['table_name']}.{r['column_name']}" for r in register
                      if r["classification"] == "Secret"]
            status = "attention" if secret else "pass"
            note = (f"{len(secret)} column(s) recorded as Secret in the data platform: {', '.join(secret)}"
                    if secret else "No column is recorded as Secret in the data platform")
        elif kind == "fresh":
            last = date.fromisoformat(str(last_eval)[:10]) if last_eval else None
            fresh = last is not None and (today - last).days <= 1
            status = "pass" if fresh else "findings"
            note = (f"Checks last ran {str(last_eval)[:16].replace('T', ' ')} UTC" if last
                    else "No check results found") + ("" if fresh else " (older than one day)")
        elif kind == "accuracy":
            c, t = accuracy.get("correct", 0), accuracy.get("total", 0)
            pct = round(100 * c / t, 1) if t else 0
            status = "pass" if t and c == t else "findings"
            note = (f"{c} of {t} Secret and Confidential columns correct ({pct}%), measured against the "
                    "simulation answer key")
        else:
            status, note = "manual", "Not checked automatically; evidence is reviewed by people"
        out.append({"number": num, "text": text, "rules": rules, "status": status, "note": note,
                    "edit": edit_link(f"POL-03 statement {num} check", note)})
    return out


# ---------- build ----------

def build_html(snapshot: dict) -> str:
    data = json.dumps(snapshot, default=str).replace("</", "<\\/")
    return (TEMPLATE
            .replace("__DATA__", data)
            .replace("__AS_OF__", html.escape(snapshot["as_of"]))
            .replace("__POL03__", POL03_URL))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--no-open", action="store_true", help="build without opening the browser")
    args = p.parse_args(argv)
    today = date.today()
    snapshot = assemble(query_bigquery(), read_register(), read_manifest(), today)
    PORTAL_DIR.mkdir(parents=True, exist_ok=True)
    (PORTAL_DIR / f"snapshot-{today.isoformat()}.json").write_text(json.dumps(snapshot, indent=1, default=str))
    page = PORTAL_DIR / "index.html"
    page.write_text(build_html(snapshot))
    cols = sum(len(t["columns"]) for t in snapshot["tables"])
    print(f"Portal built: {len(snapshot['tables'])} tables, {cols} columns, {len(snapshot['findings'])} findings.")
    print(f"Open: {page}")
    if not args.no_open:
        webbrowser.open(page.as_uri())
    return 0


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ECT Data & Governance Portal</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1b;--mute:#6b6b66;--line:#e2e2dc;--acc:#2b5fd9;
--pass:#1f7a4d;--find:#b3261e;--att:#9a6700;--man:#6b6b66}
@media(prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--ink:#ecece8;--mute:#a3a39c;--line:#33332f;
--acc:#7aa2ff;--pass:#5fc28d;--find:#ff8a80;--att:#e3b341;--man:#a3a39c}}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:20px 28px;border-bottom:1px solid var(--line);background:var(--card)}
h1{font-size:20px;margin:0}.sub{color:var(--mute);font-size:13px}
nav{display:flex;gap:4px;padding:0 28px;background:var(--card);border-bottom:1px solid var(--line)}
nav button{border:0;background:none;padding:10px 14px;font:inherit;color:var(--mute);cursor:pointer;border-bottom:2px solid transparent}
nav button.on{color:var(--ink);border-color:var(--acc)}
main{padding:24px 28px;max-width:1300px}section{display:none}section.on{display:block}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.tile b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.tile span{color:var(--mute);font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--mute);font-weight:600}tr:last-child td{border-bottom:0}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;font-weight:600;border:1px solid currentColor}
.pass{color:var(--pass)}.findings{color:var(--find)}.attention{color:var(--att)}.manual{color:var(--man)}
a{color:var(--acc)}.muted{color:var(--mute)}code{font-size:12px}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
input,select{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
input{min-width:260px}.tbl{cursor:pointer}.tbl:hover{background:color-mix(in srgb,var(--acc) 6%,transparent)}
.detail td{background:var(--bg)}.tag{font-size:11px;color:var(--mute);margin-right:8px;white-space:nowrap}
.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--att);padding:10px 14px;border-radius:6px;margin-bottom:18px}
</style></head><body>
<header><h1>ECT Data &amp; Governance Portal</h1>
<div class="sub">Snapshot __AS_OF__ · read-only · <strong>Internal: private copy, never commit or publish</strong> ·
first slice: <a href="__POL03__" target="_blank">POL-03 Data Classification &amp; Handling</a></div></header>
<nav><button class="on" data-s="pol">POL-03 compliance</button><button data-s="exp">Explore</button><button data-s="fnd">Findings</button></nav>
<main>
<section id="pol" class="on"><div class="tiles" id="tiles"></div>
<div class="note">Each statement shows the check that tests it and its latest result. Edits are never made here:
<em>Request an edit</em> opens a Jira task for the steward to propose and the owner to approve (POL-03 statement 3).</div>
<table><thead><tr><th>#</th><th>Statement</th><th>Check</th><th>Result</th><th></th></tr></thead><tbody id="stm"></tbody></table></section>
<section id="exp"><div class="bar"><input id="q" placeholder="Search tables and columns"><select id="fl"><option value="">All layers</option>
<option>raw</option><option>staging</option><option>marts</option></select><select id="ft"><option value="">All classifications</option></select>
<select id="ff"><option value="">With or without findings</option><option value="y">With findings only</option></select></div>
<table><thead><tr><th>Table</th><th>Domain</th><th>Owner / steward</th><th>Classification</th><th>Columns</th><th>Rows</th><th>Findings</th></tr></thead>
<tbody id="tbls"></tbody></table></section>
<section id="fnd"><div class="bar"><select id="fr"><option value="">All rules</option></select></div>
<table><thead><tr><th>Rule</th><th>Table</th><th>Column</th><th>Detail</th></tr></thead><tbody id="fnds"></tbody></table></section>
</main>
<script>
const D=__DATA__;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const RULES={"CLS-01":"Column not classified","CLS-02":"Register entry for missing column","CLS-03":"Classification not approved",
"CLS-04":"Table label inconsistent with columns","CLS-05":"Classification changes between raw and staging","CLS-06":"Above the marts cap",
"CLS-07":"Register steward differs from table label","CLS-08":"Invalid classification value"};
const LABEL={pass:'Pass',findings:'Findings',attention:'Attention',manual:'Manual'};
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('nav button,section').forEach(e=>e.classList.remove('on'));
b.classList.add('on');document.getElementById(b.dataset.s).classList.add('on')});
const cols=D.tables.reduce((n,t)=>n+t.columns.length,0), classified=D.tables.reduce((n,t)=>n+t.columns.filter(c=>c.classification).length,0);
const st=s=>D.statements.filter(x=>x.status===s).length;
document.getElementById('tiles').innerHTML=[[D.tables.length,'tables'],[cols,'columns'],[Math.round(100*classified/cols)+'%','columns classified'],
[D.findings.length,'open CLS findings'],[st('pass'),'statements passing'],[st('findings')+st('attention'),'statements needing action'],[st('manual'),'checked by people']]
.map(([v,l])=>`<div class="tile"><b>${esc(v)}</b><span>${esc(l)}</span></div>`).join('');
document.getElementById('stm').innerHTML=D.statements.map(s=>`<tr><td>${s.number}</td><td>${esc(s.text)}</td>
<td>${s.rules.map(esc).join(', ')||'<span class="muted">—</span>'}</td><td><span class="pill ${s.status}">${LABEL[s.status]}</span><br>
<span class="muted">${esc(s.note)}</span></td><td><a href="${esc(s.edit)}" target="_blank">Request an edit</a></td></tr>`).join('');
const tiers=['Secret','Confidential','Sensitive','Internal','Public'];
document.getElementById('ft').innerHTML+=tiers.map(t=>`<option>${t}</option>`).join('')+'<option value="-">Not classified</option>';
Object.keys(RULES).forEach(r=>document.getElementById('fr').innerHTML+=`<option value="${r}">${r} ${esc(RULES[r])} (${D.rule_counts[r]||0})</option>`);
const open=new Set();
function nf(t){return t.findings.length+t.columns.reduce((n,c)=>n+c.findings.length,0)}
function renderTables(){const q=document.getElementById('q').value.toLowerCase(),L=document.getElementById('fl').value,
T=document.getElementById('ft').value,F=document.getElementById('ff').value;let h='';
for(const t of D.tables){if(L&&t.layer!==L)continue;const key=t.layer+'.'+t.name;
let cs=t.columns.filter(c=>(!T||(T==='-'?!c.classification:c.classification===T))&&(!q||key.includes(q)||c.name.toLowerCase().includes(q)||(c.description||'').toLowerCase().includes(q)));
if(!cs.length&&!(!T&&q&&key.includes(q)))continue;if(F&&!nf(t))continue;const lb=t.labels;
h+=`<tr class="tbl" data-k="${esc(key)}"><td><strong>${esc(key)}</strong> <span class="tag">${esc(t.kind)}</span><br><span class="muted">${esc(t.description)}</span></td>
<td>${esc(lb.domain)}</td><td>${esc(lb.data_owner)}<br><span class="muted">${esc(lb.data_steward)}</span></td><td>${esc(lb.classification)}</td>
<td>${t.columns.length}</td><td>${t.rows==null?'':Number(t.rows).toLocaleString()}</td>
<td>${nf(t)?`<span class="findings">${nf(t)}</span>`:'<span class="pass">0</span>'}${t.missing_labels.length?`<br><span class="attention">missing labels: ${t.missing_labels.map(esc).join(', ')}</span>`:''}</td></tr>`;
if(open.has(key)||q||T){h+=`<tr class="detail"><td colspan="7">${t.findings.length?`<p>Table findings: ${t.findings.map(r=>`<span class="findings">${r} ${esc(RULES[r])}</span>`).join(', ')}</p>`:''}
<p>${Object.entries(lb).map(([k,v])=>`<span class="tag">${esc(k)}=${esc(v)}</span>`).join('')}</p>
<table><thead><tr><th>Column</th><th>Type</th><th>Classification</th><th>Category / treatment</th><th>Status</th><th>Findings</th><th></th></tr></thead><tbody>
${cs.map(c=>`<tr><td><code>${esc(c.name)}</code><br><span class="muted">${esc(c.description||c.rationale)}</span></td><td>${esc(c.type)}</td>
<td>${c.classification?esc(c.classification):'<span class="findings">not classified</span>'}</td><td>${esc(c.category)}<br><span class="muted">${esc(c.treatment)}</span></td>
<td>${esc(c.status)}${c.approved_by?`<br><span class="muted">${esc(c.approved_by)} ${esc(c.approved_on)}</span>`:''}</td>
<td>${c.findings.map(r=>`<span class="findings" title="${esc(RULES[r])}">${r}</span>`).join(' ')}</td><td><a href="${esc(c.edit)}" target="_blank">Request an edit</a></td></tr>`).join('')}
</tbody></table></td></tr>`}}
document.getElementById('tbls').innerHTML=h||'<tr><td colspan="7" class="muted">No matches</td></tr>';
document.querySelectorAll('.tbl').forEach(r=>r.onclick=()=>{const k=r.dataset.k;open.has(k)?open.delete(k):open.add(k);renderTables()})}
['q','fl','ft','ff'].forEach(i=>document.getElementById(i).oninput=renderTables);renderTables();
function renderFindings(){const R=document.getElementById('fr').value;
document.getElementById('fnds').innerHTML=D.findings.filter(f=>!R||f.rule_id===R).map(f=>`<tr><td><span class="findings">${esc(f.rule_id)}</span><br>
<span class="muted">${esc(RULES[f.rule_id])}</span></td><td>${esc(f.layer+'.'+f.table_name)}</td><td><code>${esc(f.column_name)}</code></td><td>${esc(f.detail)}</td></tr>`).join('')}
document.getElementById('fr').oninput=renderFindings;renderFindings();
</script></body></html>"""


if __name__ == "__main__":
    sys.exit(main())
