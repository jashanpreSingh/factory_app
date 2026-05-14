import logging
from datetime import date, time
from typing import Optional

from hdbcli import dbapi

from .connection import HanaConnection
from ..exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)


class HanaGRPOReader:
    """Read SAP Business One GRPO documents from OPDN/PDN1."""

    CRUDE_OIL_LINE_FILTER = """(
        IFNULL(T2."ItmsGrpCod", -1) = 106
        AND UPPER(TRIM(IFNULL(T2."U_Variety", ''))) = 'CRUDE'
        AND UPPER(TRIM(IFNULL(T2."U_Unit", ''))) = 'OIL'
    )"""

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    def list_grpos(
        self,
        search: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 50,
        crude_oil_only: bool = False,
    ) -> list[dict]:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except dbapi.Error as e:
            logger.error("SAP HANA connection failed while reading GRPO documents: %s", e)
            raise SAPConnectionError("Unable to connect to SAP HANA.") from e

        try:
            cursor = conn.cursor()
            schema = self.connection.schema
            safe_limit = max(1, min(int(limit or 50), 100))

            where = ['T0."CANCELED" = ?']
            params: list = ["N"]

            if from_date:
                where.append('T0."DocDate" >= ?')
                params.append(from_date)
            if to_date:
                where.append('T0."DocDate" <= ?')
                params.append(to_date)
            if crude_oil_only:
                where.append(self.CRUDE_OIL_LINE_FILTER)
            if search:
                term = f"%{search.lower()}%"
                where.append(
                    """(
                        LOWER(TO_NVARCHAR(T0."DocNum")) LIKE ?
                        OR LOWER(IFNULL(T0."CardCode", '')) LIKE ?
                        OR LOWER(IFNULL(T0."CardName", '')) LIKE ?
                        OR LOWER(IFNULL(T0."NumAtCard", '')) LIKE ?
                        OR LOWER(IFNULL(T0."Comments", '')) LIKE ?
                        OR LOWER(IFNULL(T1."ItemCode", '')) LIKE ?
                        OR LOWER(IFNULL(T1."Dscription", '')) LIKE ?
                        OR LOWER(IFNULL(T2."ItemName", '')) LIKE ?
                        OR LOWER(IFNULL(T1."WhsCode", '')) LIKE ?
                    )"""
                )
                params.extend([term, term, term, term, term, term, term, term, term])

            query = f"""
                SELECT
                    T0."DocEntry",
                    T0."DocNum",
                    T0."DocDate",
                    T0."TaxDate",
                    IFNULL(T0."DocTime", 0),
                    IFNULL(T0."DocStatus", ''),
                    IFNULL(T0."CardCode", ''),
                    IFNULL(T0."CardName", ''),
                    IFNULL(T0."NumAtCard", ''),
                    IFNULL(T0."Comments", ''),
                    T0."BPLId",
                    COUNT(T1."LineNum") AS line_count,
                    SUM(T1."Quantity") AS total_quantity
                FROM "{schema}"."OPDN" T0
                JOIN "{schema}"."PDN1" T1 ON T0."DocEntry" = T1."DocEntry"
                LEFT JOIN "{schema}"."OITM" T2 ON T1."ItemCode" = T2."ItemCode"
                WHERE {" AND ".join(where)}
                GROUP BY
                    T0."DocEntry", T0."DocNum", T0."DocDate", T0."TaxDate",
                    T0."DocTime", T0."DocStatus", T0."CardCode", T0."CardName",
                    T0."NumAtCard", T0."Comments", T0."BPLId"
                ORDER BY T0."DocDate" DESC, T0."DocTime" DESC, T0."DocNum" DESC
                LIMIT {safe_limit}
            """

            cursor.execute(query, tuple(params))
            return [self._header_from_row(row) for row in cursor.fetchall()]
        except dbapi.Error as e:
            logger.error("SAP HANA GRPO list query failed: %s", e)
            raise SAPDataError("Failed to retrieve GRPO documents from SAP.") from e
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

    def get_grpo(self, doc_entry: int, crude_oil_only: bool = False) -> Optional[dict]:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except dbapi.Error as e:
            logger.error("SAP HANA connection failed while reading GRPO document: %s", e)
            raise SAPConnectionError("Unable to connect to SAP HANA.") from e

        try:
            cursor = conn.cursor()
            schema = self.connection.schema
            line_filter = f' AND {self.CRUDE_OIL_LINE_FILTER}' if crude_oil_only else ""

            cursor.execute(
                f"""
                SELECT
                    T0."DocEntry",
                    T0."DocNum",
                    T0."DocDate",
                    T0."TaxDate",
                    IFNULL(T0."DocTime", 0),
                    IFNULL(T0."DocStatus", ''),
                    IFNULL(T0."CardCode", ''),
                    IFNULL(T0."CardName", ''),
                    IFNULL(T0."NumAtCard", ''),
                    IFNULL(T0."Comments", ''),
                    T0."BPLId",
                    COUNT(T1."LineNum") AS line_count,
                    SUM(T1."Quantity") AS total_quantity
                FROM "{schema}"."OPDN" T0
                JOIN "{schema}"."PDN1" T1 ON T0."DocEntry" = T1."DocEntry"
                LEFT JOIN "{schema}"."OITM" T2 ON T1."ItemCode" = T2."ItemCode"
                WHERE T0."DocEntry" = ? AND T0."CANCELED" = 'N'{line_filter}
                GROUP BY
                    T0."DocEntry", T0."DocNum", T0."DocDate", T0."TaxDate",
                    T0."DocTime", T0."DocStatus", T0."CardCode", T0."CardName",
                    T0."NumAtCard", T0."Comments", T0."BPLId"
                """,
                (doc_entry,),
            )
            header_row = cursor.fetchone()
            if not header_row:
                return None

            grpo = self._header_from_row(header_row)

            cursor.execute(
                f"""
                SELECT
                    T1."LineNum",
                    IFNULL(T1."ItemCode", ''),
                    IFNULL(T1."Dscription", ''),
                    T1."Quantity",
                    IFNULL(T1."unitMsr", ''),
                    IFNULL(T1."WhsCode", ''),
                    IFNULL(T1."BaseType", -1),
                    IFNULL(T1."BaseEntry", -1),
                    IFNULL(T1."BaseLine", -1)
                FROM "{schema}"."PDN1" T1
                LEFT JOIN "{schema}"."OITM" T2 ON T1."ItemCode" = T2."ItemCode"
                WHERE T1."DocEntry" = ?{line_filter}
                ORDER BY T1."LineNum"
                """,
                (doc_entry,),
            )
            grpo["lines"] = [self._line_from_row(row) for row in cursor.fetchall()]
            return grpo
        except dbapi.Error as e:
            logger.error("SAP HANA GRPO detail query failed: %s", e)
            raise SAPDataError("Failed to retrieve GRPO document from SAP.") from e
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

    @staticmethod
    def _header_from_row(row) -> dict:
        doc_date = row[2].date() if hasattr(row[2], "date") else row[2]
        tax_date = row[3].date() if hasattr(row[3], "date") else row[3]
        return {
            "doc_entry": int(row[0]),
            "doc_num": str(row[1]),
            "doc_date": doc_date,
            "tax_date": tax_date,
            "doc_time": HanaGRPOReader._sap_time_from_int(row[4]),
            "doc_status": row[5] or "",
            "supplier_code": row[6] or "",
            "supplier_name": row[7] or "",
            "reference": row[8] or "",
            "comments": row[9] or "",
            "branch_id": int(row[10]) if row[10] is not None else None,
            "line_count": int(row[11] or 0),
            "total_quantity": float(row[12] or 0),
        }

    @staticmethod
    def _sap_time_from_int(value) -> Optional[time]:
        if value in (None, "", 0):
            return None

        try:
            padded = str(int(value)).zfill(4)
        except (TypeError, ValueError):
            return None

        hour = int(padded[:-2] or "0")
        minute = int(padded[-2:])

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None

        return time(hour=hour, minute=minute)

    @staticmethod
    def _line_from_row(row) -> dict:
        base_type = int(row[6]) if row[6] is not None and int(row[6]) >= 0 else None
        base_entry = int(row[7]) if row[7] is not None and int(row[7]) >= 0 else None
        base_line = int(row[8]) if row[8] is not None and int(row[8]) >= 0 else None
        return {
            "line_num": int(row[0]),
            "item_code": row[1] or "",
            "item_name": row[2] or "",
            "quantity": float(row[3] or 0),
            "uom": row[4] or "",
            "warehouse_code": row[5] or "",
            "base_type": base_type,
            "base_entry": base_entry,
            "base_line": base_line,
        }
