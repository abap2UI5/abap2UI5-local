# Contributing

**This repository does not take source changes. Contribute to
[abap2UI5/abap2UI5](https://github.com/abap2UI5/abap2UI5) instead.**

`abap2UI5-local` is a delivery repository. Nothing here is written by hand:

| Content | Written by | A hand-made change here … |
|---|---|---|
| `input/` on `main` | `update_input`, which copies `src/` out of a fresh clone of abap2UI5 and lints it | is overwritten on the next refresh |
| the `standard`, `702` and `cloud` branches | `generate_standard` / `generate_702` / `generate_cloud`, each rebuilding its branch from the current `main` | is discarded on the next generation |

The refresh runs on every push to abap2UI5's `main` (its `trigger_local`
workflow pushes here), with a monthly cron as a safety net. So a change made
here is reviewed, merged, and works — until an unrelated push upstream wipes
it, with nothing in the history to say why the fix vanished.

## Where a change belongs

| You want to … | Go to |
|---|---|
| change the framework — the handler, the classes, anything under `input/` | [abap2UI5/abap2UI5](https://github.com/abap2UI5/abap2UI5), directory `src/`; the refresh delivers it here |
| change how a branch is generated or linted | here, in `.github/` — see below |
| report a bug in what a branch installs | [abap2UI5 issues](https://github.com/abap2UI5/abap2UI5/issues), because that is where the code is |
| report a bug in the generation itself | [this repository's issues](https://github.com/abap2UI5/abap2UI5-local/issues) |

## What this repository does own

Its own machinery and its own documentation: the workflows and scripts under
`.github/`, `abaplint.jsonc`, `README.md`, this file, and `SECURITY.md`. Those
are the legitimate reason to open a pull request here, and they must target
`main` — every other branch is generated and rebuilt from scratch.

All text files are LF-only. English for code, comments, commit messages, pull
requests and issues.
