# TSC TTP-244 Pro Barcode Printing

> Superseded for the current DA310 setup. Use
> `factory_app/docs/TSC_DA310_BARCODE_PRINTING.md` for the active
> `100mm x 40mm` label configuration.

This document explains how the TSC TTP-244 Pro printer integration works in the current barcode module implementation.

## What Was Implemented

The first implementation uses the safest production pilot path from `BARCODE_TSC_TTP244_PRO_INTEGRATION.md`:

```text
FactoryFlow barcode page
        |
        v
Backend print endpoint logs print metadata
        |
        v
Frontend renders 60mm x 40mm label
        |
        v
Browser print dialog
        |
        v
Windows TSC printer driver
        |
        v
TSC TTP-244 Pro printer
```

This does not send raw TSPL commands yet. It prints through the Windows/browser print stack, which is the right first step for the USB TSC TTP-244 Pro setup.

## Supported Print Profiles

The frontend now supports two print profiles:

| Profile         | Use                                                            |
| --------------- | -------------------------------------------------------------- |
| `THERMAL_60X40` | Direct 60mm x 40mm thermal label printing for TSC TTP-244 Pro  |
| `A4_SHEET`      | Fallback sheet printing with multiple 60mm x 40mm labels on A4 |

The default profile is:

```text
THERMAL_60X40
```

The default printer name is:

```text
TSC TTP-244 Pro
```

The selected printer name and print profile are stored in browser local storage, so the operator does not need to set them again on every page.

## Frontend Flow

Frontend files:

```text
FactoryFlow/src/modules/barcode/components/labelPrint.ts
FactoryFlow/src/modules/barcode/components/PrinterProfileControls.tsx
FactoryFlow/src/modules/barcode/hooks/usePrinterProfile.ts
FactoryFlow/src/modules/barcode/pages/LabelGeneratePage.tsx
FactoryFlow/src/modules/barcode/pages/ReprintPage.tsx
FactoryFlow/src/modules/barcode/types/barcode.types.ts
```

### Label Generation

On `Generate Labels`, the operator can select:

- Printer name
- Print profile

When boxes are generated, the frontend calls bulk print with the selected printer name:

```json
{
  "items": [
    {
      "label_type": "BOX",
      "id": 123,
      "printer_name": "TSC TTP-244 Pro"
    }
  ]
}
```

The backend returns label data. The frontend renders the labels and prints using the selected page style.

### Reprint

On `Reprint Labels`, the operator can select:

- Printer name
- Print profile
- Reprint reason

The print request includes the selected printer name:

```json
{
  "print_type": "REPRINT",
  "reprint_reason": "Label damaged",
  "printer_name": "TSC TTP-244 Pro"
}
```

## Backend Flow

Backend files:

```text
factory_app/barcode/serializers.py
factory_app/barcode/views.py
factory_app/barcode/services/label_service.py
factory_app/barcode/models.py
factory_app/barcode/tests.py
```

The backend already had `LabelPrintLog.printer_name`. The implementation now ensures:

- Single box print logs `printer_name`.
- Single pallet print logs `printer_name`.
- Bulk print also logs `printer_name`.
- Bulk print items are validated with a structured serializer.
- `printer_name` is limited to 100 characters to match the database field.

## Print Audit

Every successful print/reprint records a `LabelPrintLog` row.

Important fields:

```text
label_type
reference_id
reference_code
print_type
reprint_reason
printed_by
printed_at
printer_name
```

This lets the team answer:

- Who printed this label?
- Was it original or reprint?
- Why was it reprinted?
- Which printer/profile was used?

## Machine Setup Steps

1. Connect the TSC TTP-244 Pro to the operator PC by USB.
2. Install the official TSC Windows printer driver.
3. In Windows printer preferences, create/select label size `60mm x 40mm`.
4. Set media type, gap sensor, print speed, and density.
5. Calibrate the printer with the loaded label roll.
6. Open FactoryFlow barcode module.
7. Set printer name to `TSC TTP-244 Pro`.
8. Set print profile to `TSC 60 x 40 mm`.
9. Generate or reprint one label.
10. In browser print dialog, select the TSC printer and disable scaling if needed.
11. Scan the printed QR/barcode and confirm it resolves to the same box or pallet.

## Current Limitation

This implementation still uses the browser print dialog. The backend logs the selected printer name, but it cannot physically confirm that the USB printer printed the label.

For fully automatic printing without the browser dialog, the next phase should add one of these:

- Raw TSPL print through network port `9100`
- Windows shared-printer transport
- Local print agent on the operator PC

## Test Coverage

Backend test added:

```text
test_label_print_log_stores_tsc_printer_name
```

This confirms the selected TSC printer name is stored in print history.

Recommended physical test:

1. Print one box label.
2. Print one pallet label.
3. Reprint one label with reason.
4. Print 10 labels in bulk.
5. Scan every printed label.
6. Confirm print history shows printer name and reprint reason.
