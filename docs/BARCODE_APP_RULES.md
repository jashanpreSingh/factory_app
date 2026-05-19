# Barcode App Rules

This document defines when each barcode operation is allowed and what the system must update.

## Main Records

- Pallet: A container that can hold boxes. It has a pallet ID, item context, batch, warehouse, status, capacity, box count, and total quantity.
- Box: A carton or label unit. It has a box barcode, item context, batch, quantity, warehouse, status, and optional pallet link.
- Loose Stock: Stock created by dismantling boxes.
- Movements: Audit records for every box or pallet operation.
- Label Print Log: Audit records for printed and reprinted labels.
- Barcode Sequence: Counter used to generate the next box or pallet number.

## Pallet Status Rules

- `ACTIVE`: Pallet can be used for normal operations.
- `CLEARED`: Pallet has been cleared, has no linked boxes, and can be reused as an empty pallet.
- `SPLIT`: Reserved status for split workflows if used by future logic.
- `VOID`: Pallet is cancelled and cannot be used.

Only `ACTIVE` pallets can be moved, cleared, split as a source pallet, dismantled, or voided.
`ACTIVE` and `CLEARED` empty pallets can receive boxes. When a `CLEARED` pallet receives boxes, it becomes `ACTIVE` again.

## Box Status Rules

- `ACTIVE`: Box can be linked, transferred, dismantled, or voided.
- `PARTIAL`: Box has been partially dismantled but can still count in pallet totals.
- `DISMANTLED`: Box has been fully converted to loose stock and cannot be used as a normal box.
- `VOID`: Box is cancelled and cannot be used.

Only `ACTIVE` or `PARTIAL` boxes can be added to pallets, transferred, removed, or counted in pallet totals.

## Create Pallet

Allowed when:

- User is authenticated.
- User has a valid company context.
- Warehouse is provided by the frontend workflow.

Rules:

- Create the pallet empty.
- Do not attach boxes during pallet creation.
- Generate a unique pallet ID using company, date, and production line.
- Initial item code, item name, batch, UOM, and total quantity are blank or zero for a generic empty pallet.
- Status must be `ACTIVE`.
- Create one pallet movement with type `CREATE`.

Not allowed when:

- Request tries to create a pallet with `box_ids`.
- Required company context is missing.
- Duplicate pallet ID is generated.

## Generate Boxes

Allowed when:

- User is authenticated.
- User has a valid company context.
- Item code, batch, quantity, box count, manufacturing date, and warehouse are provided.
- Box count is between 1 and the configured maximum.

Rules:

- Generate unique box barcodes using company, date, production line, and sequence.
- Every generated box starts as `ACTIVE`.
- Boxes are created unpalletized unless generated through a pallet-specific workflow.
- Create one box movement with type `CREATE` for every generated box.
- Store barcode payload data on each box.

Not allowed when:

- Quantity is not positive.
- Box count is missing, zero, negative, or above the maximum.
- Required item or date fields are missing.
- Duplicate box barcode is generated.

## Add Box To Pallet

Allowed when:

- Target pallet is `ACTIVE`, or target pallet is `CLEARED` and empty.
- Box is `ACTIVE` or `PARTIAL`.
- Box is not already linked to another pallet.
- Pallet capacity is not exceeded.

Rules:

- If the pallet is empty and has no item context, the first linked box sets the pallet item code, item name, batch, UOM, manufacturing date, expiry date, production line, and production run.
- If the pallet is `CLEARED`, linking boxes reactivates it and sets the new item context from the linked box.
- If the pallet already has item context, every added box must match the pallet item code, batch, and UOM.
- All boxes added in one request to an empty pallet must have the same item code, batch, and UOM.
- Linked boxes move to the pallet warehouse.
- Create one box movement with type `PALLETIZE` for each linked box.
- Recalculate pallet box count, total quantity, and barcode payload after linking.

Not allowed when:

- Pallet is `SPLIT` or `VOID`.
- Pallet is `CLEARED` but still has linked active or partial boxes.
- Box is `DISMANTLED` or `VOID`.
- Box is already on a pallet.
- Box item, batch, or UOM differs from the pallet.
- Pallet capacity would be exceeded.

## Remove Box From Pallet

Allowed when:

- Pallet is `ACTIVE`.
- Selected boxes are currently on that pallet.
- Selected boxes are `ACTIVE` or `PARTIAL`.

Rules:

- Remove the selected boxes from the pallet.
- Keep the boxes in their current warehouse.
- Create one box movement with type `DEPALLETIZE` for each removed box.
- Recalculate pallet box count, total quantity, and barcode payload.
- Create one pallet movement with type `DISMANTLE` noting removed quantity.

Not allowed when:

- Pallet is not `ACTIVE`.
- Any selected box is not on the pallet.
- Any selected box is not active or partial.

## Clear Pallet

Allowed when:

- Pallet is `ACTIVE`.
- Pallet has at least one active or partial box.

Rules:

- Remove all active and partial boxes from the pallet.
- Set pallet status to `CLEARED`.
- Set pallet box count, maximum box count, and total quantity to zero.
- Clear item code, item name, batch, UOM, and production run so the pallet can be reused for a different item or batch.
- Keep the same pallet ID and warehouse.
- Create box movements with type `DEPALLETIZE`.
- Create a pallet movement with type `CLEAR`.

Not allowed when:

- Pallet is not `ACTIVE`.
- Pallet has no active boxes.

## Move Pallet

Allowed when:

- Pallet is `ACTIVE`.
- Destination warehouse is provided.
- Destination warehouse is different from current warehouse.

Rules:

- Move the pallet to the destination warehouse.
- Move all active or partial boxes on the pallet to the same warehouse.
- Create a pallet movement with type `MOVE`.
- Create box movements with type `MOVE` or transfer-related movement for affected boxes.

Not allowed when:

- Pallet is not `ACTIVE`.
- Source and destination warehouse are the same.

## Split Pallet

Allowed when:

- Source pallet is `ACTIVE`.
- Target pallet is `ACTIVE`, or target pallet is `CLEARED` and empty.
- Target pallet is different from source pallet.
- Target pallet is empty.
- Selected boxes are active or partial and belong to the source pallet.
- Not all source pallet boxes are selected.

Rules:

- Move selected boxes from source pallet to target pallet.
- If the target pallet is `CLEARED`, reactivate it to `ACTIVE`.
- Target pallet item code, item name, batch, UOM, manufacturing date, expiry date, production line, and production run are set from the moved boxes when the target is empty.
- Selected boxes must share the same item code, batch, and UOM.
- Target pallet capacity must not be exceeded.
- Move selected boxes to the target pallet warehouse.
- Recalculate both pallet totals.
- Create source and target pallet movement records with type `SPLIT`.
- Create box movement records for depalletizing from source and palletizing into target.

Not allowed when:

- Target pallet is the same as source pallet.
- Target pallet is not empty.
- Target pallet is `SPLIT` or `VOID`.
- Target pallet capacity would be exceeded.
- Any selected box is missing or not on the source pallet.
- All boxes are selected. Use Move Pallet instead.

## Void Box

Allowed when:

- Box exists and is not already `VOID`.

Rules:

- Set box status to `VOID`.
- Remove box from pallet if linked.
- Create box movement with type `VOID`.
- Recalculate old pallet totals if the box was on an active pallet.

Not allowed when:

- Box is already `VOID`.

## Void Pallet

Allowed when:

- Pallet exists and is not already `VOID`.

Rules:

- Set pallet status to `VOID`.
- Remove active boxes from the pallet.
- Create box movements with type `DEPALLETIZE`.
- Create pallet movement with type `VOID`.

Not allowed when:

- Pallet is already `VOID`.

## Dismantle Pallet

Allowed when:

- Pallet is `ACTIVE`.
- Pallet has active boxes.
- Optional selected boxes are active and belong to the pallet.

Rules:

- Remove selected boxes, or all active boxes when no box IDs are provided.
- Create box movements with type `DISMANTLE`.
- Recalculate pallet totals.
- If no active boxes remain, set pallet status to `CLEARED` and clear item code, item name, batch, UOM, production run, capacity, and total quantity so the physical pallet can be reused.
- Create pallet movement with type `DISMANTLE`.

Not allowed when:

- Pallet is not `ACTIVE`.
- No active boxes exist.
- Selected boxes are not active or do not belong to the pallet.

## Dismantle Box

Allowed when:

- Box is `ACTIVE` or `PARTIAL`.
- Dismantle quantity is positive.
- Dismantle quantity does not exceed box quantity.

Rules:

- Create loose stock for dismantled quantity.
- If full quantity is dismantled, set box status to `DISMANTLED` and quantity to zero.
- If partial quantity is dismantled, reduce box quantity and set status to `PARTIAL`.
- Create box movement with type `DISMANTLE`.
- Recalculate pallet totals when the box is on an active pallet.

Not allowed when:

- Box is `DISMANTLED` or `VOID`.
- Quantity is zero or negative.
- Quantity exceeds available box quantity.

## Repack Loose Stock

Allowed when:

- Selected loose stock records are `ACTIVE`.
- All selected loose stock records have the same item and batch.
- Destination warehouse is provided.

Rules:

- Create a new box from loose stock.
- Reduce or consume loose stock quantities.
- Mark fully used loose stock as `REPACKED`.
- Link loose stock records to the new box.
- Create movement records for traceability.

Not allowed when:

- Any loose stock record is not active.
- Selected records have mixed item or batch.
- Repack quantity is zero, negative, or greater than available loose quantity.

## Print And Reprint Labels

Allowed when:

- Box or pallet exists.
- Reprint requests include a reprint reason.

Rules:

- Return label data to the frontend.
- Create label print log records.
- Reprints must be logged with print type `REPRINT` and reason.

Not allowed when:

- Box or pallet does not exist.
- Reprint reason is missing for reprint workflows.

## Scan And Lookup

Allowed when:

- User is authenticated and has company context.
- Barcode text is provided.

Rules:

- Parse QR payloads and simple barcode strings.
- Return entity type, entity ID, status, and core item data when found.
- Log scans through the scan endpoint.
- Lookup endpoint does not create scan logs.

Not allowed when:

- Barcode is missing or cannot be matched to a box or pallet.

## Data Deletion Rule

When resetting barcode data for testing, delete only barcode-owned data:

- Label print logs
- Scan logs
- Loose stock
- Box movements
- Pallet movements
- Boxes
- Pallets
- Barcode sequences

Do not delete users, companies, warehouses, production runs, SAP configuration, or non-barcode module records.
