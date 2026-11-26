#!/usr/bin/env bash
# Prepares a checkout of a generated branch (standard or 702) for the shared
# namespace rename, .github/scripts/rename.mjs - the branches are what gets
# installed, input/ on main never is. Run from main's checkout, with the
# branch checkout as the argument:
#
#   .github/scripts/rename_prepare.sh <branch-checkout>
#
# It copies rename.mjs into the branch tree, installs the abaplint the
# ecosystem pins next to the branch's own devDependencies (no lockfile
# change) and limits the name to 9 characters (package.json
# config.renameMaxLength): the ICF node z2ui5_local has 11, an ICF node may
# have 15. Nothing of it is committed - the branch is rebuilt from main by
# generate_branch.yaml, and the renamed tree goes to its own branch.
set -euo pipefail
tree="$1"
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$tree/.github/scripts"
cp "$here/rename.mjs" "$tree/.github/scripts/rename.mjs"
node -e '
  const fs = require("fs");
  const file = process.argv[1] + "/package.json";
  const p = JSON.parse(fs.readFileSync(file, "utf8"));
  p.config = {
    ...(p.config || {}),
    renameMaxLength: 9,
    renameMaxLengthWhy: "the ICF node z2ui5_local has 11 characters and an ICF node at most 15",
  };
  fs.writeFileSync(file, JSON.stringify(p, null, 2) + "\n");
' "$tree"
(cd "$tree" && npm install --no-save --no-audit --no-fund @abaplint/cli@2.120.120 >/dev/null)
