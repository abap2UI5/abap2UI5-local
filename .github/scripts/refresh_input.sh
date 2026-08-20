#!/usr/bin/env bash
# Refresh input/ from an abap2UI5 source tree, validate the copy with
# abaplint (abaplint.jsonc points at /input) and push the change to main.
#
# Single implementation of the refresh sequence, used from two sides:
#   - update_input.yaml in this repo (monthly safety net / manual run)
#   - trigger_local.yaml in abap2UI5/abap2UI5 (on every upstream push;
#     it checks out this repo and calls the script from that checkout)
#
# Usage: refresh_input.sh <path-to-abap2UI5-src> [upstream-sha]
#
# The SHA is optional and only ever ends up in the commit message. It matters
# because the message used to name the RELEASE - "update input to abap2UI5
# v1.143.0" - and the version constant only moves on a release, so a week of
# upstream commits produced a week of identical messages (three within 40
# minutes on 2026-08-17). The history then cannot answer the one question it
# is asked: which upstream commit is this snapshot? Derived from the source
# checkout when the caller does not pass it.
# Must run inside a checkout of abap2UI5-local with push access to main.
set -euo pipefail

upstream_src=$1
upstream_sha=${2:-}
if [ -z "$upstream_sha" ]; then
  upstream_sha=$(git -C "$(dirname "$upstream_src")" rev-parse HEAD 2>/dev/null || true)
fi

cd "$(dirname "$0")/../.."

rm -rf input
cp -r "$upstream_src" input

npx --yes @abaplint/cli@latest

version=$(grep -oP "VALUE \`\K[0-9.]+" input/02/z2ui5_if_app.intf.abap)
git config user.name 'github-actions[bot]'
git config user.email 'github-actions[bot]@users.noreply.github.com'
git add -A input
if git diff --cached --quiet; then
  echo "input: no changes"
else
  if [ -n "$upstream_sha" ]; then
    git commit -m "update input to abap2UI5 v${version} (@${upstream_sha:0:12})" \
               -m "abap2UI5/abap2UI5@${upstream_sha}"
  else
    # No SHA to be had - say that in the message rather than implying the
    # snapshot is unidentifiable for some more interesting reason.
    git commit -m "update input to abap2UI5 v${version} (upstream commit unknown)"
  fi
  git push origin main
fi
