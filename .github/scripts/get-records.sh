#!/usr/bin/env bash
# Copy the run records and configuration-check results from the `records` branch into this checkout,
# so steps that read earlier records (security review trends, watchdog) see all of them.
# Since GOV-77, main only changes through pull requests, so the workflows save evidence to `records`
# (see save-records.sh). Before the branch exists, the copies already on main are used.
set -euo pipefail
cd "$GITHUB_WORKSPACE"
if git fetch -q --depth=1 origin records 2>/dev/null; then
  for d in run-records config-checks; do
    git checkout FETCH_HEAD -- "data-platform/$d" 2>/dev/null || true
  done
  echo "Records copied from the records branch."
else
  echo "No records branch yet: using the records on main."
fi
