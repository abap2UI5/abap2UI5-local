#!/usr/bin/env bash
# Refresh input/ from an abap2UI5 source tree, validate the copy with
# abaplint (abaplint.jsonc points at /input) and push the change to main.
#
# Single implementation of the refresh sequence, used from two sides:
#   - update_input.yaml in this repo (monthly safety net / manual run)
#   - trigger_local.yaml in abap2UI5/abap2UI5 (on every upstream push;
#     it checks out this repo and calls the script from that checkout)
#
# Usage: refresh_input.sh <path-to-abap2UI5-src>
# Must run inside a checkout of abap2UI5-local with push access to main.
set -euo pipefail

upstream_src=$1
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
  git commit -m "update input to abap2UI5 v${version}"
  git push origin main
fi
