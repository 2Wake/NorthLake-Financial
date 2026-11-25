# Setting up the daily run (GitHub Actions + keyless Google sign-in)

One-time setup, all done in web consoles. When it's finished, the workflow in
[`.github/workflows/daily-refresh.yml`](../../.github/workflows/daily-refresh.yml) runs every
morning: it generates and loads yesterday's data, rebuilds dbt, and commits a run record to
`data-platform/run-records/`.

**How the sign-in works (no keys):** GitHub gives each workflow run a short-lived identity token
saying "I am a run of repository 2Wake/empire-city-taxi-grc". Google trusts that token (through a
*Workload Identity pool*) and lets the run act as one service account, `ect-pipeline`, for about an
hour. No password or key file exists anywhere, so there is nothing to leak or rotate.

**What the pipeline can do (least privilege):** run BigQuery jobs, and edit data in `raw`, `staging`
and `marts` only. It can't change settings, billing or anything else.

---

## A. Turn on three Google APIs

Google Cloud console → **APIs & Services → Library**. Search for each name, open it, click **Enable**:
1. **Identity and Access Management (IAM) API**
2. **IAM Service Account Credentials API**
3. **Security Token Service API**

## B. Create the service account

**IAM & Admin → Service Accounts → + Create service account**
1. Name: `ect-pipeline`. The ID fills in as `ect-pipeline`. Description: `Daily data refresh (GitHub Actions)`. Click **Create and continue**.
2. **Grant this service account access to project** → Role: **BigQuery Job User**. Click **Continue**, then **Done**.
3. Note the email: `ect-pipeline@empire-city-taxi.iam.gserviceaccount.com`.

> ⚠️ Don't create a key for it (no "Keys → Add key"). Keyless sign-in replaces keys.

## C. Give it access to the three datasets

**BigQuery** → Explorer → click the dataset **`raw`** → **Share** (or **Sharing → Permissions**) → **Add principal**
- New principal: `ect-pipeline@empire-city-taxi.iam.gserviceaccount.com`
- Role: **BigQuery Data Editor** → **Save**

Repeat for **`staging`** and **`marts`**.

> ⚠️ Grant it on the datasets, not on the whole project, which would be broader than needed.

## D. Create the Workload Identity pool and provider

**IAM & Admin → Workload Identity Federation → Create pool** (or **Get started**)
1. **Pool:** name `github`, Pool ID `github`. Click **Continue**.
2. **Provider:** select **OpenID Connect (OIDC)**.
   - Provider name `github-actions`, Provider ID `github-actions`
   - Issuer (URL): `https://token.actions.githubusercontent.com`
   - Audiences: **Default audience**
   - Click **Continue**.
3. **Provider attributes:** add three mappings:

   | Google | OIDC |
   |---|---|
   | `google.subject` | `assertion.sub` |
   | `attribute.repository` | `assertion.repository` |
   | `attribute.repository_owner` | `assertion.repository_owner` |

4. **Attribute conditions → Add condition:**
   ```
   assertion.repository == "2Wake/empire-city-taxi-grc"
   ```
   This makes Google accept tokens from **this repository only**.
5. Click **Save**.

## E. Let the pool use the service account

On the `github` pool's page → **Grant access** → **Grant access using service account impersonation**
- Service account: `ect-pipeline`
- Select principals: attribute name **repository**, attribute value `2Wake/empire-city-taxi-grc`
- Click **Save**. If a "Configure your application" box appears, **Dismiss** it. No file is needed.

## F. Tell GitHub which pool and account to use

GitHub repo → **Settings → Secrets and variables → Actions → Variables** tab → **New repository variable**

| Name | Value |
|---|---|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github/providers/github-actions` |
| `GCP_SERVICE_ACCOUNT` | `ect-pipeline@empire-city-taxi.iam.gserviceaccount.com` |

`<PROJECT_NUMBER>` is the number on the Google Cloud console **Dashboard** (Project info card), not the project ID.

> These are identifiers, not secrets, so **Variables** is correct. Nothing goes in **Secrets**.

## G. Test it

GitHub repo → **Actions** → **Daily data refresh** → **Run workflow** → **Run workflow**.

A green check means it worked: a new file appears in `data-platform/run-records/`. If a step is
red, open it and share the error.

---

## H. The log reader account for the daily security review (POL-09)

The daily run also reviews yesterday's Google Cloud audit logs (`ect-security-review`). It reads them as
a **separate account, `ect-monitor`**, that can only read logs, so the pipeline never reads the audit
trail about itself (POL-09 statement 8). Same keyless sign-in as `ect-pipeline`: no key.

### H1. Create the account

**IAM & Admin → Service Accounts → + Create service account**
1. Name: `ect-monitor`. Description: `Daily security review: reads audit logs (POL-09)`. Click **Create and continue**.
2. **Grant this service account access to project** → Role: type `Private Logs Viewer` and pick
   **Private Logs Viewer** (under Logging). Click **Continue**, then **Done**.

> ⚠️ Pick **Private** Logs Viewer, not plain **Logs Viewer**: plain Logs Viewer can't see Data Access
> logs (who read which table), which most of the checks need. Neither role can delete logs.
> ⚠️ Don't create a key for it.

### H2. Let the workflow use it

**IAM & Admin → Workload Identity Federation** → pool **`github`** → **Grant access** →
**Grant access using service account impersonation**
- Service account: `ect-monitor`
- Select principals: attribute name **repository**, attribute value `2Wake/empire-city-taxi-grc`
- Click **Save**. If a "Configure your application" box appears, **Dismiss** it.

### H3. Tell GitHub the account name (a variable)

GitHub repo → **Settings → Secrets and variables → Actions → Variables** tab → **New repository variable**

| Name | Value |
|---|---|
| `GCP_MONITOR_SERVICE_ACCOUNT` | `ect-monitor@empire-city-taxi.iam.gserviceaccount.com` |

### H4. Tell GitHub who the maintainer is (a secret)

Same page → **Secrets** tab (not Variables) → **New repository secret**

| Name | Value |
|---|---|
| `ECT_MAINTAINER_PRINCIPAL` | the Google account email you sign in to the console with |

The logs name you by your email. The review uses this secret to show you as `maintainer` in the
public run record instead of an unknown identity. It's a **secret** so it's hidden in workflow logs
and never stored in a file.

### H5. Test it

**Actions → Daily data refresh → Run workflow.** In the run record, look for the **Security review
(POL-09)** section with `Status: ok`.

Expect the **first** run to fail at its last step, "Fail the run if the security review raised
alerts": it reviews the previous day, and that day contains your own setting changes (IAM and logging
changes), which are exactly what it's meant to catch. Each alert is triaged in Jira (POL-09
statement 15). The setup changes in H1 and H2 will show up in the next day's review the same way.

If the section says `Status: not_run`, the sign-in in H2 or the variable in H3 is missing.

## I. The watchdog

Nothing to set up. `.github/workflows/watchdog.yml` runs at 12:05 New York time and fails (GitHub
emails you) if there's no run record for today. To test it by hand: **Actions → Watchdog (daily run)
→ Run workflow**. Before noon it just says "Skipped".
