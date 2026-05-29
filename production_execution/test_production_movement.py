from datetime import date
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from production_execution.serializers import ProductionMovementFilterSerializer
from production_execution.services.production_movement_reader import ProductionMovementReader
from production_execution.services.production_movement_service import ProductionMovementService


def _movement(**overrides):
    row = {
        "date": "2026-05-21",
        "item_code": "PM0000817",
        "item_name": "PREFORM 21/23 GMS",
        "item_group": "PACKAGING MATERIAL",
        "warehouse": "BH-PM",
        "warehouse_name": "BH Production Material",
        "in_qty": 100.0,
        "out_qty": 0.0,
        "quantity": 100.0,
        "direction": "IN",
        "transaction_value": 2500.0,
        "abs_value": 2500.0,
        "transaction_type": 59,
        "transaction_label": "Goods Receipt",
        "reference": "123",
        "doc_num": "456",
        "created_by": "1",
    }
    row.update(overrides)
    return row


class ProductionMovementFilterSerializerTests(SimpleTestCase):
    def test_accepts_comma_separated_transaction_types(self):
        serializer = ProductionMovementFilterSerializer(
            data={"transaction_type": "59, 60", "direction": "in"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["transaction_type"], "59,60")

    def test_rejects_invalid_date_range(self):
        serializer = ProductionMovementFilterSerializer(
            data={"date_from": "2026-05-21", "date_to": "2026-05-01"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class ProductionMovementReaderTests(SimpleTestCase):
    def test_build_query_scopes_to_production_warehouses_by_default(self):
        reader = ProductionMovementReader.__new__(ProductionMovementReader)
        reader.connection = type("Connection", (), {"schema": "TEST_SCHEMA"})()

        query, params = reader._build_movements_query(
            {
                "date_from": date(2026, 5, 1),
                "date_to": date(2026, 5, 21),
                "warehouse": "BH-PM",
                "direction": "out",
                "transaction_types": [60, 202],
                "search": "PM0000817",
                "limit": 25,
                "production_only": True,
            }
        )

        self.assertIn('SELECT TOP 25', query)
        self.assertIn('INNER JOIN ProductionWarehouses P', query)
        self.assertIn('LEFT JOIN "TEST_SCHEMA"."WTR1" T', query)
        self.assertIn('T."LineNum" = O."DocLineNum"', query)
        self.assertIn('O."Warehouse" = ?', query)
        self.assertIn('COALESCE(O."OutQty", 0) > 0', query)
        self.assertIn('O."TransType" IN (?, ?)', query)
        self.assertEqual(
            params[:5],
            [date(2026, 5, 1), date(2026, 5, 21), "BH-PM", 60, 202],
        )

    def test_build_query_can_include_all_warehouses(self):
        reader = ProductionMovementReader.__new__(ProductionMovementReader)
        reader.connection = type("Connection", (), {"schema": "TEST_SCHEMA"})()

        query, _ = reader._build_movements_query(
            {"limit": 10, "production_only": False}
        )

        self.assertNotIn('INNER JOIN ProductionWarehouses P', query)

    def test_map_movement_row_includes_transfer_warehouses(self):
        reader = ProductionMovementReader.__new__(ProductionMovementReader)
        row = [
            date(2026, 5, 21),
            "FG000001",
            "Finished Item",
            "Finished Goods",
            "BH-BS",
            "Bhakharpur Basement",
            0,
            25,
            -1000,
            67,
            "12345",
            999,
            55,
            "BH-BS",
            "Bhakharpur Basement",
            "BH-PC",
            "Bhakharpur Production Consumption",
        ]

        result = reader._map_movement_row(row)

        self.assertEqual(result["from_warehouse"], "BH-BS")
        self.assertEqual(result["from_warehouse_name"], "Bhakharpur Basement")
        self.assertEqual(result["to_warehouse"], "BH-PC")
        self.assertEqual(result["to_warehouse_name"], "Bhakharpur Production Consumption")

    def test_build_stock_balance_query_uses_date_boundaries_and_warehouse(self):
        reader = ProductionMovementReader.__new__(ProductionMovementReader)
        reader.connection = type("Connection", (), {"schema": "TEST_SCHEMA"})()

        query, params = reader._build_stock_balances_query(
            {
                "date_from": date(2026, 5, 21),
                "date_to": date(2026, 5, 21),
                "warehouse": "BH-PC",
                "production_only": True,
            }
        )

        self.assertIn('O."DocDate" < ?', query)
        self.assertIn('O."DocDate" <= ?', query)
        self.assertIn('INNER JOIN ProductionWarehouses P', query)
        self.assertIn('O."Warehouse" = ?', query)
        self.assertEqual(
            params,
            [date(2026, 5, 21), date(2026, 5, 21), date(2026, 5, 21), "BH-PC"],
        )


class ProductionMovementServiceTests(SimpleTestCase):
    def test_report_summarizes_in_and_out_movements(self):
        service = ProductionMovementService.__new__(ProductionMovementService)
        service.reader = MagicMock()
        service.reader.get_stock_balances.return_value = {
            "opening_qty": 500.0,
            "closing_qty": 585.0,
        }
        service.reader.get_movements.return_value = [
            _movement(),
            _movement(
                warehouse="BH-PM",
                in_qty=0.0,
                out_qty=40.0,
                quantity=40.0,
                direction="OUT",
                transaction_value=-1000.0,
                abs_value=1000.0,
                transaction_type=60,
                transaction_label="Goods Issue",
            ),
            _movement(warehouse="GP-PM", warehouse_name="GP Production", in_qty=25.0, quantity=25.0),
        ]

        result = service.get_report(
            {
                "date_from": date(2026, 5, 1),
                "date_to": date(2026, 5, 21),
                "limit": 100,
            }
        )

        self.assertEqual(result["summary"]["total_entries"], 3)
        self.assertEqual(result["summary"]["inward_entries"], 2)
        self.assertEqual(result["summary"]["outward_entries"], 1)
        self.assertEqual(result["summary"]["opening_qty"], 500.0)
        self.assertEqual(result["summary"]["total_in_qty"], 125.0)
        self.assertEqual(result["summary"]["total_out_qty"], 40.0)
        self.assertEqual(result["summary"]["net_qty"], 85.0)
        self.assertEqual(result["summary"]["closing_qty"], 585.0)
        self.assertEqual(result["summary"]["total_value"], 6000.0)
        self.assertEqual(result["summary"]["warehouse_count"], 2)
        self.assertEqual(result["warehouse_summary"][0]["warehouse"], "BH-PM")
        self.assertEqual(result["movement_type_summary"][0]["transaction_type"], 59)
