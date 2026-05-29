import logging
from typing import Any, Dict, List

from hdbcli import dbapi

from sap_client.exceptions import SAPConnectionError, SAPDataError
from sap_client.hana.connection import HanaConnection

logger = logging.getLogger(__name__)


TRANSACTION_TYPES: Dict[int, str] = {
    13: "AR Invoice",
    14: "AR Credit",
    15: "Delivery",
    16: "Return",
    18: "AP Invoice",
    19: "AP Credit",
    20: "GRPO",
    21: "Return to Vendor",
    59: "Goods Receipt",
    60: "Goods Issue",
    67: "Transfer",
    202: "Production Order",
}


class ProductionMovementReader:
    """Reads SAP inventory movements for production-related warehouses."""

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        schema = self.connection.schema
        query = f"""
WITH ProductionWarehouses AS (
    SELECT DISTINCT "Warehouse" AS "WhsCode"
    FROM "{schema}"."OWOR"
    WHERE COALESCE("Warehouse", '') <> ''
    UNION
    SELECT DISTINCT "wareHouse" AS "WhsCode"
    FROM "{schema}"."WOR1"
    WHERE COALESCE("wareHouse", '') <> ''
)
SELECT
    W."WhsCode",
    COALESCE(W."WhsName", W."WhsCode") AS "WhsName"
FROM "{schema}"."OWHS" W
INNER JOIN ProductionWarehouses P
    ON P."WhsCode" = W."WhsCode"
WHERE COALESCE(W."Inactive", 'N') <> 'Y'
ORDER BY W."WhsCode" ASC
"""
        rows = self._execute(query, [])
        return {
            "warehouses": [
                {"code": row[0] or "", "name": row[1] or row[0] or ""}
                for row in rows
            ],
            "transaction_types": [
                {"code": code, "label": label}
                for code, label in TRANSACTION_TYPES.items()
            ],
        }

    def get_all_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        schema = self.connection.schema
        query = f"""
SELECT
    W."WhsCode",
    COALESCE(W."WhsName", W."WhsCode") AS "WhsName"
FROM "{schema}"."OWHS" W
WHERE COALESCE(W."Inactive", 'N') <> 'Y'
ORDER BY W."WhsCode" ASC
"""
        rows = self._execute(query, [])
        return {
            "warehouses": [
                {"code": row[0] or "", "name": row[1] or row[0] or ""}
                for row in rows
            ],
            "transaction_types": [
                {"code": code, "label": label}
                for code, label in TRANSACTION_TYPES.items()
            ],
        }

    def get_movements(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        query, params = self._build_movements_query(filters)
        rows = self._execute(query, params)
        return [self._map_movement_row(row) for row in rows]

    def get_production_order_reconciliations(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        query, params = self._build_production_order_reconciliation_query(filters)
        rows = self._execute(query, params)
        return [self._map_production_order_row(row) for row in rows]

    def get_component_reconciliations(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        query, params = self._build_component_reconciliation_query(filters)
        rows = self._execute(query, params)
        return [self._map_component_row(row) for row in rows]

    def get_stock_balances(self, filters: Dict[str, Any]) -> Dict[str, float]:
        query, params = self._build_stock_balances_query(filters)
        rows = self._execute(query, params)
        if not rows:
            return {"opening_qty": 0.0, "closing_qty": 0.0}
        return {
            "opening_qty": round(float(rows[0][0] or 0), 3),
            "closing_qty": round(float(rows[0][1] or 0), 3),
        }

    def _build_movements_query(self, filters: Dict[str, Any]):
        schema = self.connection.schema
        clauses = [
            '(COALESCE(O."InQty", 0) <> 0 OR COALESCE(O."OutQty", 0) <> 0)'
        ]
        params: List[Any] = []

        production_only = filters.get("production_only", True)
        production_join = ""
        if production_only:
            production_join = """
INNER JOIN ProductionWarehouses P
    ON P."WhsCode" = O."Warehouse"
"""

        if filters.get("date_from"):
            clauses.append('O."DocDate" >= ?')
            params.append(filters["date_from"])

        if filters.get("date_to"):
            clauses.append('O."DocDate" <= ?')
            params.append(filters["date_to"])

        if filters.get("warehouse"):
            clauses.append('O."Warehouse" = ?')
            params.append(filters["warehouse"])

        direction = filters.get("direction")
        if direction == "in":
            clauses.append('COALESCE(O."InQty", 0) > 0')
        elif direction == "out":
            clauses.append('COALESCE(O."OutQty", 0) > 0')

        transaction_types = filters.get("transaction_types") or []
        if transaction_types:
            placeholders = ", ".join("?" for _ in transaction_types)
            clauses.append(f'O."TransType" IN ({placeholders})')
            params.extend(transaction_types)

        search = (filters.get("search") or "").strip().upper()
        if search:
            clauses.append(
                '('
                'UPPER(O."ItemCode") LIKE ? OR '
                'UPPER(COALESCE(I."ItemName", \'\')) LIKE ? OR '
                'UPPER(COALESCE(O."BASE_REF", \'\')) LIKE ? OR '
                'UPPER(O."Warehouse") LIKE ?'
                ')'
            )
            term = f"%{search}%"
            params.extend([term, term, term, term])

        where = " AND ".join(clauses)
        limit = int(filters.get("limit") or 500)

        query = f"""
WITH ProductionWarehouses AS (
    SELECT DISTINCT "Warehouse" AS "WhsCode"
    FROM "{schema}"."OWOR"
    WHERE COALESCE("Warehouse", '') <> ''
    UNION
    SELECT DISTINCT "wareHouse" AS "WhsCode"
    FROM "{schema}"."WOR1"
    WHERE COALESCE("wareHouse", '') <> ''
)
SELECT TOP {limit}
    O."DocDate",
    O."ItemCode",
    COALESCE(I."ItemName", '') AS "ItemName",
    COALESCE(G."ItmsGrpNam", '') AS "ItemGroup",
    O."Warehouse",
    COALESCE(W."WhsName", O."Warehouse") AS "WarehouseName",
    COALESCE(O."InQty", 0) AS "InQty",
    COALESCE(O."OutQty", 0) AS "OutQty",
    COALESCE(O."TransValue", 0) AS "TransValue",
    O."TransType",
    COALESCE(O."BASE_REF", '') AS "BaseRef",
    O."TransNum",
    O."CreatedBy",
    COALESCE(T."FromWhsCod", '') AS "FromWarehouse",
    COALESCE(FW."WhsName", T."FromWhsCod", '') AS "FromWarehouseName",
    COALESCE(T."WhsCode", '') AS "ToWarehouse",
    COALESCE(TW."WhsName", T."WhsCode", '') AS "ToWarehouseName"
FROM "{schema}"."OINM" O
{production_join}
LEFT JOIN "{schema}"."OITM" I
    ON I."ItemCode" = O."ItemCode"
LEFT JOIN "{schema}"."OITB" G
    ON G."ItmsGrpCod" = I."ItmsGrpCod"
LEFT JOIN "{schema}"."OWHS" W
    ON W."WhsCode" = O."Warehouse"
LEFT JOIN "{schema}"."WTR1" T
    ON O."TransType" = 67
    AND T."DocEntry" = O."CreatedBy"
    AND T."LineNum" = O."DocLineNum"
LEFT JOIN "{schema}"."OWHS" FW
    ON FW."WhsCode" = T."FromWhsCod"
LEFT JOIN "{schema}"."OWHS" TW
    ON TW."WhsCode" = T."WhsCode"
WHERE {where}
ORDER BY O."DocDate" DESC, O."TransNum" DESC
"""
        return query, params

    def _build_common_reconciliation_clauses(
        self,
        filters: Dict[str, Any],
        date_column: str,
        item_expression: str,
        name_expression: str,
        warehouse_expression: str,
        doc_expression: str,
    ):
        clauses = []
        params: List[Any] = []

        if filters.get("date_from"):
            clauses.append(f"{date_column} >= ?")
            params.append(filters["date_from"])

        if filters.get("date_to"):
            clauses.append(f"{date_column} <= ?")
            params.append(filters["date_to"])

        if filters.get("warehouse"):
            clauses.append(f"{warehouse_expression} = ?")
            params.append(filters["warehouse"])

        search = (filters.get("search") or "").strip().upper()
        if search:
            clauses.append(
                "("
                f"UPPER({item_expression}) LIKE ? OR "
                f"UPPER(COALESCE({name_expression}, '')) LIKE ? OR "
                f"UPPER(CAST({doc_expression} AS NVARCHAR)) LIKE ? OR "
                f"UPPER(COALESCE({warehouse_expression}, '')) LIKE ?"
                ")"
            )
            term = f"%{search}%"
            params.extend([term, term, term, term])

        return clauses, params

    def _build_production_order_reconciliation_query(self, filters: Dict[str, Any]):
        schema = self.connection.schema
        limit = int(filters.get("limit") or 500)
        clauses, params = self._build_common_reconciliation_clauses(
            filters,
            'O."PostDate"',
            'O."ItemCode"',
            'O."ProdName"',
            'O."Warehouse"',
            'O."DocNum"',
        )
        where = " AND ".join(clauses) if clauses else "1 = 1"

        query = f"""
SELECT TOP {limit}
    O."DocEntry",
    O."DocNum",
    O."PostDate",
    O."DueDate",
    O."ItemCode",
    COALESCE(O."ProdName", I."ItemName", '') AS "ItemName",
    O."Warehouse",
    COALESCE(W."WhsName", O."Warehouse") AS "WarehouseName",
    COALESCE(O."PlannedQty", 0) AS "PlannedQty",
    COALESCE(O."CmpltQty", 0) AS "CompletedQty",
    COALESCE(O."RjctQty", 0) AS "RejectedQty",
    COALESCE(O."Status", '') AS "Status"
FROM "{schema}"."OWOR" O
LEFT JOIN "{schema}"."OITM" I
    ON I."ItemCode" = O."ItemCode"
LEFT JOIN "{schema}"."OWHS" W
    ON W."WhsCode" = O."Warehouse"
WHERE {where}
ORDER BY O."PostDate" DESC, O."DocNum" DESC
"""
        return query, params

    def _build_component_reconciliation_query(self, filters: Dict[str, Any]):
        schema = self.connection.schema
        limit = int(filters.get("limit") or 500)
        clauses, params = self._build_common_reconciliation_clauses(
            filters,
            'O."PostDate"',
            'C."ItemCode"',
            'C."ItemName"',
            'C."wareHouse"',
            'O."DocNum"',
        )
        where = " AND ".join(clauses) if clauses else "1 = 1"

        query = f"""
SELECT TOP {limit}
    O."DocEntry",
    O."DocNum",
    O."PostDate",
    O."DueDate",
    O."ItemCode" AS "ParentItemCode",
    COALESCE(O."ProdName", P."ItemName", '') AS "ParentItemName",
    C."ItemCode",
    COALESCE(C."ItemName", I."ItemName", '') AS "ItemName",
    C."wareHouse",
    COALESCE(W."WhsName", C."wareHouse") AS "WarehouseName",
    COALESCE(C."PlannedQty", 0) AS "PlannedQty",
    COALESCE(C."IssuedQty", 0) AS "IssuedQty",
    COALESCE(O."Status", '') AS "Status"
FROM "{schema}"."WOR1" C
INNER JOIN "{schema}"."OWOR" O
    ON O."DocEntry" = C."DocEntry"
LEFT JOIN "{schema}"."OITM" I
    ON I."ItemCode" = C."ItemCode"
LEFT JOIN "{schema}"."OITM" P
    ON P."ItemCode" = O."ItemCode"
LEFT JOIN "{schema}"."OWHS" W
    ON W."WhsCode" = C."wareHouse"
WHERE {where}
ORDER BY O."PostDate" DESC, O."DocNum" DESC, C."LineNum" ASC
"""
        return query, params

    def _build_stock_balances_query(self, filters: Dict[str, Any]):
        schema = self.connection.schema
        params: List[Any] = [
            filters["date_from"],
            filters["date_to"],
            filters["date_to"],
        ]
        clauses = [
            '(COALESCE(O."InQty", 0) <> 0 OR COALESCE(O."OutQty", 0) <> 0)',
            'O."DocDate" <= ?',
        ]

        production_join = ""
        if filters.get("production_only", True):
            production_join = """
INNER JOIN ProductionWarehouses P
    ON P."WhsCode" = O."Warehouse"
"""

        if filters.get("warehouse"):
            clauses.append('O."Warehouse" = ?')
            params.append(filters["warehouse"])

        where = " AND ".join(clauses)

        query = f"""
WITH ProductionWarehouses AS (
    SELECT DISTINCT "Warehouse" AS "WhsCode"
    FROM "{schema}"."OWOR"
    WHERE COALESCE("Warehouse", '') <> ''
    UNION
    SELECT DISTINCT "wareHouse" AS "WhsCode"
    FROM "{schema}"."WOR1"
    WHERE COALESCE("wareHouse", '') <> ''
)
SELECT
    ROUND(
        COALESCE(SUM(
            CASE
                WHEN O."DocDate" < ?
                THEN COALESCE(O."InQty", 0) - COALESCE(O."OutQty", 0)
                ELSE 0
            END
        ), 0),
        3
    ) AS "OpeningQty",
    ROUND(
        COALESCE(SUM(
            CASE
                WHEN O."DocDate" <= ?
                THEN COALESCE(O."InQty", 0) - COALESCE(O."OutQty", 0)
                ELSE 0
            END
        ), 0),
        3
    ) AS "ClosingQty"
FROM "{schema}"."OINM" O
{production_join}
WHERE {where}
"""
        return query, params

    def _map_movement_row(self, row) -> Dict[str, Any]:
        in_qty = float(row[6] or 0)
        out_qty = float(row[7] or 0)
        trans_value = float(row[8] or 0)
        trans_type = int(row[9] or 0)
        direction = "IN" if in_qty > 0 else "OUT"

        return {
            "date": row[0].isoformat() if row[0] else "",
            "item_code": row[1] or "",
            "item_name": row[2] or "",
            "item_group": row[3] or "",
            "warehouse": row[4] or "",
            "warehouse_name": row[5] or row[4] or "",
            "in_qty": in_qty,
            "out_qty": out_qty,
            "quantity": in_qty if in_qty > 0 else out_qty,
            "direction": direction,
            "transaction_value": trans_value,
            "abs_value": abs(trans_value),
            "transaction_type": trans_type,
            "transaction_label": TRANSACTION_TYPES.get(
                trans_type,
                f"Other ({trans_type})",
            ),
            "reference": row[10] or "",
            "doc_num": str(row[11]) if row[11] is not None else "",
            "created_by": str(row[12]) if row[12] is not None else "",
            "from_warehouse": row[13] or "",
            "from_warehouse_name": row[14] or row[13] or "",
            "to_warehouse": row[15] or "",
            "to_warehouse_name": row[16] or row[15] or "",
        }

    def _map_production_order_row(self, row) -> Dict[str, Any]:
        planned_qty = float(row[8] or 0)
        completed_qty = float(row[9] or 0)
        rejected_qty = float(row[10] or 0)
        difference = round(planned_qty - completed_qty, 3)

        return {
            "source_type": "production_order",
            "document": str(row[1]) if row[1] is not None else "",
            "doc_entry": str(row[0]) if row[0] is not None else "",
            "date": row[2].isoformat() if row[2] else "",
            "due_date": row[3].isoformat() if row[3] else "",
            "item_code": row[4] or "",
            "item_name": row[5] or "",
            "warehouse": row[6] or "",
            "warehouse_name": row[7] or row[6] or "",
            "expected_qty": planned_qty,
            "actual_qty": completed_qty,
            "difference_qty": difference,
            "rejected_qty": rejected_qty,
            "status": row[11] or "",
        }

    def _map_component_row(self, row) -> Dict[str, Any]:
        planned_qty = float(row[10] or 0)
        issued_qty = float(row[11] or 0)
        difference = round(planned_qty - issued_qty, 3)

        return {
            "source_type": "bom_component",
            "document": str(row[1]) if row[1] is not None else "",
            "doc_entry": str(row[0]) if row[0] is not None else "",
            "date": row[2].isoformat() if row[2] else "",
            "due_date": row[3].isoformat() if row[3] else "",
            "parent_item_code": row[4] or "",
            "parent_item_name": row[5] or "",
            "item_code": row[6] or "",
            "item_name": row[7] or "",
            "warehouse": row[8] or "",
            "warehouse_name": row[9] or row[8] or "",
            "expected_qty": planned_qty,
            "actual_qty": issued_qty,
            "difference_qty": difference,
            "status": row[12] or "",
        }

    def _execute(self, query: str, params: List[Any]) -> List:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except dbapi.Error as e:
            logger.error("SAP HANA connection failed for production movements: %s", e)
            raise SAPConnectionError(
                "Unable to connect to SAP HANA. Please try again later."
            ) from e

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except dbapi.ProgrammingError as e:
            logger.error("SAP HANA query error in production movements: %s", e)
            raise SAPDataError(
                "Failed to retrieve production movement data from SAP. Invalid query."
            ) from e
        except dbapi.Error as e:
            logger.error("SAP HANA data error in production movements: %s", e)
            raise SAPDataError(
                "Failed to retrieve production movement data from SAP. Please try again."
            ) from e
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
