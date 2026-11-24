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
