# Security policy

## Reporting a vulnerability

**A vulnerability in what this repository ships is a vulnerability in
abap2UI5.** Every ABAP file here is copied from
[abap2UI5/abap2UI5](https://github.com/abap2UI5/abap2UI5) `src/` by the
`update_input` workflow, so a fix belongs there and reaches every branch here
on the next refresh. Report it with the GitHub Security Advisory
["Report a Vulnerability"](https://github.com/abap2UI5/abap2UI5/security/advisories/new)
tab **on abap2UI5**.

Use [this repository's advisory tab](https://github.com/abap2UI5/abap2UI5-local/security/advisories/new)
only when the problem is in the *generation* rather than in the code — a
workflow, `refresh_input.sh`, or a branch whose content does not match the
`main` it was built from. Do not open a public issue for either.

## Supported versions

The three branches as they currently stand: `standard`, `702` and `cloud`.
There are no releases to patch, and no older generation is maintained — a
branch is rebuilt from scratch on each refresh, so a fix upstream is a
regenerated branch rather than a patch.

If you pulled a branch into a system with abapGit, pull it again to pick a fix
up; the README's badges show when each branch was last generated.

## What this repository is, from a security point of view

- **It ships an HTTP handler you install in your own system.** `standard` and
  `702` bring the ICF node `z2ui5_local`; `cloud` brings the HTTP service
  `Z2UI5_SERVICE_HTTP`. Both start an app named in the request
  (`?app_start=<class>`), so what the endpoint exposes is decided by **your**
  system's authorisations and by which classes exist in it — the same
  consideration as any other abap2UI5 installation, and the reason the service
  is delivered inactive and has to be activated in `SICF` deliberately.
- **Its own tables are separate on purpose.** `z2ui5_t_99` and `z2ui5_t_98`
  exist so that installing this alongside a normal abap2UI5 cannot interfere
  with that installation's state.
- **Nothing here is compiled or fetched at runtime.** The branches are ABAP
  source, generated in CI from a pinned copy of abap2UI5 and linted with
  abaplint before they are pushed.
