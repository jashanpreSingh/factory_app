# Stock Dashboard API

The stock dashboard API powers the frontend Stock Benchmark page. It reads SAP HANA directly and does not write application database rows.

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/dashboards/stock/` | Stock benchmark rows, pagination, and meta counts |
| GET | `/api/v1/dashboards/stock/<item_code>/warehouses/` | Per-warehouse detail for an expanded grouped item |

All endpoints require:

- JWT authentication
- `Company-Code` header
- `can_view_stock_dashboard` permission

## Query Parameters

`GET /api/v1/dashboards/stock/`

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Case-insensitive match against item code, item name, or warehouse code. |
| `warehouse` | comma-separated string | Warehouse codes. Two or more warehouses switch the service to grouped item rows. |
| `item_group` | string | SAP item group name from `OITB.ItmsGrpNam`, for example `PACKAGING MATERIAL`. |
| `status` | comma-separated string | Allowed values: `healthy`, `low`, `critical`, `unset`. The `unset` value is displayed as No Benchmark Set. When the default operational set `healthy,low,critical` is used without a movement filter excluding slow rows, slow rows with a benchmark are still returned with no stock status so the Movement filter owns slow-moving visibility. |
| `movement_status` | comma-separated string | Allowed values: `planned`, `recent`, `slow`. Omit to include all movement states. |
| `sort_by` | string | `item_code`, `item_name`, `warehouse`, `on_hand`, `min_stock`, `planned_qty`, `health_ratio`. The `min_stock` sort is the Benchmark column. |
| `sort_dir` | string | `asc` or `desc`. |
| `page` | integer | Page number, minimum 1. |
| `page_size` | integer | Page size, minimum 1, maximum 200. |

`GET /api/v1/dashboards/stock/<item_code>/warehouses/`

| Parameter | Type | Description |
|-----------|------|-------------|
| `warehouse` | comma-separated string | Required warehouse list for the per-warehouse breakdown. |

## SAP HANA Sources

| SAP table | Usage |
|-----------|-------|
| `OITW` | Item warehouse stock, `OnHand`, benchmark (`MinStock`), warehouse code |
| `OITM` | Item name, inventory UOM, inventory item flag |
| `OITB` | Item group name for material type filtering |
| `OINM` | Inventory audit trail for item-level outbound consumption history |
| `OWOR` | Open production orders |
| `WOR1` | Production order component demand and component warehouse |

Outbound consumption is taken from `OINM` rows with `OutQty > 0` and transaction types:

| TransType | Meaning |
|-----------|---------|
| `15` | Delivery |
| `60` | Goods Issue |
| `202` | Production Order |

Open planning demand is based on `OWOR.Status IN ('P', 'R')`, component rows with `ItemType = 4`, inventory items, and remaining demand where `PlannedQty - IssuedQty > 0`. The response exposes that remaining demand as `planned_qty`.
Stock and benchmark quantities are limited to the selected warehouses. Movement age is item-level: recent consumption in any warehouse prevents the item from being classified as slow-moving in Stock Benchmark.

## Stock Status Rules

The backend owns stock status so filtering, returned rows, grouped rows, and meta counts stay consistent.
Rows classified as `slow` movement do not receive a stock health status and are not counted as Healthy, Low, Critical, or No Benchmark Set. Benchmarked slow rows remain visible in the default Stock Benchmark view as no-status rows; slow rows with no benchmark stay out of the default operational status view.

| Status | Rule |
|--------|------|
| `healthy` | Not slow-moving, required quantity is set, and `OnHand >= Benchmark + Planned Qty` |
| `low` | Not slow-moving, required quantity is set, `OnHand < Benchmark + Planned Qty`, and `OnHand >= (Benchmark + Planned Qty) * 0.6` |
| `critical` | Not slow-moving, required quantity is set, and `OnHand < (Benchmark + Planned Qty) * 0.6` |
| `unset` | Not slow-moving, benchmark and planned quantity are both zero |

The SAP field behind Benchmark is `MinStock`; the API field remains `min_stock` for compatibility. `planned_qty` is part of the required quantity used for status, health ratio, and health sorting.

## Movement Rules

`SLOW_MOVING_DAYS` is currently `30`.

| Movement | Rule |
|----------|------|
| `planned` | Open planning demand exists. |
| `recent` | No open planning demand, and last outbound consumption is within 30 days. |
| `slow` | No open planning demand, and no outbound consumption exists or the last outbound consumption is older than 30 days. |

Planning takes precedence over consumption age.
Consumption age is checked by item code across SAP inventory movement, not only the selected Stock Benchmark warehouses.

## Grouped Rows

If two or more warehouses are selected, the service returns grouped item rows:

- `on_hand` is summed across selected warehouses.
- Benchmark (`min_stock`) is summed across selected warehouses.
- `planned_qty` is summed from open production order component demand across selected warehouses.
- `warehouse` is displayed as `<n> warehouses`.
- `warehouse_count` contains the number of contributing warehouse rows.
- `has_warning` is set when a child warehouse has a worse status than the aggregate row.
- A grouped row can be Healthy while still showing `has_warning=true` when an individual child warehouse is Low or Critical.

## Meta Counts

The response meta contains:

| Field | Description |
|-------|-------------|
| `total_items` | Number of rows after the active backend filters, including no-status slow rows when they are visible. |
| `healthy_count` | Count of non-slow rows classified as Healthy. |
| `low_stock_count` | Count of non-slow rows classified as Low. |
| `critical_stock_count` | Count of non-slow rows classified as Critical. |
| `warehouses` | Distinct warehouse list from SAP. |
| `page`, `page_size`, `total_pages` | Pagination metadata. |

The frontend Stock Benchmark page uses a separate pinned stats query for the top cards. That query uses default Packing Material, warehouses `BH-BS,BH-PM`, statuses `healthy,low,critical`, and movements `planned,recent`.

## Tests

Run the stock dashboard test suite with:

```powershell
$env:DEBUG='False'; .\.venv\Scripts\python.exe manage.py test stock_dashboard
```
