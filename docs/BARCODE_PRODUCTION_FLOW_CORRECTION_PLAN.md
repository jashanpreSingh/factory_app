# Barcode Production Flow Correction Plan

This document lists the mistakes found in the barcode flow, why they matter, and what must be corrected before production deployment.

## Production Goal

The barcode module must support the real factory lifecycle:

1. Create an empty physical pallet QR.
2. Generate or scan box labels.
3. Link boxes to a pallet.
4. Move, split, clear, dismantle, reprint, and scan records with full traceability.
5. Reuse a cleared physical pallet for a new item or batch.

The system must never allow item/batch mixing by accident, silent quantity mismatch, or confusing error messages.

## Current High-Risk Flow Mistakes

## Implementation Status - 2026-05-18

The current code now corrects the high-risk pallet receive flows:

- Add Box To Pallet, Split Pallet target, and Box Transfer target all use the same backend validation rule before boxes are attached to a pallet.
- `ACTIVE` and empty `CLEARED` pallets can receive boxes.
- Empty `CLEARED` pallets are reactivated to `ACTIVE` when boxes are received.
- Boxes being received by one pallet must share the same item code, batch, and UOM.
- Pallets with existing item context reject mismatched boxes.
- Pallet capacity is checked before linking, splitting, or transferring boxes into the target pallet.
- Split target pallets now receive item code, item name, batch, UOM, manufacturing date, expiry date, production line, and production run context from the moved boxes.
- Full pallet dismantle now clears the pallet's current item context when the pallet becomes `CLEARED`.
- Frontend split target search now hides empty active pallets with mismatched stale item context and allows empty cleared pallets.

Verification completed:

- Backend barcode tests: `17` tests passing.
- Frontend production build: passing, with existing Rollup chunk/circular dependency warnings outside this barcode flow.

### 1. Cleared Pallets Were Treated As Dead Pallets

Mistake:

- After clearing a pallet, status became `CLEARED`.
- Add-box logic allowed only `ACTIVE` pallets.
- Frontend pallet search also looked mostly for `ACTIVE` pallets.
- Result: a physically reusable pallet QR could not be reused.

Why this is wrong:

- In factory operations, clearing a pallet means the boxes were removed and the pallet is free.
- A cleared physical pallet should be reusable for another item or batch.
- Operators should not need to create a new pallet QR every time a physical pallet is emptied.

Correction:

- A cleared pallet must be considered reusable when it has no active or partial boxes.
- When boxes are added to a cleared pallet, the pallet status must become `ACTIVE`.
- The new linked boxes must set the new item context.
- The same pallet ID should be retained for physical traceability.

Implemented rule:

- `CLEARED + empty + add boxes` is allowed.
- `CLEARED + not empty + add boxes` is blocked.

### 2. Clear Pallet Kept Old Item Context

Mistake:

- Clearing a pallet removed boxes and set quantity to zero, but old item code, item name, batch, UOM, and capacity could remain.

Why this is wrong:

- A cleared pallet with stale item context looks like it still belongs to the old SKU.
- Reusing it for a new SKU would cause either a false mismatch or operator confusion.
- Production users may see the old batch on an empty pallet and assume it is still reserved.

Correction:

- Clear pallet must reset item code, item name, batch, UOM, total quantity, max box count, and production run.
- Keep pallet ID, warehouse, created metadata, and movement history.
- Rebuild pallet barcode payload after clearing.

Production rule:

- A cleared pallet means: same physical pallet, no current item assignment.

### 3. Add Box To Pallet Allowed Weak Context Earlier

Mistake:

- The add-box workflow did not fully enforce that boxes must match the target pallet item, batch, and UOM.
- Empty pallet context was not always set clearly from the first linked box.

Why this is wrong:

- Mixing two SKUs or batches on one pallet breaks traceability.
- Inventory reports and SAP reconciliation become unreliable.
- Quality hold or recall tracing becomes unsafe.

Correction:

- If pallet has item context, every box must match item code, batch, and UOM.
- If pallet is empty with no context, all boxes in the request must match each other.
- Empty pallet takes item context from the first linked box.
- Cleared pallet is treated as empty/no-context when reused.

Production rule:

- One active pallet can hold only one item code, one batch, and one UOM.

### 4. Pallet Capacity Was Not Enforced In Link Flow

Mistake:

- A pallet with `max_box_count` could receive more boxes than allowed.

Why this is wrong:

- Operators may over-link labels beyond physical or planned packing capacity.
- Printed labels and pallet quantity can diverge from the planned pallet size.

Correction:

- Add-box operation must reject links that exceed `max_box_count`.
- Cleared pallet resets `max_box_count` to zero so a future production flow can define a new capacity.

Production rule:

- Capacity `0` means no capacity limit is set.
- Positive capacity means linked boxes cannot exceed that number.

### 5. Frontend Search Hid Valid Reusable Pallets

Mistake:

- Several screens searched only `ACTIVE` pallets.
- Cleared empty pallets did not appear in Pallet QR Print, box-to-pallet link, or split target selection.

Why this is wrong:

- Backend can allow reuse, but users still cannot select the pallet.
- Operators would think the pallet is missing.

Correction:

- Reuse screens must show empty pallets with status `ACTIVE` or `CLEARED`.
- Source operation screens should still require `ACTIVE` pallets.

Screen rules:

- Pallet QR Print: show `ACTIVE` empty and `CLEARED` empty pallets.
- Link Box to Pallet: show compatible `ACTIVE` pallets and empty reusable `CLEARED` pallets.
- Split Pallet target: show `ACTIVE` empty and `CLEARED` empty target pallets.
- Move/Clear/Void/Dismantle source: require `ACTIVE`.

### 6. Error Messages Were Too Generic

Mistake:

- Some pages showed `Failed`, `Failed to move`, or `Failed to print`.
- Some API validation errors were not formatted cleanly.

Why this is wrong:

- Operators cannot fix the issue from the message.
- Support teams waste time checking logs for normal validation problems.

Correction:

- Barcode pages should use one shared error formatter.
- API messages like `Box item, batch, or UOM does not match the target pallet.` must be shown directly.
- Field errors like `box_ids: This list may not be empty` must be readable.

Production rule:

- Every blocked action should tell the user what to correct.

### 7. Clear, Dismantle, And Remove Need Distinct Meanings

Mistake:

- The business meaning of clear, dismantle, and remove could be confused.

Correct definitions:

- Remove boxes from pallet: Selected boxes are depalletized. Pallet remains active.
- Clear pallet: All active/partial boxes are removed. Pallet becomes reusable `CLEARED`.
- Dismantle pallet: Boxes are removed for repack/sample/damage/return reasons. If no active boxes remain, pallet becomes `CLEARED`.
- Dismantle box: Box quantity becomes loose stock.

Production rule:

- Use clear when the physical pallet is emptied for reuse.
- Use dismantle when stock is being broken down or changed.

## Corrected Lifecycle

### New Pallet Lifecycle

1. User creates empty pallet.
2. Pallet status is `ACTIVE`.
3. Pallet has no item context.
4. User links boxes or uses Pallet QR Print.
5. First box assignment sets item, batch, UOM, dates, and quantity context.

### Clear And Reuse Lifecycle

1. User clears an active pallet.
2. System removes all active/partial boxes.
3. System sets pallet status to `CLEARED`.
4. System clears current item/batch/UOM context.
5. Pallet appears as reusable empty pallet.
6. User links new boxes.
7. System sets pallet status back to `ACTIVE`.
8. New item/batch/UOM context is assigned from the linked boxes.

### Invalid Reuse Cases

These must stay blocked:

- Reusing a `VOID` pallet.
- Reusing a `SPLIT` pallet unless a future rule explicitly allows it.
- Adding boxes to a cleared pallet that still has active or partial boxes.
- Adding a mismatched item or batch to an active pallet with existing context.
- Adding boxes beyond capacity.

## Backend Corrections Required

### Pallet Clear

Must:

- Remove active and partial boxes.
- Create depalletize movement records.
- Set pallet status to `CLEARED`.
- Reset item code, item name, batch, UOM, max box count, total quantity, and production run.
- Rebuild pallet barcode data.
- Create clear movement.

Must not:

- Delete pallet record.
- Delete movement history.
- Delete old boxes.
- Change pallet ID.

### Add Boxes To Pallet

Must:

- Allow `ACTIVE` pallets.
- Allow `CLEARED` pallets only when empty.
- Reject `VOID` and `SPLIT` pallets.
- Reactivate `CLEARED` pallet on successful link.
- Set context from boxes when pallet is empty or cleared.
- Enforce item, batch, UOM, and capacity rules.
- Recalculate pallet totals.

### Tests Required

Backend tests must cover:

- Empty pallet can receive boxes.
- Active pallet rejects mismatched item/batch/UOM.
- Capacity is enforced.
- Clear pallet resets context.
- Cleared pallet can be reused for a different item/batch.
- Reused pallet keeps the same pallet ID.
- Reused pallet becomes `ACTIVE`.

## Frontend Corrections Required

### Pallet QR Print

Must show:

- Empty `ACTIVE` pallets.
- Empty `CLEARED` pallets.

Must not show:

- Non-empty pallets.
- `VOID` pallets.
- `SPLIT` pallets.

### Link Box To Pallet

Must show:

- Active compatible pallets with matching item, batch, and UOM.
- Empty active pallets with no context.
- Empty cleared pallets.

Must not show:

- Full pallets.
- Mismatched item/batch/UOM pallets.
- Void or split pallets.

### Split Target Pallet

Must show:

- Empty active pallets.
- Empty cleared pallets.

Must not show:

- Source pallet.
- Non-empty target pallets.
- Void or split pallets.

## Production Deployment Checklist

Before pushing to production:

- Run backend barcode tests.
- Run frontend build.
- Verify cleared pallet appears in Pallet QR Print.
- Verify cleared pallet appears in Link Box to Pallet.
- Verify adding boxes to cleared pallet changes status to `ACTIVE`.
- Verify cleared pallet can be reused for a different item and batch.
- Verify active pallet still rejects mismatched boxes.
- Verify capacity error message is clear.
- Verify movement history remains visible after reuse.
- Verify reports do not count cleared pallets as active stock.
- Confirm with operations whether `max_box_count` should reset on clear or remain as physical pallet capacity. Current rule resets it because current capacity is SKU/pallet-plan related.

## Pagination Analysis And Fix

Implemented on 2026-05-18.

### Pages That Need Pagination

- Box List: can grow quickly because every generated carton creates one row.
- Pallet List: can grow over time because pallet QR records are reusable and should not be deleted.
- Loose Stock List: can grow from dismantle, sample, damage, return, and repack flows.
- Print History: audit logs grow continuously and must stay searchable without loading all records.

### Pages That Should Not Use Main Table Pagination Yet

- Box Detail and Pallet Detail: these are single-record trace screens, not primary list screens.
- Link Box to Pallet, Split, Move, Dismantle, Repack, Reprint: these are operation screens. They should use filtered lookup lists so users can find valid targets quickly.
- Dashboard: should continue to load lightweight summary data. If dashboard counts become slow later, replace with aggregate endpoints instead of table pagination.

### Implementation Rule

- Backend list APIs now accept `page` and `page_size`.
- Default page size is 25.
- Maximum page size is 100.
- Paginated responses include `results`, `count`, `page`, `page_size`, `total_pages`, `next`, and `previous`.
- Existing dropdown/search consumers that do not send `page` or `page_size` continue to receive the old list response, capped at 500 records.

## Remaining Risks To Review

### SAP Posting

Risk:

- Moving or clearing pallets may need SAP stock transfer or warehouse confirmation depending on live process.

Decision needed:

- Decide which barcode operations are local traceability only and which post to SAP.

### Pallet Identity

Risk:

- Reusing the same pallet ID is correct for physical pallet tracking, but some reports may assume one pallet ID equals one batch lifecycle.

Decision needed:

- Reports must use movement history and current status, not only pallet ID.

### Cleared Pallet Date Fields

Risk:

- Pallet model requires manufacturing and expiry dates. Cleared pallet keeps old dates until new boxes are linked.

Decision needed:

- This is acceptable if UI treats cleared pallets as no-current-item. Future schema could allow null dates for empty pallets.

### Historical Label Reprints

Risk:

- Reprinting a reused pallet label prints current pallet context, not old context.

Decision needed:

- If old pallet labels must be reprinted exactly, label print logs need stored immutable label payload snapshots.

## Final Production Rule

A pallet record represents a reusable physical pallet QR. Its current item context is temporary and belongs only to the currently linked boxes. Clearing the pallet ends the current item assignment but does not delete the physical pallet identity or history.
