from collections import defaultdict
from datetime import date
from typing import Any, Dict, List

from sap_client.context import CompanyContext

from .production_movement_reader import ProductionMovementReader


class ProductionFlowService:
    """Builds one-row production-order flow from planning through FG receipt."""

    def __init__(self, company_code: str):
        self.company_code = company_code
        self.context = CompanyContext(company_code)
        self.reader = ProductionMovementReader(self.context)

    def get_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        normalized_filters = self._normalize_filters(filters)
        orders = self.reader.get_production_flow_orders(normalized_filters)
        doc_entries = [order["doc_entry"] for order in orders if order["doc_entry"]]
        documents = [order["document"] for order in orders if order["document"]]
        components = self.reader.get_production_flow_components(doc_entries)
        movements = self.reader.get_production_flow_movements(documents, doc_entries)

        components_by_order = self._group_by_key(components, "doc_entry")
        movements_by_order = self._group_movements_by_order(orders, movements)
        rows = [
            self._build_flow_row(
                order,
                components_by_order.get(order["doc_entry"], []),
                movements_by_order.get(order["doc_entry"], []),
            )
            for order in orders
        ]

        status_filter = normalized_filters.get("status") or "all"
        if status_filter != "all":
            rows = [row for row in rows if row["flow_status"] == status_filter]

        return {
            "summary": self._build_summary(rows),
            "data": rows,
            "meta": {
                "date_from": normalized_filters["date_from"].isoformat(),
                "date_to": normalized_filters["date_to"].isoformat(),
                "warehouse": normalized_filters.get("warehouse") or "",
                "search": normalized_filters.get("search") or "",
                "status": normalized_filters.get("status") or "all",
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
            "status": (filters.get("status") or "all").strip() or "all",
            "limit": min(int(filters.get("limit") or 500), 1000),
        }

    def _group_by_key(
        self,
        rows: List[Dict[str, Any]],
        key: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row.get(key) or ""].append(row)
        return grouped

    def _group_movements_by_order(
        self,
        orders: List[Dict[str, Any]],
        movements: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        order_by_document = {
            order["document"]: order["doc_entry"]
            for order in orders
            if order.get("document") and order.get("doc_entry")
        }
        order_by_doc_entry = {
            order["doc_entry"]: order["doc_entry"]
            for order in orders
            if order.get("doc_entry")
        }

        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for movement in movements:
            doc_entry = order_by_doc_entry.get(movement.get("source_order_doc_entry") or "")
            if not doc_entry:
                doc_entry = order_by_document.get(movement.get("reference") or "")
            if not doc_entry:
                doc_entry = order_by_doc_entry.get(movement.get("created_by") or "")
            if doc_entry:
                grouped[doc_entry].append(movement)
        return grouped

    def _build_flow_row(
        self,
        order: Dict[str, Any],
        components: List[Dict[str, Any]],
        movements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        component_codes = {component["item_code"] for component in components}
        material_movements = [
            movement
            for movement in movements
            if movement["item_code"] in component_codes
            or (movement["direction"] == "OUT" and movement["item_code"] != order["item_code"])
        ]
        finished_good_movements = [
            movement for movement in movements if movement["item_code"] == order["item_code"]
        ]

        material_movement_out_qty = round(
            sum(movement["out_qty"] for movement in material_movements),
            3,
        )
        fg_received_qty = round(
            sum(movement["in_qty"] for movement in finished_good_movements),
            3,
        )
        fg_moved_qty = round(
            sum(movement["out_qty"] for movement in finished_good_movements),
            3,
        )
        production_gap_qty = self._clean_qty(order["remaining_qty"])
        material_gap_qty = self._clean_qty(order["component_gap_qty"])
        fg_gap_qty = self._clean_qty(order["completed_qty"] - fg_received_qty)
        flow_status = self._get_flow_status(
            order=order,
            material_gap_qty=material_gap_qty,
            production_gap_qty=production_gap_qty,
            fg_gap_qty=fg_gap_qty,
        )

        return {
            **order,
            "components": components,
            "material_movements": material_movements,
            "finished_good_movements": finished_good_movements,
            "movement_entries": movements,
            "material_warehouse_codes": self._unique_values(
                component["warehouse"] for component in components
            ),
            "fg_warehouse_codes": self._unique_values(
                movement["warehouse"]
                for movement in finished_good_movements
                if movement["in_qty"] > 0
            )
            or ([order["warehouse"]] if order["warehouse"] else []),
            "material_movement_out_qty": material_movement_out_qty,
            "fg_received_qty": fg_received_qty,
            "fg_moved_qty": fg_moved_qty,
            "material_gap_qty": material_gap_qty,
            "production_gap_qty": production_gap_qty,
            "fg_gap_qty": fg_gap_qty,
            "flow_status": flow_status,
            "movement_count": len(movements),
        }

    def _get_flow_status(
        self,
        order: Dict[str, Any],
        material_gap_qty: float,
        production_gap_qty: float,
        fg_gap_qty: float,
    ) -> str:
        if order["component_issued_qty"] <= 0 and order["completed_qty"] <= 0:
            return "not_started"
        if material_gap_qty > 0:
            return "material_pending"
        if production_gap_qty > 0:
            return "production_pending"
        if fg_gap_qty > 0:
            return "fg_pending"
        return "complete"

    def _build_summary(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "total_orders": len(rows),
            "planned_qty": self._sum(rows, "planned_qty"),
            "completed_qty": self._sum(rows, "completed_qty"),
            "rejected_qty": self._sum(rows, "rejected_qty"),
            "remaining_qty": self._sum(rows, "production_gap_qty"),
            "component_gap_qty": self._sum(rows, "material_gap_qty"),
            "fg_gap_qty": self._sum(rows, "fg_gap_qty"),
            "not_started": self._count(rows, "not_started"),
            "material_pending": self._count(rows, "material_pending"),
            "production_pending": self._count(rows, "production_pending"),
            "fg_pending": self._count(rows, "fg_pending"),
            "complete": self._count(rows, "complete"),
        }

    def _sum(self, rows: List[Dict[str, Any]], key: str) -> float:
        return round(sum(float(row.get(key) or 0) for row in rows), 3)

    def _count(self, rows: List[Dict[str, Any]], status: str) -> int:
        return sum(1 for row in rows if row.get("flow_status") == status)

    def _clean_qty(self, value: float) -> float:
        rounded = round(float(value or 0), 3)
        return 0.0 if abs(rounded) < 0.001 else rounded

    def _unique_values(self, values) -> List[str]:
        seen = set()
        result = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
