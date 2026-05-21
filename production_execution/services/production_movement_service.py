from collections import defaultdict
from datetime import date
from typing import Any, Dict, List

from sap_client.context import CompanyContext

from .production_movement_reader import ProductionMovementReader


class ProductionMovementService:
    """Builds the production movement dashboard response."""

    def __init__(self, company_code: str):
        self.company_code = company_code
        self.context = CompanyContext(company_code)
        self.reader = ProductionMovementReader(self.context)

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.reader.get_filter_options()

    def get_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        normalized_filters = self._normalize_filters(filters)
        movements = self.reader.get_movements(normalized_filters)
        stock_balances = self.reader.get_stock_balances(normalized_filters)

        return {
            "data": movements,
            "summary": self._build_summary(movements, stock_balances),
            "warehouse_summary": self._build_warehouse_summary(movements),
            "movement_type_summary": self._build_movement_type_summary(movements),
            "meta": {
                "date_from": normalized_filters["date_from"].isoformat(),
                "date_to": normalized_filters["date_to"].isoformat(),
                "warehouse": normalized_filters.get("warehouse") or "",
                "direction": normalized_filters.get("direction") or "all",
                "production_only": bool(normalized_filters.get("production_only", True)),
                "limit": int(normalized_filters.get("limit") or 500),
            },
        }

    def _normalize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        date_to = filters.get("date_to") or date.today()
        date_from = filters.get("date_from") or date_to

        transaction_types = []
        transaction_type = (filters.get("transaction_type") or "").strip()
        if transaction_type:
            transaction_types = [
                int(value)
                for value in transaction_type.split(",")
                if value.strip().isdigit()
            ]

        return {
            **filters,
            "date_from": date_from,
            "date_to": date_to,
            "direction": filters.get("direction") or "all",
            "transaction_types": transaction_types,
            "limit": min(int(filters.get("limit") or 500), 1000),
            "production_only": filters.get("production_only", True),
        }

    def _build_summary(
        self,
        rows: List[Dict[str, Any]],
        stock_balances: Dict[str, float],
    ) -> Dict[str, Any]:
        total_in_qty = sum(row["in_qty"] for row in rows)
        total_out_qty = sum(row["out_qty"] for row in rows)
        total_value = sum(row["abs_value"] for row in rows)
        net_value = sum(row["transaction_value"] for row in rows)

        return {
            "total_entries": len(rows),
            "inward_entries": sum(1 for row in rows if row["direction"] == "IN"),
            "outward_entries": sum(1 for row in rows if row["direction"] == "OUT"),
            "opening_qty": round(stock_balances.get("opening_qty", 0.0), 3),
            "total_in_qty": round(total_in_qty, 3),
            "total_out_qty": round(total_out_qty, 3),
            "net_qty": round(total_in_qty - total_out_qty, 3),
            "closing_qty": round(stock_balances.get("closing_qty", 0.0), 3),
            "total_value": round(total_value, 2),
            "net_value": round(net_value, 2),
            "warehouse_count": len({row["warehouse"] for row in rows if row["warehouse"]}),
        }

    def _build_warehouse_summary(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            warehouse = row["warehouse"]
            if warehouse not in buckets:
                buckets[warehouse] = {
                    "warehouse": warehouse,
                    "warehouse_name": row["warehouse_name"],
                    "entry_count": 0,
                    "in_qty": 0.0,
                    "out_qty": 0.0,
                    "net_qty": 0.0,
                    "total_value": 0.0,
                }
            bucket = buckets[warehouse]
            bucket["entry_count"] += 1
            bucket["in_qty"] += row["in_qty"]
            bucket["out_qty"] += row["out_qty"]
            bucket["total_value"] += row["abs_value"]

        summary = sorted(
            buckets.values(),
            key=lambda item: item["total_value"],
            reverse=True,
        )
        for row in summary:
            row["in_qty"] = round(row["in_qty"], 3)
            row["out_qty"] = round(row["out_qty"], 3)
            row["net_qty"] = round(row["in_qty"] - row["out_qty"], 3)
            row["total_value"] = round(row["total_value"], 2)
        return summary

    def _build_movement_type_summary(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[int, Dict[str, Any]] = defaultdict(
            lambda: {
                "transaction_type": 0,
                "transaction_label": "",
                "entry_count": 0,
                "in_qty": 0.0,
                "out_qty": 0.0,
                "total_value": 0.0,
            }
        )

        for row in rows:
            bucket = buckets[row["transaction_type"]]
            bucket["transaction_type"] = row["transaction_type"]
            bucket["transaction_label"] = row["transaction_label"]
            bucket["entry_count"] += 1
            bucket["in_qty"] += row["in_qty"]
            bucket["out_qty"] += row["out_qty"]
            bucket["total_value"] += row["abs_value"]

        summary = sorted(
            buckets.values(),
            key=lambda item: item["total_value"],
            reverse=True,
        )
        for row in summary:
            row["in_qty"] = round(row["in_qty"], 3)
            row["out_qty"] = round(row["out_qty"], 3)
            row["total_value"] = round(row["total_value"], 2)
        return summary
