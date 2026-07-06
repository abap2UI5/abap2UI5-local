[![generate_cloud](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml)
[![ABAP_CLOUD](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_cloud.yaml/badge.svg?branch=cloud)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_cloud.yaml)
[![last generated](https://img.shields.io/github/last-commit/abap2UI5/abap2UI5-local/cloud?label=generated)](https://github.com/abap2UI5/abap2UI5-local/commits/cloud)

# abap2UI5-local — `cloud` branch

Ready-to-install [abap2UI5](https://github.com/abap2UI5/abap2UI5) for **ABAP for Cloud** (`if_http_service_extension`), generated from **abap2UI5 v{{VERSION}}**. Runs on the BTP ABAP Environment, S/4HANA Cloud and any system restricted to the ABAP Cloud language version.

The complete framework is merged into the local classes of a single HTTP handler class — no other abap2UI5 installation is required, and your app stays completely independent of the rest of the system.

#### What's inside

| Object | Type | Purpose |
|---|---|---|
| `Z2UI5_CL_ABAP2UI5_LOCAL` | Class | HTTP handler (`if_http_service_extension`) — the entire framework lives in its local classes |
| `Z2UI5_T_99` | Table | Persistence for draft/session data |
| `Z2UI5_T_98` | Table | Utility persistence |
| `Z2UI5_SERVICE_HTTP` | HTTP service | Service definition + binding wired to the handler class |

#### Installation

**Option A — abapGit (recommended):** pull this branch into your system with [abapGit for ADT](https://eclipse.abapgit.org).

**Option B — copy & paste:** create the handler class manually and copy the sources from `src/`, then create the two tables (DDL in the [main README](https://github.com/abap2UI5/abap2UI5-local#persistence)) and an HTTP service pointing to the class.

#### Getting started

1. In ADT, open the HTTP service `Z2UI5_SERVICE_HTTP` and take the URL from its service binding.
2. Create your app as a class (or local class) implementing `z2ui5_if_app` from the locals of the handler.
3. Open it in the browser:

```
https://<service-binding-url>?app_start=<your_app_class>
```

#### Sibling branches

| Branch | Use when |
|---|---|
| [`standard`](https://github.com/abap2UI5/abap2UI5-local/tree/standard) | Your system runs Standard ABAP (`if_http_extension`, ICF) |
| [`702`](https://github.com/abap2UI5/abap2UI5-local/tree/702) | Your system runs an old release (NW 7.02+) |

#### About this branch

This branch is **generated** — the [generate_cloud](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/generate_cloud.yaml) workflow merges the upstream sources with [abapmerge](https://github.com/larshp/abapmerge), lints them with [abaplint](https://abaplint.org) and force-pushes the result as a single commit on top of `main`. Do not open pull requests against it: changes belong in [`main`](https://github.com/abap2UI5/abap2UI5-local) (tooling) or in [abap2UI5](https://github.com/abap2UI5/abap2UI5) (framework).

#### Issues

For bug reports or feature requests, please open an issue in the [abap2UI5 repository](https://github.com/abap2UI5/abap2UI5/issues).
