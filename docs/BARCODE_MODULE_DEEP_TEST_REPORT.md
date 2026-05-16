# Barcode Module Deep Test Report

Date: 2026-05-16

Scope:
- Frontend barcode pages in `FactoryFlow/src/modules/barcode`
- Backend barcode APIs, serializers, services, models, and migrations in `factory_app/barcode`
- Main user flow requested: create generic pallet with warehouse only, select empty pallet, select SAP HANA item/release, enter item count per pallet, print two pallet QR labels first, then print linked box labels.

## Tested Flow Summary

Expected current flow:

1. Create a pallet from the Pallet page by selecting only a warehouse.
2. Pallet is generic and has no item, batch, or quantity connection.
3. Open Pallet QR Print.
4. Select only an empty pallet.
5. Select item/release data fetched from SAP HANA.
6. Enter the number of items/boxes per pallet.
7. Generate box labels from the SAP item data.
8. Attach those boxes to the selected pallet.
9. Print two pallet QR labels first.
10. Print all box QR labels after that, with each box linked to the pallet.

This flow is partly working, but older barcode module paths still exist and can conflict with it.

## Verification Results

Frontend build:

```text
npm run build
Result: PASS
```

Notes:
- Build completed successfully.
- Rollup reported existing circular chunk warnings around shared API client exports.
- Bundle size warnings remain for large chunks.

Frontend lint, full app:

```text
npm run lint
Result: FAIL
Problems: 827
```

Most failures are existing app-wide lint issues outside the barcode module, especially tests, shared hooks, shared UI exports, and React hook lint rules.

Barcode-focused lint:

```text
npx eslint src/modules/barcode src/config/constants/api.constants.ts
Result: FAIL
Problems: 3
```

Barcode lint issues:
- `src/modules/barcode/components/labelPrint.ts:57`: `_mode` is assigned but never used.
- `src/modules/barcode/pages/LabelGeneratePage.tsx:1`: import order warning.
- `src/modules/barcode/pages/PalletDetailPage.tsx:1`: import order warning.

Backend Django checks:

```text
$env:DEBUG='true'; .\.venv\Scripts\python.exe manage.py check
Result: PASS
```

Backend barcode tests:

```text
$env:DEBUG='true'; .\.venv\Scripts\python.exe manage.py test barcode --keepdb --verbosity 2
Result: PASS
Tests: 10
Time: 12.305s
```

Note:
- Running `manage.py test barcode` without `--keepdb` failed because the existing `test_factory` database prompted for deletion and the command could not answer interactively.

API smoke response times:

```text
POST create empty pallet W1: 201, 285.1 ms
POST create empty pallet W2: 201, 145.6 ms
POST generate 3 boxes: 201, 150.7 ms
POST add boxes to pallet: 200, 136.3 ms
POST bulk print 2 pallet + 3 boxes: 200, 131.7 ms
POST split 1 box to empty pallet: 200, 217.9 ms
POST scan box barcode: 200, 45.2 ms
GET pallet list active: 200, 34.3 ms
```

The successful smoke test used a unique production line and rolled back the transaction after testing.

## Not Correct / Needs Fix

### 1. Pallet ID generation can create duplicate pallet IDs

Severity: High

Evidence:
- `barcode/services/barcode_service.py` generates IDs as `PLT-{date}-{line}-{sequence}`.
- The sequence is scoped by company/date/line through `BarcodeSequence`.
- `Pallet.pallet_id` is globally unique.
- An API smoke test creating a generic empty pallet with only warehouse hit:

```text
IntegrityError: duplicate key value violates unique constraint "barcode_pallet_pallet_id_key"
DETAIL: Key (pallet_id)=(PLT-20260516-XX-001) already exists.
```

Impact:
- Creating pallets can fail with a server error.
- This is especially likely after clearing `BarcodeSequence`, creating generic pallets without production line, or creating pallets in multiple companies that share the same date and line key.

Recommendation:
- Make generated pallet IDs globally unique, or make the database uniqueness match the real scope.
- Add retry/check logic before saving.
- Catch `IntegrityError` in `PalletCreateAPI` and return a clear 400 response.

### 2. Box barcode generation has the same uniqueness risk

Severity: High

Evidence:
- Box barcodes use the same company/date/line sequence pattern.
- `Box.box_barcode` is globally unique.
- The backend handles `IntegrityError` in `BoxGenerateAPI`, but the root sequence/design issue remains.

Impact:
- Box generation can fail when another company or reset sequence uses the same date and line.

Recommendation:
- Use a globally unique barcode namespace or include company/plant/warehouse-safe prefix in the barcode.
- Keep the existing `IntegrityError` handling, but also prevent the duplicate before it happens.

### 3. Pallet creation API still documents and supports the old "create pallet with boxes" behavior

Severity: High

Evidence:
- `barcode/views.py:136` has `PalletCreateAPI` docstring: "Create a pallet by linking existing boxes."
- `barcode/services/barcode_service.py:329` still supports `box_ids` during pallet creation.
- `src/modules/barcode/pages/BoxDetailPage.tsx:73` still has `handleCreateNewPallet`.
- `src/modules/barcode/pages/BoxDetailPage.tsx:76` creates a pallet with `box_ids: [box.id]`.

Impact:
- Users can still create a pallet already connected to an item/box from the Box Detail page.
- This conflicts with the latest requirement: pallet creation should only create a pallet and should not connect it with item, batch, or box data.

Recommendation:
- Remove or disable "Create New Pallet with This Box" in Box Detail.
- Change backend pallet creation endpoint to reject `box_ids` if generic-only pallet creation is now the required contract.
- Move box linking into only the intended print/attach workflow.

### 4. Pallet Detail page still has the old print workflow

Severity: High

Evidence:
- `src/modules/barcode/pages/PalletDetailPage.tsx:76` uses `usePrintPalletWorkflow`.
- `src/modules/barcode/pages/PalletDetailPage.tsx:293` shows "Print Pallet + Boxes".
- `barcode/views.py:419` calls `svc.ensure_pallet_boxes(...)`.
- `barcode/services/barcode_service.py:480` can auto-create missing boxes from pallet metadata.

Impact:
- Users can print from a second path that bypasses the new SAP HANA item selection workflow.
- Generic pallets have blank item and batch fields, so this path can create or print empty-item labels.

Recommendation:
- Remove this print button or redirect it to the new Pallet QR Print page.
- Keep only one official print path for pallet plus linked boxes.

### 5. Pallet Detail "Add Boxes" dialog filters by blank pallet item and batch

Severity: Medium

Evidence:
- `src/modules/barcode/pages/PalletDetailPage.tsx:95` filters boxes by `pallet.item_code`.
- `src/modules/barcode/pages/PalletDetailPage.tsx:96` filters boxes by `pallet.batch_number`.
- Generic empty pallets intentionally have blank `item_code` and `batch_number`.
- `src/modules/barcode/pages/PalletDetailPage.tsx:436` displays "Showing unpalletized active boxes for {pallet.item_code} - {pallet.batch_number}".

Impact:
- The dialog will be confusing for generic pallets.
- It may show no boxes or appear broken because the pallet does not have item metadata by design.

Recommendation:
- Remove this dialog for generic pallets, or replace it with the SAP item/release selection flow.

### 6. Pallet list still displays item/batch columns for generic pallets

Severity: Medium

Evidence:
- `src/modules/barcode/pages/PalletListPage.tsx:165` displays `p.item_code`.
- `src/modules/barcode/pages/PalletListPage.tsx:170` displays `p.batch_number`.
- Generic pallets now store these fields as blank.

Impact:
- The list has empty columns and can make users think data is missing.

Recommendation:
- For the new generic pallet model, show pallet ID, warehouse, empty/full state, box count/capacity, and created date.
- Move item information to the linked box/label history view.

### 7. Empty pallets display capacity as `0/0`

Severity: Medium

Evidence:
- `src/modules/barcode/pages/PalletListPage.tsx:172` renders `{p.box_count}/{p.max_box_count || p.box_count}`.
- New empty pallets are created with `box_count = 0` and `max_box_count = 0`.

Impact:
- Users see `0/0`, which looks like a broken capacity value.

Recommendation:
- Display `0 / Not set` or `Empty` until the user enters the item/box count at print time.

### 8. New print flow is not transactional from the user's point of view

Severity: Medium

Evidence:
- `src/modules/barcode/pages/LabelGeneratePage.tsx:225` generates boxes.
- `src/modules/barcode/pages/LabelGeneratePage.tsx:243` attaches boxes to the pallet.
- `src/modules/barcode/pages/LabelGeneratePage.tsx:248` creates print data/logs.
- These are three separate frontend API steps.

Impact:
- If box generation succeeds but attaching fails, generated boxes can remain unpalletized.
- If attaching succeeds but printing/logging fails, the pallet state is changed but labels are not printed.
- If browser print is cancelled, backend print logs may already exist.

Recommendation:
- Add a single backend endpoint for "generate, attach, prepare labels" inside one transaction.
- Log a final "printed" state only after print confirmation if the printer integration supports that.
- Add recovery UI showing unprinted or partially printed labels for the pallet.

### 9. Print logs are created before physical print success is known

Severity: Medium

Evidence:
- Bulk print API returns label data and logs print records before browser print completes.
- Browser print can be cancelled or printer can fail after the API says success.

Impact:
- Audit log can claim a label was printed when it was only prepared.

Recommendation:
- Rename this state to "prepared" or add a later confirmation step.
- If direct printer integration is added, log only after printer acceptance.

### 10. Pallet QR labels do not contain SAP item name in the current generic-pallet model

Severity: Product decision needed

Evidence:
- `barcode/services/label_service.py:59` builds pallet label data from pallet fields.
- Generic pallets store blank `item_code`, `item_name`, and `batch_number`.
- Box labels do contain the SAP item data after generation.

Impact:
- This matches the latest clarification that pallets are not connected with item data.
- It conflicts with the earlier objective that pallet and box labels should both have human-readable item code and name.

Recommendation:
- Confirm the final business rule.
- If pallet labels must show item name only for the printed batch, the print request should pass SAP item label context without permanently connecting the item to the pallet.

### 11. Frontend schema is stale for pallet creation

Severity: Low

Evidence:
- `src/modules/barcode/schemas/barcode.schemas.ts:17` still requires `box_ids` with at least one box.

Impact:
- If this schema is reused by any form later, it will block warehouse-only pallet creation.

Recommendation:
- Update or remove the stale schema.

### 12. Empty pallet selectors are client-side filtered from only the first 500 pallets

Severity: Low

Evidence:
- Barcode list APIs return `qs[:500]`.
- `LabelGeneratePage` and `PalletSplitPage` filter empty pallets client-side.

Impact:
- If there are more than 500 active pallets, valid empty pallets may not appear.

Recommendation:
- Add server-side filters such as `empty=true` and search by pallet ID.
- Use paginated selectors for large data.

### 13. SAP warehouse selection has weak failure UX

Severity: Low

Evidence:
- Pallet creation now depends on SAP HANA warehouse fetching.
- If the SAP warehouse call fails or returns no data, the create form has no clear recovery path beyond an empty dropdown.

Impact:
- Users may not know if SAP is down, no warehouse exists, or the page failed.

Recommendation:
- Show a clear SAP warehouse load error.
- Add refresh and disabled submit messaging.

### 14. Barcode module has small local lint issues

Severity: Low

Evidence:
- Barcode-focused ESLint found 3 issues.

Impact:
- CI can fail if barcode lint is enforced.

Recommendation:
- Remove the unused `_mode` parameter or use it.
- Run import sort on `LabelGeneratePage.tsx` and `PalletDetailPage.tsx`.

## UI Flow Observations

Working:
- Empty pallets are visually highlighted in the pallet list.
- Pallet QR Print only shows empty pallets.
- Pallet creation now asks for warehouse only.
- Split Pallet no longer automatically creates a target pallet; it requires an existing empty target pallet.
- The new print flow sends two pallet labels before box labels.

Needs correction:
- Box Detail still lets users create a pallet with the current box.
- Pallet Detail still lets users print pallet and boxes through the old workflow.
- Pallet Detail still treats pallet item and batch as meaningful even though pallets are now generic.
- Pallet list still has old item/batch columns.
- Some labels/text contain mojibake dash characters, for example `â€”`, which should be a normal hyphen or proper UTF-8 dash.

## API Behavior Observations

Working:
- Backend barcode tests pass.
- API response times in smoke testing were acceptable for the small dataset.
- Split Pallet now requires a target pallet and rejects non-empty targets.
- Box scanning works for linked boxes.

Needs correction:
- Pallet create duplicate ID returns a server error instead of a clean validation response.
- Pallet create endpoint still accepts boxes.
- Old print workflow can auto-create boxes from pallet fields, which is unsafe for generic pallets.
- Print logging does not distinguish "label data prepared" from "printer successfully printed".

## Recommended Next Fix Order

1. Fix global uniqueness and `IntegrityError` handling for pallet and box barcode generation.
2. Remove old pallet-with-box creation from Box Detail and backend pallet creation if no longer allowed.
3. Remove or redirect Pallet Detail old "Print Pallet + Boxes" workflow.
4. Replace Pallet Detail item/batch-based Add Boxes with the new SAP item label flow or hide it for generic pallets.
5. Update Pallet List columns for the generic pallet model.
6. Convert the three-step generate/attach/print flow into one backend transaction.
7. Fix barcode lint issues.
8. Add server-side empty pallet filtering and search.
9. Improve SAP warehouse error UI.

## Suggested Regression Tests To Add

Backend:
- Create warehouse-only pallet with no `box_ids`.
- Reject pallet creation with `box_ids` if generic-only creation is the final rule.
- Creating pallets in two companies on the same date does not duplicate `pallet_id`.
- Creating boxes in two companies on the same date/line does not duplicate `box_barcode`.
- Split pallet requires target pallet and rejects non-empty target pallet.
- Print workflow returns exactly two pallet labels followed by N box labels.
- Generic pallet old print workflow is disabled or rejected.

Frontend:
- Pallet creation form shows only warehouse and creates an empty pallet.
- Pallet QR Print selector only lists empty pallets.
- Print flow calls generate boxes, attach boxes, then bulk print in pallet-first order.
- Box Detail does not offer "Create New Pallet with This Box".
- Pallet Detail does not offer the old print path for generic pallets.
- Pallet List renders empty pallets without blank item/batch confusion.

