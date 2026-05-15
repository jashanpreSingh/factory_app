# TSC DA310 Barcode Label Printing

This barcode print flow is configured for browser printing through the Windows
TSC printer driver. Each generated box or pallet barcode is rendered as one
physical label-sized page.

## Label Size

```text
Width:  100 mm
Height: 40 mm
Printer: TSC DA310
Profile: TSC_DA310_100X40
```

The frontend print style is defined in:

```text
FactoryFlow/src/modules/barcode/components/labelPrint.ts
```

The important print CSS is:

```css
@page {
  size: 100mm 40mm;
  margin: 0;
}

@media print {
  html,
  body {
    width: 100mm;
    min-height: 40mm;
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
    overflow: visible !important;
  }

  .barcode-print-sheet {
    width: 100mm;
    margin: 0;
    padding: 0;
    background: #fff;
    display: block;
  }

  .barcode-label {
    width: 100mm;
    height: 40mm;
    margin: 0;
    break-after: page;
    page-break-after: always;
    break-inside: avoid;
    page-break-inside: avoid;
    overflow: hidden;
  }

  .barcode-label:last-child {
    break-after: auto;
    page-break-after: auto;
  }
}
```

## Print Structure

The off-screen print container must render labels like this:

```html
<div class="barcode-print-sheet">
  <div class="barcode-label">...</div>
  <div class="barcode-label">...</div>
  <div class="barcode-label">...</div>
</div>
```

Rules:

- One `.barcode-label` equals one physical `100mm x 40mm` page.
- Multiple labels are rendered as sibling `.barcode-label` elements.
- Do not use an A4 grid for barcode printing.
- Use `react-to-print` `ignoreGlobalStyles: true` for barcode labels so the
  app-level A4 `@page` style does not override the label page size.

## TSC DA310 Setup

On the operator PC:

1. Install the TSC Windows printer driver for the DA310.
2. Add/select the `TSC DA310` printer in Windows.
3. In printer preferences, create or select stock size `100 mm x 40 mm`.
4. Set media type to match the loaded labels, usually gap labels.
5. Calibrate the media/gap sensor after loading the roll.
6. Set browser print scale to `100%` or `Actual size`.
7. Set margins to `None` or the smallest available value.
8. Disable browser header/footer printing.
9. Print one label, scan it, then print a multi-label batch and confirm each
   barcode starts on its own label.

For the DA310 at 300 DPI, `100mm x 40mm` is approximately `1181 x 472` printer
dots. If a future direct TSPL flow is added, use those dimensions for command
layout calculations.
