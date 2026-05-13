"""
stock_dashboard/hana_reader.py

Executes SAP HANA SQL queries for the Stock Dashboard.
Reads from SAP B1 HANA tables: OITW (Item Warehouses), OITM (Item Master).
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from hdbcli import dbapi

from sap_client.hana.connection import HanaConnection
from sap_client.exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)

SLOW_MOVING_DAYS = 30


class HanaStockDashboardReader:
    """
    Reads stock level data directly from SAP HANA.

    Returns items with current OnHand quantities, warehouse code, and
    inventory UOM. Pagination is handled via LIMIT/OFFSET.
    """

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    # Transaction types that represent real outbound usage/demand, not stock transfers.
    _CONSUMPTION_TRANS_TYPES = (15, 60, 202)  # Delivery, Goods Issue, Production Order

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

    def get_stock_levels(self, filters: Dict[str, Any], page: int = 1, page_size: int = 50) -> List[Dict]:
        """Returns one page of item-warehouse rows, ordered by warehouse then item code."""
        query, params = self._build_query(filters)
        offset = (page - 1) * page_size
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        rows = self._execute(paginated_query, params + [page_size, offset])
        return [self._map_row(r) for r in rows]

    def get_warehouses(self) -> List[str]:
        """Returns sorted list of distinct warehouse codes present in OITW."""
        schema = self.connection.schema
        query = f"""
            SELECT DISTINCT w."WhsCode"
            FROM "{schema}"."OITW" w
            ORDER BY w."WhsCode" ASC
        """
        rows = self._execute(query, [])
        return [r[0] for r in rows if r[0]]

    def get_stock_stats(self, filters: Dict[str, Any]) -> Dict:
        """Returns total, healthy, low, and critical counts across the full filtered dataset."""
        query, params = self._build_stats_query(filters)
        rows = self._execute(query, params)
        row = rows[0] if rows else (0, 0, 0, 0)
        return {
            "total_items": int(row[0] or 0),
            "healthy_count": int(row[1] or 0),
            "low_count": int(row[2] or 0),
            "critical_count": int(row[3] or 0),
        }

    # ------------------------------------------------------------------
    # Query Builders
    # ------------------------------------------------------------------

    # Maps each status to its SQL condition based on the health thresholds.
    # Slow-moving rows are excluded from all stock health statuses.
    _UNGROUPED_HAS_PLAN_SQL = 'IFNULL(plan."OpenPlanCount", 0) > 0'
    _UNGROUPED_NO_PLAN_SQL = 'IFNULL(plan."OpenPlanCount", 0) = 0'
    _UNGROUPED_DAYS_SQL = 'DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)'
    _UNGROUPED_SLOW_SQL = (
        f'{_UNGROUPED_NO_PLAN_SQL} AND '
        f'(mov."LastConsumptionDate" IS NULL OR {_UNGROUPED_DAYS_SQL} > {SLOW_MOVING_DAYS})'
    )
    _UNGROUPED_NOT_SLOW_SQL = f'NOT ({_UNGROUPED_SLOW_SQL})'
    _UNGROUPED_SLOW_OPERATIONAL_SQL = f'w."MinStock" > 0 AND {_UNGROUPED_SLOW_SQL}'
    _STATUS_SQL = {
        "unset":    f'w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) = 0 AND {_UNGROUPED_NOT_SLOW_SQL}',
        "healthy":  f'w."MinStock" > 0 AND w."OnHand" >= w."MinStock" AND {_UNGROUPED_NOT_SLOW_SQL}',
        "low":      f'w."MinStock" > 0 AND w."OnHand" < w."MinStock" AND w."OnHand" >= w."MinStock" * 0.6 AND {_UNGROUPED_NOT_SLOW_SQL}',
        "critical": f'((w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0) OR (w."MinStock" > 0 AND w."OnHand" < w."MinStock" * 0.6 AND {_UNGROUPED_NOT_SLOW_SQL}))',
    }

    # Status conditions for aggregated (grouped) queries - uses SUM aliases.
    _GROUPED_HAS_PLAN_SQL = "has_open_plan > 0"
    _GROUPED_NO_PLAN_SQL = "IFNULL(has_open_plan, 0) = 0"
    _GROUPED_DAYS_SQL = "days_since_last_consumption"
    _GROUPED_SLOW_SQL = (
        f"{_GROUPED_NO_PLAN_SQL} AND "
        f"({_GROUPED_DAYS_SQL} IS NULL OR {_GROUPED_DAYS_SQL} > {SLOW_MOVING_DAYS})"
    )
    _GROUPED_NOT_SLOW_SQL = f"NOT ({_GROUPED_SLOW_SQL})"
    _GROUPED_SLOW_OPERATIONAL_SQL = f"min_stock > 0 AND {_GROUPED_SLOW_SQL}"

    _GROUPED_STATUS_SQL = {
        "unset":    f"min_stock = 0 AND planned_without_benchmark = 0 AND {_GROUPED_NOT_SLOW_SQL}",
        "healthy":  f"planned_without_benchmark = 0 AND min_stock > 0 AND on_hand >= min_stock AND {_GROUPED_NOT_SLOW_SQL}",
        "low":      f"planned_without_benchmark = 0 AND min_stock > 0 AND on_hand < min_stock AND on_hand >= min_stock * 0.6 AND {_GROUPED_NOT_SLOW_SQL}",
        "critical": f"planned_without_benchmark > 0 OR (min_stock > 0 AND on_hand < min_stock * 0.6 AND {_GROUPED_NOT_SLOW_SQL})",
    }
    _DEFAULT_OPERATIONAL_STATUSES = {"healthy", "low", "critical"}

    # Maps frontend sort column names to SQL expressions
    _SORT_COL_SQL = {
        "item_code":    'w."ItemCode"',
        "item_name":    'm."ItemName"',
        "warehouse":    'w."WhsCode"',
        "on_hand":      'w."OnHand"',
        "min_stock":    'w."MinStock"',
        # health_ratio is computed, so we use the ratio expression directly
        "health_ratio": 'CASE WHEN w."MinStock" > 0 THEN w."OnHand" / w."MinStock" ELSE 0 END',
    }

    # For grouped queries the aliases are different
    _SORT_COL_GROUPED = {
        "item_code":    "item_code",
        "item_name":    "item_name",
        "warehouse":    "warehouse_count",
        "on_hand":      "on_hand",
        "min_stock":    "min_stock",
        "health_ratio": "CASE WHEN min_stock > 0 THEN on_hand / min_stock ELSE 0 END",
    }

    def _build_order_by(self, filters: Dict[str, Any], grouped: bool = False) -> str:
        col = filters.get("sort_by", "health_ratio")
        direction = filters.get("sort_dir", "asc").upper()
        col_map = self._SORT_COL_GROUPED if grouped else self._SORT_COL_SQL
        sql_col = col_map.get(col, col_map["health_ratio"])
        return f"ORDER BY {sql_col} {direction}"

    def _movement_joins(self, schema: str) -> str:
        consumption_types = ", ".join(str(t) for t in self._CONSUMPTION_TRANS_TYPES)
        return f"""
            LEFT JOIN (
                SELECT
                    n."ItemCode",
                    MAX(n."DocDate") AS "LastConsumptionDate"
                FROM "{schema}"."OINM" n
                WHERE n."OutQty" > 0
                  AND n."TransType" IN ({consumption_types})
                GROUP BY n."ItemCode"
            ) mov
                ON mov."ItemCode" = w."ItemCode"
            LEFT JOIN (
                SELECT
                    c."ItemCode",
                    IFNULL(c."wareHouse", '') AS "WhsCode",
                    COUNT(*) AS "OpenPlanCount"
                FROM "{schema}"."OWOR" po
                JOIN "{schema}"."WOR1" c
                    ON po."DocEntry" = c."DocEntry"
                LEFT JOIN "{schema}"."OITM" cm
                    ON c."ItemCode" = cm."ItemCode"
                WHERE po."Status" IN ('P', 'R')
                  AND c."ItemType" = 4
                  AND cm."InvntItem" = 'Y'
                  AND (IFNULL(c."PlannedQty", 0) - IFNULL(c."IssuedQty", 0)) > 0
                GROUP BY c."ItemCode", IFNULL(c."wareHouse", '')
            ) plan
                ON plan."ItemCode" = w."ItemCode"
                AND plan."WhsCode" = w."WhsCode"
        """

    def _build_base_where(self, filters: Dict[str, Any]) -> Tuple[List[str], List]:
        """Base WHERE clauses for warehouse, item group, and search (no status)."""
        clauses = []
        params = []

        warehouse_list = filters.get("warehouse", [])
        if warehouse_list:
            placeholders = ", ".join("?" for _ in warehouse_list)
            clauses.append(f'w."WhsCode" IN ({placeholders})')
            params.extend(warehouse_list)

        item_group = (filters.get("item_group") or "").strip()
        if item_group:
            clauses.append('UPPER(IFNULL(grp."ItmsGrpNam", \'\')) = UPPER(?)')
            params.append(item_group)

        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            clauses.append(
                '(w."ItemCode" LIKE ? OR m."ItemName" LIKE ? OR w."WhsCode" LIKE ?)'
            )
            params.extend([search_term, search_term, search_term])

        return clauses, params

    def _build_where(self, filters: Dict[str, Any]) -> Tuple[str, List]:
        """Full WHERE clause including stock and movement filters."""
        clauses, params = self._build_base_where(filters)

        status_list = filters.get("status", [])
        if status_list:
            conditions = [f'({self._STATUS_SQL[s]})' for s in status_list if s in self._STATUS_SQL]
            if self._includes_default_operational_statuses(status_list):
                conditions.append(f'({self._UNGROUPED_SLOW_OPERATIONAL_SQL})')
            if conditions:
                clauses.append(f'({" OR ".join(conditions)})')

        movement_clause = self._movement_where_clause(filters, grouped=False)
        if movement_clause:
            clauses.append(movement_clause)

        where = f'WHERE {" AND ".join(clauses)}' if clauses else ''
        return where, params

    def _post_group_where_clause(self, filters: Dict[str, Any]) -> str:
        """Builds filters that apply after grouped aggregation."""
        clauses = []
        status_list = filters.get("status", [])
        if status_list:
            conditions = [
                f"({self._GROUPED_STATUS_SQL[s]})"
                for s in status_list
                if s in self._GROUPED_STATUS_SQL
            ]
            if self._includes_default_operational_statuses(status_list):
                conditions.append(f"({self._GROUPED_SLOW_OPERATIONAL_SQL})")
            if conditions:
                clauses.append(f'({" OR ".join(conditions)})')

        movement_clause = self._movement_where_clause(filters, grouped=True)
        if movement_clause:
            clauses.append(movement_clause)

        return f'WHERE {" AND ".join(clauses)}' if clauses else ""

    def _movement_where_clause(self, filters: Dict[str, Any], grouped: bool) -> str:
        """Builds a movement-status filter matching the service display labels."""
        movement_statuses = filters.get("movement_status", [])
        if not movement_statuses:
            return ""

        if grouped:
            has_plan = "has_open_plan > 0"
            no_plan = "IFNULL(has_open_plan, 0) = 0"
            days = "days_since_last_consumption"
        else:
            has_plan = 'IFNULL(plan."OpenPlanCount", 0) > 0'
            no_plan = 'IFNULL(plan."OpenPlanCount", 0) = 0'
            days = 'DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)'

        sql_map = {
            "planned": has_plan,
            "recent": (
                f'{no_plan} AND {days} IS NOT NULL '
                f'AND {days} <= {SLOW_MOVING_DAYS}'
            ),
            "slow": (
                f'{no_plan} AND '
                f'( {days} IS NULL OR {days} > {SLOW_MOVING_DAYS} )'
            ),
        }
        conditions = [f"({sql_map[s]})" for s in movement_statuses if s in sql_map]
        return f'({" OR ".join(conditions)})' if conditions else ""

    @classmethod
    def _includes_default_operational_statuses(cls, status_list: List[str]) -> bool:
        return set(status_list) == cls._DEFAULT_OPERATIONAL_STATUSES

    def _build_query(self, filters: Dict[str, Any]) -> Tuple[str, List]:
        schema = self.connection.schema
        where, params = self._build_where(filters)
        order_by = self._build_order_by(filters)

        query = f"""
            SELECT
                w."ItemCode",
                m."ItemName",
                w."WhsCode",
                w."OnHand",
                w."MinStock",
                IFNULL(m."InvntryUom", '')  AS uom,
                mov."LastConsumptionDate",
                CASE
                    WHEN mov."LastConsumptionDate" IS NULL THEN NULL
                    ELSE DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)
                END AS "DaysSinceLastConsumption",
                CASE
                    WHEN IFNULL(plan."OpenPlanCount", 0) > 0 THEN 1
                    ELSE 0
                END AS "HasOpenPlan"
            FROM "{schema}"."OITW" w
            JOIN "{schema}"."OITM" m
                ON w."ItemCode" = m."ItemCode"
            LEFT JOIN "{schema}"."OITB" grp
                ON m."ItmsGrpCod" = grp."ItmsGrpCod"
            {self._movement_joins(schema)}
            {where}
            {order_by}
        """
        return query, params

    def _build_stats_query(self, filters: Dict[str, Any]) -> Tuple[str, List]:
        """
        Counts items using the same thresholds as the service layer:
          critical: planned without benchmark, or on_hand < min_stock * 0.6
          low:      on_hand < min_stock AND on_hand >= min_stock * 0.6
        """
        schema = self.connection.schema
        where, params = self._build_where(filters)

        query = f"""
            SELECT
                COUNT(*) AS total_items,
                SUM(CASE
                    WHEN w."MinStock" > 0 AND w."OnHand" >= w."MinStock"
                         AND {self._UNGROUPED_NOT_SLOW_SQL}
                    THEN 1 ELSE 0
                END) AS healthy_count,
                SUM(CASE
                    WHEN w."MinStock" > 0 AND w."OnHand" < w."MinStock" AND w."OnHand" >= w."MinStock" * 0.6
                         AND {self._UNGROUPED_NOT_SLOW_SQL}
                    THEN 1 ELSE 0
                END) AS low_count,
                SUM(CASE
                    WHEN (w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0)
                         OR (w."MinStock" > 0 AND w."OnHand" < w."MinStock" * 0.6
                             AND {self._UNGROUPED_NOT_SLOW_SQL})
                    THEN 1 ELSE 0
                END) AS critical_count
            FROM "{schema}"."OITW" w
            JOIN "{schema}"."OITM" m
                ON w."ItemCode" = m."ItemCode"
            LEFT JOIN "{schema}"."OITB" grp
                ON m."ItmsGrpCod" = grp."ItmsGrpCod"
            {self._movement_joins(schema)}
            {where}
        """
        return query, params

    # ------------------------------------------------------------------
    # Grouped Queries (multi-warehouse)
    # ------------------------------------------------------------------

    def get_grouped_stock_levels(
        self, filters: Dict[str, Any], page: int = 1, page_size: int = 50
    ) -> List[Dict]:
        """Returns one page of item rows grouped across warehouses."""
        query, params = self._build_grouped_query(filters)
        offset = (page - 1) * page_size
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        rows = self._execute(paginated_query, params + [page_size, offset])
        return [self._map_grouped_row(r) for r in rows]

    def get_grouped_stock_stats(self, filters: Dict[str, Any]) -> Dict:
        """Stats for grouped items (multi-warehouse)."""
        query, params = self._build_grouped_stats_query(filters)
        rows = self._execute(query, params)
        row = rows[0] if rows else (0, 0, 0, 0)
        return {
            "total_items": int(row[0] or 0),
            "healthy_count": int(row[1] or 0),
            "low_count": int(row[2] or 0),
            "critical_count": int(row[3] or 0),
        }

    def get_item_warehouses(
        self, item_code: str, warehouses: List[str]
    ) -> List[Dict]:
        """Returns per-warehouse rows for a single item (expand detail)."""
        schema = self.connection.schema
        placeholders = ", ".join("?" for _ in warehouses)
        query = f"""
            SELECT
                w."ItemCode",
                m."ItemName",
                w."WhsCode",
                w."OnHand",
                w."MinStock",
                IFNULL(m."InvntryUom", '') AS uom,
                mov."LastConsumptionDate",
                CASE
                    WHEN mov."LastConsumptionDate" IS NULL THEN NULL
                    ELSE DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)
                END AS "DaysSinceLastConsumption",
                CASE
                    WHEN IFNULL(plan."OpenPlanCount", 0) > 0 THEN 1
                    ELSE 0
                END AS "HasOpenPlan"
            FROM "{schema}"."OITW" w
            JOIN "{schema}"."OITM" m
                ON w."ItemCode" = m."ItemCode"
            {self._movement_joins(schema)}
            WHERE w."ItemCode" = ? AND w."WhsCode" IN ({placeholders})
            ORDER BY w."WhsCode" ASC
        """
        rows = self._execute(query, [item_code] + warehouses)
        return [self._map_row(r) for r in rows]

    def _build_grouped_query(self, filters: Dict[str, Any]) -> Tuple[str, List]:
        schema = self.connection.schema
        base_clauses, params = self._build_base_where(filters)
        base_where = f'WHERE {" AND ".join(base_clauses)}' if base_clauses else ""
        post_group_where = self._post_group_where_clause(filters)
        order_by = self._build_order_by(filters, grouped=True)

        query = f"""
            SELECT * FROM (
                SELECT
                    w."ItemCode"    AS item_code,
                    m."ItemName"    AS item_name,
                    SUM(w."OnHand")    AS on_hand,
                    SUM(w."MinStock")  AS min_stock,
                    IFNULL(m."InvntryUom", '') AS uom,
                    COUNT(*)           AS warehouse_count,
                    SUM(CASE WHEN (w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0)
                              OR (w."MinStock" > 0 AND w."OnHand" < w."MinStock" * 0.6
                                  AND {self._UNGROUPED_NOT_SLOW_SQL})
                         THEN 1 ELSE 0 END) AS critical_wh,
                    SUM(CASE WHEN w."MinStock" > 0
                              AND w."OnHand" < w."MinStock"
                              AND w."OnHand" >= w."MinStock" * 0.6
                              AND {self._UNGROUPED_NOT_SLOW_SQL}
                         THEN 1 ELSE 0 END) AS low_wh,
                    MAX(mov."LastConsumptionDate") AS last_consumption_date,
                    MIN(CASE
                        WHEN mov."LastConsumptionDate" IS NULL THEN NULL
                        ELSE DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)
                    END) AS days_since_last_consumption,
                    MAX(CASE
                        WHEN IFNULL(plan."OpenPlanCount", 0) > 0 THEN 1
                        ELSE 0
                    END) AS has_open_plan,
                    SUM(CASE
                        WHEN w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0
                        THEN 1 ELSE 0
                    END) AS planned_without_benchmark
                FROM "{schema}"."OITW" w
                JOIN "{schema}"."OITM" m ON w."ItemCode" = m."ItemCode"
                LEFT JOIN "{schema}"."OITB" grp
                    ON m."ItmsGrpCod" = grp."ItmsGrpCod"
                {self._movement_joins(schema)}
                {base_where}
                GROUP BY w."ItemCode", m."ItemName", m."InvntryUom"
            ) g
            {post_group_where}
            {order_by}
        """
        return query, params

    def _build_grouped_stats_query(self, filters: Dict[str, Any]) -> Tuple[str, List]:
        schema = self.connection.schema
        base_clauses, params = self._build_base_where(filters)
        base_where = f'WHERE {" AND ".join(base_clauses)}' if base_clauses else ""
        post_group_where = self._post_group_where_clause(filters)

        query = f"""
            SELECT
                COUNT(*) AS total_items,
                SUM(CASE WHEN planned_without_benchmark = 0
                              AND min_stock > 0 AND on_hand >= min_stock
                              AND {self._GROUPED_NOT_SLOW_SQL}
                    THEN 1 ELSE 0 END) AS healthy_count,
                SUM(CASE WHEN planned_without_benchmark = 0
                              AND min_stock > 0 AND on_hand < min_stock
                              AND on_hand >= min_stock * 0.6
                              AND {self._GROUPED_NOT_SLOW_SQL}
                    THEN 1 ELSE 0 END) AS low_count,
                SUM(CASE WHEN planned_without_benchmark > 0
                              OR (min_stock > 0 AND on_hand < min_stock * 0.6
                                  AND {self._GROUPED_NOT_SLOW_SQL})
                    THEN 1 ELSE 0 END) AS critical_count
            FROM (
                SELECT
                    SUM(w."OnHand")   AS on_hand,
                    SUM(w."MinStock") AS min_stock,
                    MIN(CASE
                        WHEN mov."LastConsumptionDate" IS NULL THEN NULL
                        ELSE DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE)
                    END) AS days_since_last_consumption,
                    MAX(CASE
                        WHEN IFNULL(plan."OpenPlanCount", 0) > 0 THEN 1
                        ELSE 0
                    END) AS has_open_plan,
                    SUM(CASE
                        WHEN w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0
                        THEN 1 ELSE 0
                    END) AS planned_without_benchmark
                FROM "{schema}"."OITW" w
                JOIN "{schema}"."OITM" m ON w."ItemCode" = m."ItemCode"
                LEFT JOIN "{schema}"."OITB" grp
                    ON m."ItmsGrpCod" = grp."ItmsGrpCod"
                {self._movement_joins(schema)}
                {base_where}
                GROUP BY w."ItemCode"
            ) g
            {post_group_where}
        """
        return query, params

    def _map_grouped_row(self, row) -> Dict:
        return {
            "item_code": row[0] or "",
            "item_name": row[1] or "",
            "on_hand": float(row[2] or 0),
            "min_stock": float(row[3] or 0),
            "uom": row[4] or "",
            "warehouse_count": int(row[5] or 0),
            "critical_warehouses": int(row[6] or 0),
            "low_warehouses": int(row[7] or 0),
            "last_consumption_date": self._format_date(row[8]),
            "days_since_last_consumption": int(row[9]) if row[9] is not None else None,
            "has_open_plan": bool(row[10]),
            "planned_without_benchmark": int(row[11] or 0),
        }

    # ------------------------------------------------------------------
    # Row Mapper
    # ------------------------------------------------------------------

    def _map_row(self, row) -> Dict:
        on_hand = float(row[3] or 0)
        min_stock = float(row[4] or 0)

        return {
            "item_code": row[0] or "",
            "item_name": row[1] or "",
            "warehouse": row[2] or "",
            "on_hand": on_hand,
            "min_stock": min_stock,
            "uom": row[5] or "",
            "last_consumption_date": self._format_date(row[6]),
            "days_since_last_consumption": int(row[7]) if row[7] is not None else None,
            "has_open_plan": bool(row[8]),
        }

    @staticmethod
    def _format_date(value) -> Optional[str]:
        if not value:
            return None
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)[:10]

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
            logger.error(f"SAP HANA query error in stock dashboard: {e}")
            raise SAPDataError(
                "Failed to retrieve stock dashboard data from SAP. Invalid query."
            ) from e
        except dbapi.Error as e:
            logger.error(f"SAP HANA data error in stock dashboard: {e}")
            raise SAPDataError(
                "Failed to retrieve stock dashboard data from SAP. Please try again."
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
