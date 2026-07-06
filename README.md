# abap2UI5-local merge template

This is the template branch of [abap2UI5-local](https://github.com/abap2UI5/abap2UI5-local). It carries the merge tooling only — the installable artifact lives on the generated branches:

| Branch | Content |
|---|---|
| `standard` | merged handler class for Standard ABAP (`if_http_extension`) |
| `702` | downported version for old releases (NW 7.02+) |
| `cloud` | version for ABAP for Cloud (`if_http_service_extension`) |

#### Generation

`.github/scripts/build_locals_imp.py` merges the current [abap2UI5](https://github.com/abap2UI5/abap2UI5) sources into the single locals include `z2ui5_cl_abap2ui5_local.clas.locals_imp.abap`: it runs [abapmerge](https://github.com/larshp/abapmerge), re-adds the local `zif_app`/`zcx_error` additions, renames the persistence tables to `z2ui5_t_99`/`z2ui5_t_98` and orders all definitions so the result compiles as one include.

The `generate_branches` workflow (via *Run workflow* or monthly schedule) rebuilds all three branches from it: it replaces the merged include on `standard` and `cloud` and regenerates `702` by downporting `standard` with [abaplint](https://abaplint.org). Every branch is validated with abaplint before it is pushed.

Run it locally:
```sh
git clone --depth 1 https://github.com/abap2UI5/abap2UI5 /tmp/abap2UI5
python3 .github/scripts/build_locals_imp.py /tmp/abap2UI5/src /tmp/locals_imp.abap
```

#### Credits
All credits go to https://github.com/larshp/abapmerge — this branch started as a fork of the abapmerge sources, which are kept here for reference.

#### Issues
For bug reports or feature requests, please open an issue in the [abap2UI5 repository.](https://github.com/abap2UI5/abap2UI5/issues)
