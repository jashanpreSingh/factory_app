# Barcode Dispatch SAP Sync Implementation Guide

## Current State

SAP sync is currently disabled for barcode dispatch completion.

When the user clicks **Confirm Dispatch**, the system only completes the dispatch locally:

- Updates scanned box / pallet quantities locally
- Marks boxes as fully or partially dispatched
- Updates pallet status
- Marks the dispatch session as `COMPLETED`
- Does not post or update anything in SAP

Current local-only completion logic is in:

```text
barcode/services/dispatch_service.py
BarcodeDispatchService.complete_session()
```

## Where SAP Sync Should Be Added Later

Add SAP sync inside:

```python
BarcodeDispatchService.complete_session()
```

Recommended position:

1. Validate the session can be completed.
2. Apply local scanned box dispatch.
3. Build SAP sync payload from the final dispatched quantities.
4. Post/update SAP.
5. Save SAP response and sync status.
6. Return updated dispatch session.

Do not calculate SAP quantity from bill quantity. Use scanned dispatch quantities only.

## Main Data Source for SAP Payload

Use these local models:

```text
DispatchSession
DispatchSessionLine
DispatchScannedUnit
DispatchScanLog
Box
Pallet
```

Important quantity source:

```text
DispatchScannedUnit.dispatch_qty
```

Do not use full box quantity blindly.

## Data to Send to SAP

Header-level data:

```text
DispatchSession.bill_number
DispatchSession.sap_doc_entry
DispatchSession.sap_doc_num
DispatchSession.delivery_number
DispatchSession.reference_delivery_number
DispatchSession.customer_code
DispatchSession.customer_name
DispatchSession.ship_to_code
DispatchSession.ship_to_name
DispatchSession.dispatched_at
DispatchSession.dispatched_by
```

Line-level data:

```text
DispatchSessionLine.sap_line_no
DispatchSessionLine.material_code
DispatchSessionLine.material_description
DispatchSessionLine.bill_qty
DispatchSessionLine.scanned_qty
DispatchSessionLine.uom
DispatchSessionLine.batch_number
DispatchSessionLine.warehouse_code
```

Barcode traceability data:

```text
DispatchScannedUnit.barcode_value
DispatchScannedUnit.entity_type
DispatchScannedUnit.box.box_barcode
DispatchScannedUnit.pallet.pallet_id
DispatchScannedUnit.material_code
DispatchScannedUnit.batch_number
DispatchScannedUnit.total_box_qty
DispatchScannedUnit.dispatch_qty
DispatchScannedUnit.remaining_qty
DispatchScannedUnit.uom
DispatchScannedUnit.scan_status
DispatchScannedUnit.created_at
DispatchScannedUnit.scan_log.scanned_by
```

## Suggested Payload Shape

```json
{
  "dispatch_doc_no": "626050605",
  "sap_doc_entry": "74260",
  "customer_code": "CUST001",
  "customer_name": "Customer Name",
  "dispatch_datetime": "2026-05-29T12:30:00+05:30",
  "scanned_by": "warehouse.user",
  "lines": [
    {
      "sap_line_no": "0",
      "item_code": "FG0000383",
      "item_name": "REFINED OIL 13 KG",
      "warehouse": "BH-BS",
      "batch_no": "324",
      "dispatch_qty": "10.000",
      "uom": "PCS",
      "barcodes": [
        {
          "barcode_type": "BOX",
          "box_barcode": "BOX-20260529-L1-001",
          "pallet_barcode": "PLT-20260529-L1-001",
          "original_qty": "20.000",
          "dispatched_qty": "10.000",
          "remaining_qty": "10.000",
          "status_after_dispatch": "Partial Dispatch"
        }
      ]
    }
  ]
}
```

## How to Group Quantities

For SAP line posting:

```text
Group DispatchScannedUnit by:
- line.sap_line_no
- material_code
- batch_number
- warehouse

Sum:
- dispatch_qty
```

For barcode traceability:

```text
Send or store each DispatchScannedUnit separately.
```

This keeps SAP quantity posting simple while preserving full barcode-level audit in the app.

## Existing Adapter to Extend

Extend this method:

```python
SapDispatchAdapter.update_dispatch_status(session)
```

Current behavior:

```text
Returns NOT_CONFIGURED.
Does not call SAP.
```

Future behavior:

```text
Build payload from DispatchScannedUnit records.
Call SAP Service Layer or required SAP endpoint.
Return SapUpdateResult with request and response payload.
```

## Sync Audit Table

Use existing model:

```text
DispatchSapSyncLog
```

Write one log record per sync attempt:

```text
session
operation
request_payload
response_payload
status
error_message
attempt_no
created_at
```

Recommended operation names:

```text
UPDATE_DISPATCH_STATUS
RETRY_UPDATE_DISPATCH_STATUS
```

## Session Status Rules After SAP Sync

If SAP sync succeeds:

```text
DispatchSession.status = COMPLETED
DispatchSession.sap_update_status = SUCCESS
DispatchSession.sap_update_error = ""
```

If SAP sync fails but local dispatch is already completed:

```text
DispatchSession.status = SAP_SYNC_FAILED
DispatchSession.sap_update_status = FAILED
DispatchSession.sap_update_error = SAP error message
```

If SAP sync is disabled:

```text
DispatchSession.status = COMPLETED
DispatchSession.sap_update_status = NOT_CONFIGURED
DispatchSession.sap_update_error = "SAP sync is disabled for barcode dispatch."
```

## Important Rule

SAP sync must never overwrite local barcode dispatch history.

Local traceability should remain the source of truth for:

- Which pallet was scanned
- Which box was scanned
- Original box quantity
- Dispatched quantity
- Remaining quantity
- Scan date/time
- Scanned by user
- Dispatch document number
- Current barcode status

## Retry Flow

The project already has retry endpoint wiring:

```text
POST /api/v1/barcode/dispatch/sessions/<session_id>/retry-sap-sync/
```

The retry method is:

```python
BarcodeDispatchService.retry_sap_sync()
```

When SAP sync is re-enabled, restore the frontend retry button only for:

```text
DispatchSession.status == SAP_SYNC_FAILED
```

## Implementation Checklist

1. Create payload builder method, for example:

```python
BarcodeDispatchService.build_sap_dispatch_payload(session)
```

2. Extend:

```python
SapDispatchAdapter.update_dispatch_status(session)
```

3. Reconnect SAP call in:

```python
BarcodeDispatchService.complete_session()
```

4. Create `DispatchSapSyncLog` for every attempt.

5. Re-enable frontend SAP status and retry UI only if required.

6. Test:

```text
Full box dispatch
Partial box dispatch
Multiple boxes for one item
Pallet dispatch with partial final box
SAP sync success
SAP sync failure
SAP retry success
Duplicate retry prevention
```

