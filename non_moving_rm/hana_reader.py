"""
non_moving_rm/hana_reader.py

Executes SAP HANA queries for the Non-Moving Raw Material Dashboard.
Reads company-scoped stock movement data directly from SAP B1 tables.
"""

import logging
from typing import Dict, List

from hdbcli import dbapi

from sap_client.hana.connection import HanaConnection
from sap_client.exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)


COMPANY_BRANCH_LABELS = {
    "JIVO_OIL": "OIL",
    "JIVO_MART": "MART",
    "JIVO_BEVERAGES": "BEV",
}


class HanaNonMovingRMReader:
    """
    Reads non-moving raw material data from SAP HANA.

    Provides two queries:
      1. get_non_moving_report() - reads stock, item, warehouse, and movement tables
      2. get_item_groups()       - reads item groups from OITB for dropdown
    """

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)
        company_code = getattr(context, "company_code", "")
        self.company_code = company_code if isinstance(company_code, str) else ""

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

    def get_non_moving_report(self, age: int, item_group: int) -> List[Dict]:
        """
        Builds the non-moving report from the selected company's SAP schema.

        Args:
            age: Number of days since last movement (e.g. 45)
            item_group: Item group code from OITB (e.g. 105), or 0 for all

        Returns:
            List of dicts with non-moving item details.
        """
        query, params = self._build_report_query(age=age, item_group=item_group)
        rows = self._execute(query, params)
        return [self._map_report_row(r) for r in rows]

    def _build_report_query(self, age: int, item_group: int):
        schema = self.connection.schema
        item_group_filter = ""
        params = []

        if item_group:
            item_group_filter = 'AND T0."ItmsGrpCod" = ?'
            params.append(item_group)

        params.extend([-age, self._branch_label(), age, age])

        query = f"""
WITH StockItems AS (
    SELECT
        T0."ItemCode",
        T0."ItemName",
        T0."CreateDate",
        T0."AvgPrice" AS "ItemAvgPrice",
        T0."LastPurPrc",
        COALESCE(T0."U_Sub_Group", '') AS "U_Sub_Group",
        T1."WhsCode",
        T1."OnHand",
        T1."AvgPrice" AS "WarehouseAvgPrice",
        T6."ItmsGrpNam"
    FROM "{schema}"."OITW" T1
    INNER JOIN "{schema}"."OITM" T0 ON T0."ItemCode" = T1."ItemCode"
    INNER JOIN "{schema}"."OITB" T6 ON T6."ItmsGrpCod" = T0."ItmsGrpCod"
    INNER JOIN "{schema}"."OWHS" T5 ON T5."WhsCode" = T1."WhsCode"
    WHERE T1."OnHand" > 0
      AND COALESCE(T5."Inactive", 'N') <> 'Y'
      {item_group_filter}
),
LastMovement AS (
    SELECT
        O."ItemCode",
        O."Warehouse",
        MAX(O."DocDate") AS "LastMovementDate"
    FROM "{schema}"."OINM" O
    INNER JOIN StockItems S
        ON S."ItemCode" = O."ItemCode"
       AND S."WhsCode" = O."Warehouse"
    WHERE O."TransType" <> 67
      AND (COALESCE(O."InQty", 0) <> 0 OR COALESCE(O."OutQty", 0) <> 0)
    GROUP BY O."ItemCode", O."Warehouse"
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
RecentConsumption AS (
    SELECT
        O."ItemCode",
        O."Warehouse",
        SUM(ABS(COALESCE(O."TransValue", 0))) AS "TotalConsumption"
    FROM "{schema}"."OINM" O
    INNER JOIN StockItems S
        ON S."ItemCode" = O."ItemCode"
       AND S."WhsCode" = O."Warehouse"
    WHERE O."DocDate" >= ADD_DAYS(CURRENT_DATE, ?)
      AND O."TransValue" < 0
      AND O."TransType" <> 67
    GROUP BY O."ItemCode", O."Warehouse"
)
SELECT
    ? AS "Branch",
    S."ItemCode",
    S."ItemName",
    S."ItmsGrpNam",
    S."U_Sub_Group",
    S."WhsCode" AS "Warehouse",
    S."OnHand" AS "Quantity",
    ROUND(
        S."OnHand" *
        CASE
            WHEN COALESCE(T3."CalcPrice", 0) <> 0 THEN T3."CalcPrice"
            WHEN COALESCE(S."WarehouseAvgPrice", 0) <> 0 THEN S."WarehouseAvgPrice"
            WHEN COALESCE(S."ItemAvgPrice", 0) <> 0 THEN S."ItemAvgPrice"
            ELSE COALESCE(S."LastPurPrc", 0)
        END,
        4
    ) AS "Value",
    T2."LastMovementDate",
    CASE
        WHEN T2."LastMovementDate" IS NULL AND S."CreateDate" IS NOT NULL
        THEN DAYS_BETWEEN(S."CreateDate", CURRENT_DATE)
        WHEN T2."LastMovementDate" IS NULL THEN 999999
        ELSE DAYS_BETWEEN(T2."LastMovementDate", CURRENT_DATE)
    END AS "DaysSinceLastMovement",
    ROUND(
        CASE
            WHEN COALESCE(T4."TotalConsumption", 0) > 0
            THEN (COALESCE(T4."TotalConsumption", 0) /
                  (COALESCE(S."OnHand", 0) + COALESCE(T4."TotalConsumption", 0))) * 100
            ELSE 0
        END,
        2
    ) AS "ConsumptionRatio"
FROM StockItems S
LEFT JOIN LastMovement T2
    ON T2."ItemCode" = S."ItemCode"
   AND T2."Warehouse" = S."WhsCode"
LEFT JOIN CalcPrice T3
    ON T3."ItemCode" = S."ItemCode"
   AND T3."Warehouse" = S."WhsCode"
LEFT JOIN RecentConsumption T4
    ON T4."ItemCode" = S."ItemCode"
   AND T4."Warehouse" = S."WhsCode"
WHERE (
      (
          T2."LastMovementDate" IS NULL
          AND (
              S."CreateDate" IS NULL
              OR DAYS_BETWEEN(S."CreateDate", CURRENT_DATE) >= ?
          )
      )
      OR DAYS_BETWEEN(T2."LastMovementDate", CURRENT_DATE) >= ?
  )
ORDER BY "DaysSinceLastMovement" DESC, S."ItemCode", S."WhsCode"
"""
        return query, params

    def _branch_label(self) -> str:
        return COMPANY_BRANCH_LABELS.get(
            self.company_code,
            self.company_code or self.connection.schema,
        )

    def get_item_groups(self) -> List[Dict]:
        """
        Reads all item groups from OITB table for the dropdown filter.

        Returns:
            List of dicts with ItmsGrpCod and ItmsGrpNam.
        """
        schema = self.connection.schema
        query = f'SELECT "ItmsGrpCod", "ItmsGrpNam" FROM "{schema}"."OITB" ORDER BY "ItmsGrpNam"'
        rows = self._execute(query, [])
        return [self._map_item_group_row(r) for r in rows]

    # ------------------------------------------------------------------
    # Row Mappers
    # ------------------------------------------------------------------

    def _map_report_row(self, row) -> Dict:
        return {
            "branch": row[0] or "",
            "item_code": row[1] or "",
            "item_name": row[2] or "",
            "item_group_name": row[3] or "",
            "sub_group": row[4] or "",
            "warehouse": row[5] or "",
            "quantity": float(row[6] or 0),
            "value": float(row[7] or 0),
            "last_movement_date": row[8].strftime("%Y-%m-%d %H:%M:%S") if row[8] else None,
            "days_since_last_movement": int(row[9] or 0),
            "consumption_ratio": float(row[10] or 0),
        }

    def _map_item_group_row(self, row) -> Dict:
        return {
            "item_group_code": int(row[0]),
            "item_group_name": row[1] or "",
        }

    # ------------------------------------------------------------------
    # Execution Helper
    # ------------------------------------------------------------------

    def _execute(self, query: str, params: List) -> List:
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
            logger.error(f"SAP HANA query error in non-moving RM: {e}")
            raise SAPDataError(
                "Failed to retrieve non-moving RM data from SAP. Invalid query."
            ) from e
        except dbapi.Error as e:
            logger.error(f"SAP HANA data error in non-moving RM: {e}")
            raise SAPDataError(
                "Failed to retrieve non-moving RM data from SAP. Please try again."
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
