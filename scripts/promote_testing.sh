#!/bin/sh
# Usage: sh scripts/promote_testing.sh v1.0.8-testing
# Safe promotion: requires clean tree; testing must fast-forward.
set -eu
source_branch=${1:?Specify the version branch, e.g. v1.0.8-testing}
if [ -n "$(git status --porcelain)" ]; then
  echo 'ERROR: working tree is not clean' >&2; exit 1
fi
git fetch origin
# Both branches must already exist on GitHub.
git rev-parse --verify "origin/$source_branch" >/dev/null
git rev-parse --verify origin/testing >/dev/null
if ! git merge-base --is-ancestor origin/testing "origin/$source_branch"; then
  echo 'ERROR: testing cannot fast-forward; use a reviewed PR instead.' >&2; exit 1
fi
printf 'Will fast-forward origin/testing to origin/%s. Continue? [y/N] ' "$source_branch"
read answer
[ "$answer" = y ] || exit 0
git push origin "refs/remotes/origin/$source_branch:refs/heads/testing"
echo 'Promoted. Streamlit testing app will redeploy if linked to testing branch.'
