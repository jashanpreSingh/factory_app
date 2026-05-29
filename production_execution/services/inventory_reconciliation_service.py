from datetime import date
from typing import Any, Dict, List, Tuple

from sap_client.context import CompanyContext

from .production_movement_reader import ProductionMovementReader


class InventoryReconciliationService:
    """Builds expected-vs-actual inventory reconciliation rows across SAP warehouses."""

    def __init__(self, company_code: str):
        self.company_code = company_code
        self.context = CompanyContext(company_code)
        self.reader = ProductionMovementReader(self.context)

    def get_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        normalized_filters = self._normalize_filters(filters)
        transfer_movements = self.reader.get_movements(
            {
                **normalized_filters,
                "direction": "all",
                "production_only": False,
                "transaction_types": [67],
                "warehouse": "",
            }
        )
        production_orders = self.reader.get_production_order_reconciliations(
            normalized_filters
        )
        components = self.reader.get_component_reconciliations(normalized_filters)

        transfer_rows = self._build_transfer_reconciliations(transfer_movements)
        if normalized_filters.get("warehouse"):
            warehouse = normalized_filters["warehouse"]
            transfer_rows = [
                row
                for row in transfer_rows
                if row["from_warehouse"] == warehouse or row["to_warehouse"] == warehouse
            ]
        production_rows = [self._add_status(row) for row in production_orders]
        component_rows = [self._add_status(row) for row in components]

        return {
            "summary": self._build_summary(
                transfer_rows,
                production_rows,
                component_rows,
            ),
            "transfer_reconciliations": transfer_rows,
            "production_reconciliations": production_rows,
            "component_reconciliations": component_rows,
            "meta": {
                "date_from": normalized_filters["date_from"].isoformat(),
                "date_to": normalized_filters["date_to"].isoformat(),
                "warehouse": normalized_filters.get("warehouse") or "",
                "search": normalized_filters.get("search") or "",
                "limit": int(normalized_filters.get("limit") or 500),
            },
        }

    def _normalize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        date_to = filters.get("date_to") or date.today()
        date_from = filters.get("date_from") or date_to

        return {
            **filters,
            "date_from": date_from,
            "date_to": date_to,
            "warehouse": (filters.get("warehouse") or "").strip(),
            "search": (filters.get("search") or "").strip(),
            "limit": min(int(filters.get("limit") or 500), 1000),
        }

    def _build_transfer_reconciliations(
        self,
        movements: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        buckets: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = {}

        for movement in movements:
            key = (
                movement["created_by"] or movement["reference"] or movement["doc_num"],
                movement["item_code"],
                movement["from_warehouse"],
                movement["to_warehouse"],
                movement["reference"],
            )
            if key not in buckets:
                buckets[key] = {
                    "source_type": "transfer",
                    "document": movement["reference"] or movement["doc_num"],
                    "doc_entry": movement["created_by"],
                    "date": movement["date"],
                    "item_code": movement["item_code"],
                    "item_name": movement["item_name"],
                    "from_warehouse": movement["from_warehouse"],
                    "from_warehouse_name": movement["from_warehouse_name"],
                    "to_warehouse": movement["to_warehouse"],
                    "to_warehouse_name": movement["to_warehouse_name"],
                    "expected_qty": 0.0,
                    "actual_qty": 0.0,
                    "difference_qty": 0.0,
                    "entries": [],
                    "entry_count": 0,
                    "status": "balanced",
                }

            bucket = buckets[key]
            bucket["entries"].append(movement)
            bucket["entry_count"] += 1
            bucket["expected_qty"] += movement["out_qty"]
            bucket["actual_qty"] += movement["in_qty"]
            if not bucket["date"] or movement["date"] > bucket["date"]:
                bucket["date"] = movement["date"]

        rows = []
        for bucket in buckets.values():
            bucket["expected_qty"] = round(bucket["expected_qty"], 3)
            bucket["actual_qty"] = round(bucket["actual_qty"], 3)
            bucket["difference_qty"] = round(
                bucket["expected_qty"] - bucket["actual_qty"],
                3,
            )
            rows.append(self._add_status(bucket))

        return sorted(
            rows,
            key=lambda row: (
                abs(row["difference_qty"]),
                row.get("date", ""),
                row.get("document", ""),
            ),
            reverse=True,
        )

    def _add_status(self, row: Dict[str, Any]) -> Dict[str, Any]:
        difference = round(float(row.get("difference_qty") or 0), 3)
        row["difference_qty"] = 0.0 if abs(difference) < 0.001 else difference

        if row["difference_qty"] == 0:
            row["status"] = "balanced"
        elif row["actual_qty"] == 0:
            row["status"] = "missing"
        elif row["actual_qty"] < row["expected_qty"]:
            row["status"] = "short"
        else:
            row["status"] = "extra"

        return row

    def _build_summary(
        self,
        transfers: List[Dict[str, Any]],
        production: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        groups = {
            "transfer_mismatches": transfers,
            "production_shortfalls": production,
            "component_gaps": components,
        }

        issue_counts = {
            key: sum(1 for row in rows if row["status"] != "balanced")
            for key, rows in groups.items()
        }
        total_rows = sum(len(rows) for rows in groups.values())
        total_issues = sum(issue_counts.values())
        total_difference_qty = round(
            sum(
                abs(row["difference_qty"])
                for rows in groups.values()
                for row in rows
                if row["status"] != "balanced"
            ),
            3,
        )

        return {
            "total_rows": total_rows,
            "total_issues": total_issues,
            "transfer_mismatches": issue_counts["transfer_mismatches"],
            "production_shortfalls": issue_counts["production_shortfalls"],
            "component_gaps": issue_counts["component_gaps"],
            "balanced_rows": total_rows - total_issues,
            "total_difference_qty": total_difference_qty,
        }
