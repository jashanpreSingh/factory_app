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
| `status` | comma-separated string | Allowed values: `healthy`, `low`, `critical`, `unset`. The `unset` value is displayed as No Benchmark Set. |
| `movement_status` | comma-separated string | Allowed values: `planned`, `recent`, `slow`. Omit to include all movement states. |
| `sort_by` | string | `item_code`, `item_name`, `warehouse`, `on_hand`, `min_stock`, `health_ratio`. The `min_stock` sort is the Benchmark column. |
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
| `OINM` | Inventory audit trail for outbound consumption history |
| `OWOR` | Open production orders |
| `WOR1` | Production order component demand and component warehouse |

Outbound consumption is taken from `OINM` rows with `OutQty > 0` and transaction types:

| TransType | Meaning |
|-----------|---------|
| `15` | Delivery |
| `60` | Goods Issue |
| `202` | Production Order |

Open planning demand is based on `OWOR.Status IN ('P', 'R')`, component rows with `ItemType = 4`, inventory items, and remaining demand where `PlannedQty - IssuedQty > 0`.

## Stock Status Rules

The backend owns stock status so filtering, returned rows, grouped rows, and meta counts stay consistent.

| Status | Rule |
|--------|------|
| `healthy` | Benchmark is set and `OnHand >= Benchmark` |
| `low` | Benchmark is set, `OnHand < Benchmark`, and `OnHand >= Benchmark * 0.6` |
| `critical` | Benchmark is set and `OnHand < Benchmark * 0.6` |
| `critical` | Benchmark is not set and open planning demand exists |
| `unset` | Benchmark is not set and no open planning demand exists |

The SAP field behind Benchmark is `MinStock`; the API field remains `min_stock` for compatibility. The planned-without-benchmark rule is intentional: a planned item with no benchmark is Critical because SAP shows real demand but no configured benchmark.

## Movement Rules

`SLOW_MOVING_DAYS` is currently `30`.

| Movement | Rule |
|----------|------|
| `planned` | Open planning demand exists. |
| `recent` | No open planning demand, and last outbound consumption is within 30 days. |
| `slow` | No open planning demand, and no outbound consumption exists or the last outbound consumption is older than 30 days. |

Planning takes precedence over consumption age.

## Grouped Rows

If two or more warehouses are selected, the service returns grouped item rows:

- `on_hand` is summed across selected warehouses.
- Benchmark (`min_stock`) is summed across selected warehouses.
- `warehouse` is displayed as `<n> warehouses`.
- `warehouse_count` contains the number of contributing warehouse rows.
- `has_warning` is set when a child warehouse has a worse status than the aggregate row.
- `planned_without_benchmark` is included internally so grouped rows and grouped stats can treat any planned no-benchmark child as Critical.

## Meta Counts

The response meta contains:

| Field | Description |
|-------|-------------|
| `total_items` | Number of rows after the active backend filters. |
| `healthy_count` | Count of rows classified as Healthy. |
| `low_stock_count` | Count of rows classified as Low. |
| `critical_stock_count` | Count of rows classified as Critical, including planned-without-benchmark rows. |
| `warehouses` | Distinct warehouse list from SAP. |
| `page`, `page_size`, `total_pages` | Pagination metadata. |

The frontend Stock Benchmark page uses a separate pinned stats query for the top cards. That query uses default Packing Material, warehouses `BH-BS,BH-PM`, statuses `healthy,low,critical`, and no movement filter.

## Tests

Run the stock dashboard test suite with:

```powershell
$env:DEBUG='False'; .\.venv\Scripts\python.exe manage.py test stock_dashboard
```
