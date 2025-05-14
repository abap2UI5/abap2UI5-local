[![ABAP_702](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_702.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_702.yaml) 
[![ABAP_STANDARD](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_STANDARD.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/ABAP_STANDARD.yaml)
<br>
[![auto_downport](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/auto_downport.yaml/badge.svg)](https://github.com/abap2UI5/abap2UI5-local/actions/workflows/auto_downport.yaml)

# abap2UI5-local
All abap2UI5 artifacts are combined into a single HTTP handler implementation as local classes. This approach makes your app completely independent of the rest of the system or any other abap2UI5 installation.

#### Installation

1. Create a new HTTP handler in your system.
2. Copy & paste the handler class from this repository.
3. Add your abap2UI5 app as a local class and start it via your new HTTP endpoint.
4. Alternatively, pull this repository using abapGit and start via `/sap/bc/z2ui5_local?app_start=z2ui5_cl_my_local_app`


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
  key mandt         : mandt not null;
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

#### Credits
* Merged files created with [abapmerge](https://github.com/larshp/abapmerge)
* `702` branch created with [abaplint](https://abaplint.org)

#### Compatibility
This repository works in both ABAP for Cloud and Standard ABAP. For old releases use the branch `702`.

#### Issues
For bug reports or feature requests, please open an issue in the [abap2UI5 repository.](https://github.com/abap2UI5/abap2UI5/issues)
