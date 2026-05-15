# Internal Lot Number Handling

## Database location

New Inspection data is stored in:

`quality_control_rawmaterialinspection`

The internal lot number column is:

`internal_lot_no`

Parameter/test result data is stored separately in:

`quality_control_inspectionparameterresult`

That table links back to the inspection through `inspection_id`.

## Current behavior

`internal_lot_no` is backend-generated only.

When a new inspection is created, the backend calls:

`RawMaterialInspection.generate_lot_no()`

The generated format is:

`LOT-YYYYMMDD-0001`

Example:

`LOT-20260502-0001`

The frontend should not send `internal_lot_no` in the New Inspection payload.

## Why the duplicate error happened

Previously, the create API accepted `internal_lot_no` from the request payload. If the frontend sent a manual value such as `36`, the backend tried to save `36` as the internal lot number.

That could produce an error like:

`Internal lot number '36' already exists`

The update path also generated a fresh lot number even when no lot number was sent, which could overwrite an existing inspection's lot number during edit.

## Fix applied

The create serializer no longer accepts `internal_lot_no`.

The create/update API now:

- Generates `internal_lot_no` only when creating a new inspection.
- Keeps the existing `internal_lot_no` unchanged when updating an inspection.
- Ignores any `internal_lot_no` value sent by the frontend.
- Returns a generic generated identifier error if a database identifier conflict happens.

## Frontend payload guidance

Do not send this field:

```json
{
  "internal_lot_no": "36"
}
```

If the user manually enters an internal report number, send it as:

```json
{
  "internal_report_no": "36"
}
```

The response will still include `internal_lot_no` for display after the backend creates it.
