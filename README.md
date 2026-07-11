[![update_input](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/update_input.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/update_input.yaml)
[![generate_standard](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_standard.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_standard.yaml)
[![generate_702](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_702.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_702.yaml)
[![generate_cloud](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml)

# abap2UI5-local

All abap2UI5 artifacts are combined into a single HTTP handler implementation as local classes. This approach makes your app completely independent of the rest of the system or any other abap2UI5 installation.

#### Branches

| Branch | Content | Last generated |
|---|---|---|
| [`standard`](https://github.com/abap2UI5/abap2UI5-local/tree/standard) | Standard ABAP (`if_http_extension`) | [![last generated](https://img.shields.io/github/last-commit/abap2UI5/abap2UI5-local/standard?label=generated)](https://github.com/abap2UI5/abap2UI5-local/commits/standard) |
| [`702`](https://github.com/abap2UI5/abap2UI5-local/tree/702) | Downport for old releases (NW 7.02+) | [![last generated](https://img.shields.io/github/last-commit/abap2UI5/abap2UI5-local/702?label=generated)](https://github.com/abap2UI5/abap2UI5-local/commits/702) |
| [`cloud`](https://github.com/abap2UI5/abap2UI5-local/tree/cloud) | ABAP for Cloud (`if_http_service_extension`) | [![last generated](https://img.shields.io/github/last-commit/abap2UI5/abap2UI5-local/cloud?label=generated)](https://github.com/abap2UI5/abap2UI5-local/commits/cloud) |

#### Installation

1. Create a new HTTP handler in your system.
2. Copy & paste the handler class from this repository.
3. Add your abap2UI5 app as a local class and start it via your new HTTP endpoint.
4. Alternatively, pull this repository using abapGit and start via `/sap/bc/z2ui5_local?app_start=z2ui5_cl_my_local_app`

#### Start via HTTP

The `standard` and `702` branches ship the ICF node **`z2ui5_local`** (service path `/sap/bc/z2ui5_local`, handler class `Z2UI5_CL_ABAP2UI5_LOCAL`). After pulling the repository, activate the node in transaction `SICF` (locate `/sap/bc/z2ui5_local`, right-click → *Activate Service*) and open your app in the browser:

```
https://<host>:<port>/sap/bc/z2ui5_local?sap-client=<client>&app_start=<your_app_class>
```

For example:

```
https://myhost:44300/sap/bc/z2ui5_local?app_start=z2ui5_cl_my_local_app
```

The `cloud` branch uses the HTTP service **`Z2UI5_SERVICE_HTTP`** instead (same handler class) — take the URL from its service binding in ADT and append `?app_start=<your_app_class>`.

#### Approach

<img width="500" alt="Screenshot 2025-02-13 at 13 24 18" src="https://github.com/user-attachments/assets/5fcc56a8-8e2c-41b2-84b3-e50242ff648c" />

#### Persistence

To avoid any side effects with other abap2UI5 installations, this version uses the separated tables for persistence. You can either pull this repository or manually create the following two table in your system:

```cds
@EndUserText.label : 'abap2UI5-local'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table z2ui5_t_99 {
  key mandt         : abap.char(3) not null;
  key id            : abap.char(32) not null;
  id_prev           : abap.char(32);
  id_prev_app       : abap.char(32);
  id_prev_app_stack : abap.char(32);
  timestampl        : timestampl;
  data              : abap.string(0);
}
```

```cds
@EndUserText.label : 'abap2ui5 local utility'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table z2ui5_t_98 {
  key mandt : abap.char(3) not null;
  key id    : abap.char(32) not null;
  uname     : abap.char(32);
  handle    : abap.char(32);
  handle2   : abap.char(32);
  handle3   : abap.char(32);
  handle4   : abap.char(32);
  handle5   : abap.char(32);
  data      : abap.string(0);
  data2     : abap.string(0);
  data3     : abap.string(0);
}
```

#### Generation

This `main` branch is the template branch — it carries the merge tooling and a snapshot of the upstream sources, the installable artifact lives on the generated branches:

* `input/` holds a copy of the current [abap2UI5](https://github.com/abap2UI5/abap2UI5) sources. Upstream's [trigger_local](https://github.com/abap2UI5/abap2UI5/actions/workflows/trigger_local.yaml) workflow refreshes it on every push to abap2UI5 `main`; the [update_input](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/update_input.yaml) workflow (monthly schedule as safety net, or *Run workflow*) does the same from this side. Both overwrite it with the latest upstream version, validates it with [abaplint](https://abaplint.org) (`abaplint.jsonc` points at `/input`) and pushes the refresh to `main`.
* Each artifact branch has its own workflow ([generate_standard](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_standard.yaml), [generate_702](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_702.yaml), [generate_cloud](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml)) which runs after every `input` refresh (and on every push to `main`). It merges the sources from `input/` into the single locals include `z2ui5_cl_abap2ui5_local.clas.locals_imp.abap` via `.github/scripts/build_locals_imp.py` (runs [abapmerge](https://github.com/larshp/abapmerge), re-adds the local `zif_app`/`zcx_error` additions, renames the persistence tables to `z2ui5_t_99`/`z2ui5_t_98` and orders all definitions so the result compiles as one include), renders the branch README from its template in `.github/readme/` (replacing the `{{VERSION}}` placeholder with the current abap2UI5 version), validates everything with abaplint and force-pushes the branch content as exactly **one commit on top of the current `main`** — so every branch always shows *1 commit ahead* of `main` and never behind. To change a branch README, edit its template on `main` — edits made directly on a generated branch are overwritten on the next run.

Run it locally:
```sh
python3 .github/scripts/build_locals_imp.py input /tmp/locals_imp.abap
```

#### Credits

* Merged files created with [abapmerge](https://github.com/larshp/abapmerge) (fetched from npm by `build_locals_imp.py`)
* `702` branch created with [abaplint](https://abaplint.org)

#### Compatibility

This repository works in both ABAP for Cloud and Standard ABAP. For old releases use the branch `702`.

#### Issues

For bug reports or feature requests, please open an issue in the [abap2UI5 repository.](https://github.com/abap2UI5/abap2UI5/issues)
