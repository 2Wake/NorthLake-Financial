#!/usr/bin/env bash
# Save run records and configuration-check results to the `records` branch.
# main only changes through pull requests (GOV-77 ruleset), and GitHub can't let Actions bypass that
# on a personal repository, so evidence goes to its own branch. A second ruleset stops `records`
# being deleted or rewritten. The first run creates the branch, starting with the records on main.
# Usage: save-records.sh "<commit message>"
set -euo pipefail
cd "$GITHUB_WORKSPACE"
R="${RUNNER_TEMP:-/tmp}/records"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
if git fetch -q origin records 2>/dev/null; then
  git worktree add -q --detach "$R" FETCH_HEAD
else
  git worktree add -q --orphan -b records "$R"
fi
for d in run-records config-checks; do
  if compgen -G "data-platform/$d/*.md" >/dev/null; then
    mkdir -p "$R/data-platform/$d"
    cp data-platform/"$d"/*.md "$R/data-platform/$d/"
  fi
done
cd "$R"
git add data-platform
if git diff --cached --quiet; then echo "Nothing new to save."; exit 0; fi
git commit -q -m "$1"
for attempt in 1 2 3; do
  if git push -q origin HEAD:records; then echo "Saved to the records branch."; exit 0; fi
  # Another workflow saved first: put this commit on top of theirs and try again.
  git fetch -q origin records && git rebase -q FETCH_HEAD
done
echo "Couldn't save to the records branch after 3 tries."; exit 1
