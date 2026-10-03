# AGENTS.md — abap2UI5-local

Single source of truth for agents working on **abap2UI5-local**: the delivery
repository that folds the whole abap2UI5 framework into the local classes of
one HTTP handler class, `Z2UI5_CL_ABAP2UI5_LOCAL`, so that an app can run
without any other abap2UI5 installation in the system. `CLAUDE.md` next to
this file is a pointer at it, nothing more.

**Language:** English for all code, comments, docs, commit messages, PRs.

## Nothing that ships is written by hand

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. The framework code is
abap2UI5's, and a change to it is a pull request to
[abap2UI5/abap2UI5](https://github.com/abap2UI5/abap2UI5), directory `src/`.
The refresh then brings it here.

- **Never hand-edit `input/`.** It is a copy of abap2UI5's `src/`, written
  by `.github/scripts/refresh_input.sh`. That script runs from two places:
  - abap2UI5's `trigger_local.yaml`, on every push to abap2UI5 `main` that
    touches `src/`. It checks out this repository with a deploy key, runs the
    script from that checkout and pushes the result to `main` here.
  - This repository's `update_input.yaml`, monthly and by hand.

  Both delete `input/` and copy it again, so a hand edit there survives only
  until the next upstream push. A commit `update input to abap2UI5 v<version>
  (@<sha>)` on `main` is that push, not a change to review.
- **Never push to `standard`, `702` or `cloud`.** These are the installable
  branches. Each is force-pushed by its `generate_*` workflow as exactly one
  commit on top of the current `main`.
- **What this repository does own** is its machinery and its documentation:
  - `.github/workflows/` and `.github/scripts/`
  - the branch README templates in `.github/readme/`
  - `abaplint.jsonc` and `.gitattributes`
  - `README.md`, `CONTRIBUTING.md`, `SECURITY.md` and this file

  Pull requests for these target `main`.

## Layout of `main`

| Path | |
|---|---|
| `input/` | Snapshot of abap2UI5 `src/` (generated, see above). `input/99` keeps only `z2ui5_if_exit` (see "The refresh") |
| `abaplint.jsonc` | Lints `input/` at `v750` against `abapedia/steampunk-2305-api-intersect-702`. `input/00` is in `noIssues` |
| `.github/scripts/refresh_input.sh` | The refresh: copy `src/`, prune `input/99`, abaplint, commit, push to `main` |
| `.github/scripts/build_locals_imp.py` | Builds `z2ui5_cl_abap2ui5_local.clas.locals_imp.abap` from `input/` |
| `.github/readme/{standard,702,cloud}.md` | The README template of each generated branch. `{{VERSION}}` is filled in by the generation |
| `.github/workflows/update_input.yaml` | The refresh from this side (monthly cron and *Run workflow*). It files an issue when a scheduled run fails |
| `.github/workflows/generate_branch.yaml` | The shared, `workflow_call` implementation of one branch rebuild |
| `.github/workflows/generate_{standard,702,cloud}.yaml` | Thin callers of `generate_branch.yaml`. They run on a push to `main`, after a successful `update_input`, and by hand |
| `.github/dependabot.yml` | GitHub Actions updates only, monthly and grouped. `main` has no npm manifest. The third-party actions are pinned to a commit SHA with the version in a trailing comment |
| `.gitattributes` | LF for all text files. It applies to commits made on `main` (the refresh included), never to the generated branches, which are committed from a checkout of their base branch |

## The refresh

- **`refresh_input.sh` is pinned by content in abap2UI5.**
  `trigger_local.yaml` runs the script with a deploy key in scope, so it
  compares the script's SHA-256 against
  `.github/pins/refresh_input.sha256` in abap2UI5 and stops on a mismatch.
  A change to the script needs a matching pull request in abap2UI5 that
  updates that hash (`sha256sum .github/scripts/refresh_input.sh`).
  Otherwise every upstream push fails its `trigger_local` run until the
  hash catches up. Say so in the pull request here.
- **`input/99` is pruned on purpose.** It is abap2UI5's frozen package, and
  the script drops all of it except `package.devc.xml` and `z2ui5_if_exit`,
  which `z2ui5_cl_ui5_user_exit` still references. Dropping that one too
  would be a framework decision. The abaplint run in the script is what
  fails if upstream adds another reference into `99`.
- The commit message names the upstream commit as well as the version,
  because the version constant only moves on a release.

## The generation

`generate_branch.yaml` checks out `main` (tooling and `input/`) and the
branch's base branch: `standard` for `standard` and `702`, `cloud` for
`cloud`. It then does the following, in order:

1. Builds the locals include with `build_locals_imp.py`.
2. Writes the include and the rendered README template over the base
   branch's tree.
3. For `702`, runs `npm run downport` from the base branch's `package.json`
   and strips trailing blanks.
4. Lints with the branch's config: `.github/abaplint/abap_standard.jsonc`
   for `standard`, the default `abaplint.jsonc` for `cloud` and `702`.
5. Pushes the tree as one commit whose parent is `main`'s head, or nothing
   when tree and parent are unchanged.

So only the include and `README.md` come from `main`, and the rest of a
branch's files (`.abapgit.xml`, the handler class, the tables, the ICF node
or HTTP service, `package.json`, the branch's own lint workflows) is
whatever its base branch carries. To change a branch README, edit
`.github/readme/<branch>.md` on `main`.

`build_locals_imp.py` does more than merge. Keep these behaviours, each of
which is documented in the script:

- **abapmerge is pinned** (`ABAPMERGE = 'abapmerge@0.16.8'`, fetched with
  `npx`).
- **`LOCAL_ADDITIONS` re-adds what upstream does not ship:** `zif_app`,
  `zcx_error`, and the entry point `z2ui5_cl_http_handler`. The branch's
  handler class calls `z2ui5_cl_http_handler=>run( )`, and that name is a
  contract between two files this repository owns.
- **The persistence tables are renamed** `z2ui5_t_01` → `z2ui5_t_99` and
  `z2ui5_t_91` → `z2ui5_t_98`. That keeps the local handler independent of a
  regular installation in the same system, and the README's DDL names the
  same tables.
- **The user exit lookup is switched off** (`disable_exit_lookup`). A global
  exit class of a regular installation cannot implement the folded
  handler's local interfaces, and finding one turned every request into a
  500.
- **Definitions are topologically ordered** so the include compiles as one
  unit.
- **The script stops on its assertions.** An upstream change that breaks one
  of these assumptions stops the build. Fix the cause and leave the
  assertion in place.

## Validation

There is no `package.json` on `main`. Before pushing a change to the
machinery, run on `main`:

```bash
npx --yes @abaplint/cli@latest            # what refresh_input.sh runs: input/ against abaplint.jsonc
python3 .github/scripts/build_locals_imp.py input /tmp/locals_imp.abap   # needs Node for npx abapmerge
```

To check what a branch would get, copy the built include into a checkout of
the base branch (`src/z2ui5_cl_abap2ui5_local.clas.locals_imp.abap`), then
run `npm ci` and the branch's lint there:

- `standard`: `npx abaplint .github/abaplint/abap_standard.jsonc`
- `cloud`: `npx abaplint`
- `702`: `npm run downport` and then `npx abaplint`, starting from a
  `standard` checkout

The `generate_*` workflows run on every push to `main` and rebuild all
three branches, so a change merged there reaches the branches right away.

All text files are LF-only, enforced on `main` by `.gitattributes`.
abap2UI5 holds its `src/` to LF with the same attributes, so the refresh
copies LF files and the attributes change nothing in `input/`.
