"""
inventory_age/hana_reader.py

Reads SAP HANA inventory age and valuation data for the current company schema.
"""

import logging
from typing import Any, Dict, List

from hdbcli import dbapi

from sap_client.hana.connection import HanaConnection
from sap_client.exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)


class HanaInventoryAgeReader:
    """
    Reads inventory age & value data from SAP B1 tables.

    The report returns one row per item-warehouse combination with columns:
        ItemCode, ItemName, U_IsLitre, ItemGroup, U_Unit, U_Variety,
        U_SKU, U_Sub_Group, WhsCode, OnHand, Litres, InStockValue,
        CalcPrice, EffectiveDate, DaysAge
    """

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    # ------------------------------------------------------------------
    # Public: lightweight query for dropdown options only
    # ------------------------------------------------------------------

    def get_filter_options(self) -> Dict[str, List]:
        """
        Return distinct dropdown values via lightweight SQL queries.
        Uses OITB for item groups, OITM/OITW for the rest.
        """
        schema = self.connection.schema

        # Item groups from OITB (same pattern as non_moving_rm)
        item_groups_rows = self._execute_query(
            f'SELECT "ItmsGrpCod", "ItmsGrpNam" FROM "{schema}"."OITB" ORDER BY "ItmsGrpNam"',
            [],
        )

        # Distinct warehouses, sub-groups, varieties from OITM + OITW
        distinct_rows = self._execute_query(
            f"""
            SELECT DISTINCT
                IFNULL(w."WhsCode", '')     AS "Warehouse",
                IFNULL(m."U_Sub_Group", '') AS "SubGroup",
                IFNULL(m."U_Variety", '')   AS "Variety"
            FROM "{schema}"."OITW" w
            JOIN "{schema}"."OITM" m ON w."ItemCode" = m."ItemCode"
            WHERE w."OnHand" > 0
            """,
            [],
        )

        warehouses: set[str] = set()
        sub_groups: set[str] = set()
        varieties: set[str] = set()

        for r in distinct_rows:
            if r[0]:
                warehouses.add(r[0])
            if r[1]:
                sub_groups.add(r[1])
            if r[2]:
                varieties.add(r[2])

        return {
            "item_groups": [
                {"item_group_code": r[0], "item_group_name": r[1] or ""}
                for r in item_groups_rows
            ],
            "sub_groups": sorted(sub_groups),
            "warehouses": sorted(warehouses),
            "varieties": sorted(varieties),
        }

    # ------------------------------------------------------------------
    # Public: full report
    # ------------------------------------------------------------------

    def get_inventory_age(self, filters: Dict[str, Any] | None = None) -> List[Dict]:
        """Read inventory age rows from the selected company schema."""
        query, params = self._build_inventory_age_query(filters or {})
        rows = self._execute_query(query, params)
        return [self._map_row(r) for r in rows]

    def _build_inventory_age_query(self, filters: Dict[str, Any]):
        schema = self.connection.schema
        stock_filters = []
        report_filters = []
        params: List[Any] = []

        item_group = (filters.get("item_group") or "").strip()
        search = (filters.get("search") or "").strip().upper()
        warehouse = (filters.get("warehouse") or "").strip()
        sub_group = (filters.get("sub_group") or "").strip()
        variety = (filters.get("variety") or "").strip()
        min_age = filters.get("min_age")

        if item_group:
            stock_filters.append('T6."ItmsGrpNam" = ?')
            params.append(item_group)

        if search:
            stock_filters.append('(UPPER(T0."ItemCode") LIKE ? OR UPPER(T0."ItemName") LIKE ?)')
            params.extend([f"%{search}%", f"%{search}%"])

        if warehouse:
            stock_filters.append('T1."WhsCode" = ?')
            params.append(warehouse)

        if sub_group:
            stock_filters.append('COALESCE(T0."U_Sub_Group", \'\') = ?')
            params.append(sub_group)

        if variety:
            stock_filters.append('COALESCE(T0."U_Variety", \'\') = ?')
            params.append(variety)

        if min_age is not None:
            report_filters.append('"DaysAge" >= ?')
            params.append(min_age)

        stock_filter_sql = ""
        if stock_filters:
            stock_filter_sql = "\n      AND " + "\n      AND ".join(stock_filters)

        report_filter_sql = ""
        if report_filters:
            report_filter_sql = "\nWHERE " + "\n  AND ".join(report_filters)

        query = f"""
WITH StockItems AS (
    SELECT
        T0."ItemCode",
        T0."ItemName",
        COALESCE(T0."U_IsLitre", 'N') AS "U_IsLitre",
        T6."ItmsGrpNam" AS "ItemGroup",
        COALESCE(T0."U_Unit", '') AS "U_Unit",
        COALESCE(T0."U_Variety", '') AS "U_Variety",
        COALESCE(T0."U_SKU", '') AS "U_SKU",
        COALESCE(T0."U_Sub_Group", '') AS "U_Sub_Group",
        T0."CreateDate",
        T0."AvgPrice" AS "ItemAvgPrice",
        T0."LastPurPrc",
        T1."WhsCode",
        T1."OnHand",
        T1."AvgPrice" AS "WarehouseAvgPrice"
    FROM "{schema}"."OITW" T1
    INNER JOIN "{schema}"."OITM" T0 ON T0."ItemCode" = T1."ItemCode"
    INNER JOIN "{schema}"."OITB" T6 ON T6."ItmsGrpCod" = T0."ItmsGrpCod"
    INNER JOIN "{schema}"."OWHS" T5 ON T5."WhsCode" = T1."WhsCode"
    WHERE T1."OnHand" > 0
      AND COALESCE(T5."Inactive", 'N') <> 'Y'{stock_filter_sql}
),
InboundByDate AS (
    SELECT
        O."ItemCode",
        O."Warehouse",
        O."DocDate",
        SUM(COALESCE(O."InQty", 0)) AS "InQty"
    FROM "{schema}"."OINM" O
    INNER JOIN StockItems S
        ON S."ItemCode" = O."ItemCode"
       AND S."WhsCode" = O."Warehouse"
    WHERE COALESCE(O."InQty", 0) > 0
      AND O."TransType" <> 67
    GROUP BY O."ItemCode", O."Warehouse", O."DocDate"
),
InboundCumulative AS (
    SELECT
        I."ItemCode",
        I."Warehouse",
        I."DocDate",
        I."InQty",
        SUM(I."InQty") OVER (
            PARTITION BY I."ItemCode", I."Warehouse"
            ORDER BY I."DocDate" DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS "CumulativeInQty"
    FROM InboundByDate I
),
EffectiveLayer AS (
    SELECT
        I."ItemCode",
        I."Warehouse",
        MAX(I."DocDate") AS "EffectiveDate"
    FROM InboundCumulative I
    INNER JOIN StockItems S
        ON S."ItemCode" = I."ItemCode"
       AND S."WhsCode" = I."Warehouse"
    WHERE I."CumulativeInQty" >= S."OnHand"
    GROUP BY I."ItemCode", I."Warehouse"
),
CalcPrice AS (
    SELECT
        O."ItemCode",
        O."Warehouse",
        CASE
            WHEN SUM(COALESCE(O."InQty", 0)) - SUM(COALESCE(O."OutQty", 0)) <> 0
            THEN SUM(COALESCE(O."TransValue", 0)) /
                 (SUM(COALESCE(O."InQty", 0)) - SUM(COALESCE(O."OutQty", 0)))
            ELSE 0
        END AS "CalcPrice"
    FROM "{schema}"."OINM" O
    INNER JOIN StockItems S
        ON S."ItemCode" = O."ItemCode"
       AND S."WhsCode" = O."Warehouse"
    GROUP BY O."ItemCode", O."Warehouse"
),
ReportRows AS (
    SELECT
        S."ItemCode",
        S."ItemName",
        S."U_IsLitre",
        S."ItemGroup",
        S."U_Unit",
        S."U_Variety",
        S."U_SKU",
        S."U_Sub_Group",
        S."WhsCode",
        S."OnHand",
        CASE WHEN S."U_IsLitre" = 'Y' THEN S."OnHand" ELSE 0 END AS "Litres",
        ROUND(
            S."OnHand" *
            CASE
                WHEN COALESCE(P."CalcPrice", 0) <> 0 THEN P."CalcPrice"
                WHEN COALESCE(S."WarehouseAvgPrice", 0) <> 0 THEN S."WarehouseAvgPrice"
                WHEN COALESCE(S."ItemAvgPrice", 0) <> 0 THEN S."ItemAvgPrice"
                ELSE COALESCE(S."LastPurPrc", 0)
            END,
            4
        ) AS "InStockValue",
        ROUND(
            CASE
                WHEN COALESCE(P."CalcPrice", 0) <> 0 THEN P."CalcPrice"
                WHEN COALESCE(S."WarehouseAvgPrice", 0) <> 0 THEN S."WarehouseAvgPrice"
                WHEN COALESCE(S."ItemAvgPrice", 0) <> 0 THEN S."ItemAvgPrice"
                ELSE COALESCE(S."LastPurPrc", 0)
            END,
            4
        ) AS "CalcPrice",
        COALESCE(E."EffectiveDate", S."CreateDate") AS "EffectiveDate",
        CASE
            WHEN COALESCE(E."EffectiveDate", S."CreateDate") IS NULL THEN 0
            ELSE DAYS_BETWEEN(COALESCE(E."EffectiveDate", S."CreateDate"), CURRENT_DATE)
        END AS "DaysAge"
    FROM StockItems S
    LEFT JOIN EffectiveLayer E
        ON E."ItemCode" = S."ItemCode"
       AND E."Warehouse" = S."WhsCode"
    LEFT JOIN CalcPrice P
        ON P."ItemCode" = S."ItemCode"
       AND P."Warehouse" = S."WhsCode"
)
SELECT
    "ItemCode",
    "ItemName",
    "U_IsLitre",
    "ItemGroup",
    "U_Unit",
    "U_Variety",
    "U_SKU",
    "U_Sub_Group",
    "WhsCode",
    "OnHand",
    "Litres",
    "InStockValue",
    "CalcPrice",
    "EffectiveDate",
    "DaysAge"
FROM ReportRows{report_filter_sql}
ORDER BY "DaysAge" DESC, "ItemCode", "WhsCode"
"""
        return query, params

    # ------------------------------------------------------------------
    # Row Mapper
    # ------------------------------------------------------------------

    def _map_row(self, row) -> Dict:
        return {
            "item_code": row[0] or "",
            "item_name": row[1] or "",
            "is_litre": (row[2] or "N") == "Y",
            "item_group": row[3] or "",
            "unit": row[4] or "",
            "variety": row[5] or "",
            "sku": row[6] or "",
            "sub_group": row[7] or "",
            "warehouse": row[8] or "",
            "on_hand": float(row[9] or 0),
            "litres": float(row[10] or 0),
            "in_stock_value": float(row[11] or 0),
            "calc_price": float(row[12] or 0),
            "effective_date": str(row[13]) if row[13] else None,
            "days_age": int(row[14] or 0),
        }

    # ------------------------------------------------------------------
    # Execution Helper
    # ------------------------------------------------------------------

    def _execute_query(self, query: str, params: List[Any]) -> List:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except dbapi.Error as e:
            logger.error(f"SAP HANA connection failed: {e}")
            raise SAPConnectionError(
                "Unable to connect to SAP HANA. Please try again later."
            ) from e

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

        except dbapi.ProgrammingError as e:
            logger.error(f"SAP HANA query error in inventory age: {e}")
            raise SAPDataError(
                f"Inventory age query error: {e}"
            ) from e
        except dbapi.Error as e:
            logger.error(f"SAP HANA data error in inventory age: {e}")
            raise SAPDataError(
                f"Inventory age HANA error: {e}"
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
