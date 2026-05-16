# Barcode Module Deep Test Report V2

Date: 2026-05-16

Scope:
- Retest after fixing the main issues from `BARCODE_MODULE_DEEP_TEST_REPORT.md`.
- Frontend barcode module in `FactoryFlow/src/modules/barcode`.
- Backend barcode APIs and services in `factory_app/barcode`.
- Focus flow: create empty pallet, select empty pallet for Pallet QR Print, select SAP item data, enter item count, generate boxes, attach boxes to pallet, print 2 pallet labels first, then print linked box labels.

## V2 Result Summary

Status: Improved and mostly ready for the requested pallet-first workflow.

Confirmed fixed:
- Pallet creation no longer accepts boxes.
- Pallet creation is warehouse/generic first.
- Duplicate pallet ID risk is reduced by checking the global barcode namespace before reserving sequence numbers.
- Old pallet print workflow is disabled.
- Frontend removed the old "Print Pallet + Boxes" action from Pallet Detail.
- Frontend removed "Create New Pallet with This Box" from Box Detail.
- Pallet list/detail no longer treats pallet item/batch as the main pallet identity.
- Barcode focused lint is clean.

Still needs attention:
- Box Detail still allows manually adding a box to an existing pallet, which can bypass the Pallet QR Print workflow.
- Production integration still calls `create_pallet` with `box_ids`, so production-run pallet creation will now fail.
- Pallet QR Print still uses multiple API calls, so partial failure can leave generated boxes or linked boxes without printed labels.
- Print logs are still created before physical print success is known.
- Large pallet lists still rely on first-page/client-side filtering.
- Some old mojibake text remains in Box Detail UI.

## Verification Commands

Frontend barcode lint:

```text
npx eslint src/modules/barcode src/config/constants/api.constants.ts
Result: PASS
```

Frontend build:

```text
npm run build
Result: PASS
```

Notes:
- Build completed.
- Existing Rollup warnings remain for circular chunk imports through shared API/auth re-exports.
- Existing chunk size warnings remain.

Backend Django check:

```text
$env:DEBUG='true'; .\.venv\Scripts\python.exe manage.py check
Result: PASS
```

Backend barcode tests:

```text
$env:DEBUG='true'; .\.venv\Scripts\python.exe manage.py test barcode --keepdb --verbosity 1
Result: PASS
Tests: 12
Time: 17.327s
```

API smoke test:
- Used DRF `APIClient`.
- Used authenticated user plus `Company-Code` header.
- Wrapped test data in a transaction and rolled it back.
- Confirmed no smoke companies/users remained after rollback.

## API Smoke Test Results

```text
POST create pallet with box_ids rejected: status=400, ms=129.9, shape=dict[box_ids]
POST create empty pallet company A: status=201, ms=175.5, shape=dict[id,pallet_id,barcode_data,item_code,item_name,batch_number,box_count,max_box_count]
POST create empty pallet company B same prefix: status=201, ms=153.5, shape=dict[id,pallet_id,barcode_data,item_code,item_name,batch_number,box_count,max_box_count]
POST create target empty pallet: status=201, ms=147.1, shape=dict[id,pallet_id,barcode_data,item_code,item_name,batch_number,box_count,max_box_count]
POST generate 3 SAP item boxes: status=201, ms=151.0, shape=list[3]
POST add boxes to selected pallet: status=200, ms=139.0, shape=dict[id,pallet_id,barcode_data,item_code,item_name,batch_number,box_count,max_box_count]
POST bulk print 2 pallet + 3 boxes: status=200, ms=130.9, shape=list[5]
POST old pallet workflow disabled: status=400, ms=9.3, shape=dict[error]
POST split 1 box to existing empty pallet: status=200, ms=219.7, shape=dict[id,pallet_id,barcode_data,item_code,item_name,batch_number,box_count,max_box_count]
POST scan linked box barcode: status=200, ms=42.7, shape=dict[scan_id,result,entity_type,entity_id,entity_data,barcode_raw,barcode_parsed]
GET pallet list active: status=200, ms=39.0, shape=list[2]
```

API smoke assertions:
- Rejected old pallet creation with `box_ids`.
- Created generic empty pallet.
- Created same-prefix pallet in a second company without duplicate ID failure.
- Generated three item boxes.
- Attached generated boxes to selected pallet.
- Bulk print returned exactly 5 labels: 2 pallet labels plus 3 box labels.
- Old print workflow returned a controlled 400 with a clear message.
- Split moved one box into an existing empty target pallet.
- Scan found a linked box successfully.

Observed generated IDs:

```text
company_a_pallet = PLT-20260516-XX-002
company_b_pallet = PLT-20260516-XX-003
bulk_label_count = 5
split_target_box_count = 1
scan_result = SUCCESS
```

Note:
- The sequence started at `002` because existing data already had matching `PLT-20260516-XX-*` IDs. This is expected after the global namespace fix.

## Flow Review

### Pallet Creation

Working:
- Pallet List page creates a pallet with warehouse only.
- Warehouses are fetched from SAP HANA through the WMS warehouse query.
- API rejects old `box_ids` pallet creation.
- Empty pallets are highlighted and show capacity as `Not set` instead of `0/0`.

Remaining concern:
- The backend serializer still has item/batch/qty fields on `PalletCreateSerializer`, although service creation ignores them and creates a generic pallet. This is low risk but the API contract could be cleaned further.

### Pallet QR Print

Working:
- Empty pallet selection exists in Pallet QR Print.
- SAP item data is selected before box generation.
- The flow generates boxes, attaches them to the pallet, then requests bulk print labels in the correct order:
  1. Pallet label
  2. Pallet label
  3. Box labels

Remaining concern:
- This flow is still three frontend API steps:
  1. Generate boxes.
  2. Add boxes to pallet.
  3. Bulk print.
- If step 2 or 3 fails, the database can be left in a partially completed state.

Recommendation:
- Add one backend endpoint for `generate -> attach -> prepare labels` in a single transaction.

### Pallet Detail

Working:
- Old "Print Pallet + Boxes" button is gone.
- Generic pallet fields are shown as pallet/warehouse/status/capacity, not item/batch identity.
- Empty pallets link the user to Pallet QR Print.
- Linked box table now shows item and batch from boxes.

Remaining concern:
- Pallet Detail does not itself select the current pallet when navigating to Pallet QR Print. User may need to select it again.

Recommendation:
- Pass `palletId` through query string, for example `/barcode/generate?palletId=...`, and auto-select it when it is still empty.

### Box Detail

Working:
- "Create New Pallet with This Box" was removed.
- The replacement action opens the Pallets page.

Not correct:
- Box Detail still allows "Add to Existing Pallet" and calls `addBoxesToPallet` with the current box.
- This can bypass the intended flow where item labels are attached to a pallet through Pallet QR Print.
- The Box Detail search item text still uses pallet item/batch fields, which are blank for generic pallets.
- Some mojibake text remains, such as `â€”` and `Â·`.

Recommendation:
- Disable direct box-to-pallet linking from Box Detail for normal users, or only allow it behind an admin/correction permission.
- Update display text for generic pallets.
- Replace mojibake characters with ASCII hyphen/dot or valid UTF-8.

### Split Pallet

Working:
- Split now requires an existing empty target pallet.
- API smoke confirmed split moves a box into the selected empty pallet.
- Split no longer auto-creates a target pallet.

Remaining concern:
- Target empty pallet selection is still client-side filtered from the loaded pallet list. Large datasets may hide valid empty pallets.

Recommendation:
- Add server-side `empty=true` filter and a paginated/searchable selector.

## Remaining Issues

### 1. Production-run pallet creation is now incompatible

Severity: High if production-run pallet creation is used.

Evidence:
- `barcode/services/production_integration_service.py` calls `svc.create_pallet({... 'box_ids': box_ids ...})`.
- `PalletCreateSerializer` and `BarcodeService.create_pallet` now reject non-empty `box_ids`.

Impact:
- `ProductionRunPalletAPI` can fail when trying to create a pallet from generated production-run boxes.

Recommendation:
- Update production integration to create an empty pallet first, then call `add_boxes_to_pallet`.
- Or retire that production endpoint if Pallet QR Print is the only approved workflow.

### 2. Direct Box Detail linking can bypass Pallet QR Print

Severity: Medium.

Evidence:
- `BoxDetailPage` still calls `addBoxesToPallet` with `box_ids: [box.id]`.

Impact:
- Users can attach item boxes to a pallet outside the official SAP item print flow.

Recommendation:
- Remove this action or restrict it to correction/admin use.

### 3. Pallet QR Print remains non-transactional

Severity: Medium.

Evidence:
- `LabelGeneratePage` performs generate, attach, and print as separate API mutations.

Impact:
- Generated boxes may remain if attach fails.
- Boxes may be linked even if print preparation or browser print fails.

Recommendation:
- Add a single backend API endpoint for this workflow.

### 4. Print log still means "prepared", not confirmed printed

Severity: Medium.

Impact:
- Browser print cancellation or printer failure can still leave print logs showing success.

Recommendation:
- Rename current log state to prepared, or add printer-confirmed logging.

### 5. Large pallet lists can hide empty pallets

Severity: Low to Medium.

Impact:
- Empty pallet selectors can miss valid pallets when more than 500 active pallets exist.

Recommendation:
- Add server-side filtering and pagination for empty pallets.

### 6. Remaining mojibake in Box Detail

Severity: Low.

Impact:
- UI looks unpolished.

Recommendation:
- Replace `â€”` and `Â·` in Box Detail with ASCII text.

## V2 Conclusion

The main pallet-first print system is now working in API smoke testing:
- Empty pallet creation works.
- Old box-linked pallet creation is rejected.
- Boxes can be generated from SAP item data and linked to the selected pallet.
- Bulk print returns two pallet labels first and then all box labels.
- Split pallet uses an existing empty pallet.
- Scanning linked boxes works.

Before calling the module fully complete, fix the production integration compatibility and decide whether Box Detail direct linking should remain available.

