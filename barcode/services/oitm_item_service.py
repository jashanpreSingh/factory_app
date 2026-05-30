import logging
from decimal import Decimal, InvalidOperation

from sap_client.client import SAPClient

logger = logging.getLogger(__name__)


class OitmItemReadError(Exception):
    pass


class OitmItemService:
    """Read active inventory items from SAP HANA OITM for barcode label generation."""

    TABLE_NAME = 'OITM'
    FINISHED_GOODS_ITEM_GROUP_CODE = 102

    def __init__(self, company_code: str):
        self.client = SAPClient(company_code=company_code)

    def list_items(self, search: str = '', limit: int = 100) -> list[dict]:
        try:
            limit = int(limit or 100)
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 200))

        schema = self.client.context.config['hana']['schema']
        where_clause = """
            WHERE "InvntItem" = 'Y'
              AND "ItmsGrpCod" = {finished_goods_item_group_code}
              AND "validFor" = 'Y'
              AND "frozenFor" = 'N'
        """.format(
            finished_goods_item_group_code=self.FINISHED_GOODS_ITEM_GROUP_CODE,
        )

        if search:
            safe_search = search.replace("'", "''")
            where_clause += f"""
              AND (
                LOWER("ItemCode") LIKE LOWER('%{safe_search}%')
                OR LOWER("ItemName") LIKE LOWER('%{safe_search}%')
              )
            """

        sql = """
            SELECT TOP {limit}
                "ItemCode",
                "ItemName",
                "InvntryUom",
                "SalUnitMsr",
                "BuyUnitMsr",
                "ItmsGrpCod",
                "ManBtchNum",
                "ManSerNum",
                "InvntItem",
                "SellItem",
                "PrchseItem",
                "validFor",
                "frozenFor"
            FROM "{schema}"."{table_name}"
            {where_clause}
            ORDER BY "ItemCode"
        """.format(
            limit=limit,
            schema=schema,
            table_name=self.TABLE_NAME,
            where_clause=where_clause,
        )

        try:
            return [self._normalize_row(row) for row in self._execute(sql)]
        except OitmItemReadError:
            raise
        except Exception as exc:
            logger.error('Failed to fetch OITM item rows: %s', exc)
            raise OitmItemReadError(str(exc))

    @staticmethod
    def _normalize_row(row: dict) -> dict:
        return {
            'item_code': row.get('ItemCode') or '',
            'item_name': row.get('ItemName') or '',
            'inventory_uom': row.get('InvntryUom') or '',
            'sales_uom': row.get('SalUnitMsr') or '',
            'purchase_uom': row.get('BuyUnitMsr') or '',
            'item_group_code': OitmItemService._to_int(row.get('ItmsGrpCod')),
            'manage_batch_numbers': row.get('ManBtchNum') == 'Y',
            'manage_serial_numbers': row.get('ManSerNum') == 'Y',
            'is_inventory_item': row.get('InvntItem') == 'Y',
            'is_sales_item': row.get('SellItem') == 'Y',
            'is_purchase_item': row.get('PrchseItem') == 'Y',
            'valid_for': row.get('validFor') == 'Y',
            'frozen_for': row.get('frozenFor') == 'Y',
        }

    @staticmethod
    def _to_int(value) -> int | None:
        if value in (None, ''):
            return None
        try:
            return int(Decimal(str(value)))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def _execute(self, sql: str) -> list[dict]:
        try:
            conn = self.client.context.hana
            from hdbcli import dbapi

            connection = dbapi.connect(
                address=conn['host'],
                port=conn['port'],
                user=conn['user'],
                password=conn['password'],
            )
            cursor = connection.cursor()
            cursor.execute(sql)
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return [dict(zip(cols, row)) for row in rows]
        except Exception as exc:
            raise OitmItemReadError(str(exc))
