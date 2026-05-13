"""
inventory_age/tests.py

Unit tests for the Inventory Age dashboard backend.
"""

from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase


def _make_inventory_age_row(
    *,
    item_code="PM0001",
    item_name="Carton",
    is_litre="N",
    item_group="PACKAGING MATERIAL",
    unit="PCS",
    variety="",
    sku="",
    sub_group="CARTON",
    warehouse="BH-PM",
    on_hand=100.0,
    litres=0.0,
    in_stock_value=2500.0,
    calc_price=25.0,
    effective_date=date(2026, 1, 1),
    days_age=131,
):
    return (
        item_code,
        item_name,
        is_litre,
        item_group,
        unit,
        variety,
        sku,
        sub_group,
        warehouse,
        on_hand,
        litres,
        in_stock_value,
        calc_price,
        effective_date,
        days_age,
    )


class TestHanaInventoryAgeReader(TestCase):
    def setUp(self):
        from inventory_age.hana_reader import HanaInventoryAgeReader

        context = MagicMock()
        context.hana = {
            "host": "localhost",
            "port": 30015,
            "user": "u",
            "password": "p",
            "schema": "TEST",
        }
        with patch("inventory_age.hana_reader.HanaConnection"):
            self.reader = HanaInventoryAgeReader(context)
            self.reader.connection.schema = "TEST"

    def test_map_row_basic_fields(self):
        result = self.reader._map_row(_make_inventory_age_row())

        self.assertEqual(result["item_code"], "PM0001")
        self.assertEqual(result["item_name"], "Carton")
        self.assertFalse(result["is_litre"])
        self.assertEqual(result["item_group"], "PACKAGING MATERIAL")
        self.assertEqual(result["warehouse"], "BH-PM")
        self.assertEqual(result["days_age"], 131)

    def test_map_row_litre_item(self):
        result = self.reader._map_row(_make_inventory_age_row(is_litre="Y", litres=50.0))

        self.assertTrue(result["is_litre"])
        self.assertEqual(result["litres"], 50.0)

    def test_build_query_uses_company_schema_not_stored_procedure(self):
        query, params = self.reader._build_inventory_age_query(
            {
                "item_group": "PACKAGING MATERIAL",
                "search": "carton",
                "min_age": 90,
            }
        )

        self.assertIn('"TEST"."OITW"', query)
        self.assertIn('"TEST"."OITM"', query)
        self.assertIn('"TEST"."OITB"', query)
        self.assertIn('"TEST"."OINM"', query)
        self.assertIn("InboundCumulative", query)
        self.assertNotIn("SP_INVENTORYAGEVALUE", query)
        self.assertEqual(params, ["PACKAGING MATERIAL", "%CARTON%", "%CARTON%", 90])

    def test_build_query_all_material_types_has_no_group_filter(self):
        query, params = self.reader._build_inventory_age_query({})

        self.assertNotIn('T6."ItmsGrpNam" = ?', query)
        self.assertEqual(params, [])


class TestInventoryAgeService(TestCase):
    def _make_service(self):
        from inventory_age.services import InventoryAgeService

        with patch("inventory_age.services.CompanyContext"), \
             patch("inventory_age.services.HanaInventoryAgeReader"):
            service = InventoryAgeService.__new__(InventoryAgeService)
            service.company_code = "JIVO_OIL"
            service.reader = MagicMock()
            return service

    def test_get_inventory_age_passes_filters_to_reader_and_summarizes(self):
        service = self._make_service()
        filters = {"item_group": "PACKAGING MATERIAL", "min_age": 90}
        service.reader.get_inventory_age.return_value = [
            {
                "item_code": "PM1",
                "item_name": "Carton",
                "item_group": "PACKAGING MATERIAL",
                "warehouse": "BH-PM",
                "sub_group": "CARTON",
                "variety": "",
                "on_hand": 100.0,
                "litres": 0.0,
                "in_stock_value": 2500.0,
                "days_age": 120,
            },
            {
                "item_code": "PM2",
                "item_name": "Label",
                "item_group": "PACKAGING MATERIAL",
                "warehouse": "BH-PM",
                "sub_group": "LABEL",
                "variety": "",
                "on_hand": 50.0,
                "litres": 0.0,
                "in_stock_value": 500.0,
                "days_age": 91,
            },
        ]

        result = service.get_inventory_age(filters)

        service.reader.get_inventory_age.assert_called_once_with(filters)
        self.assertEqual(result["meta"]["total_items"], 2)
        self.assertEqual(result["meta"]["total_value"], 3000.0)
        self.assertEqual(result["meta"]["total_quantity"], 150.0)
        self.assertEqual(result["warehouse_summary"][0]["warehouse"], "BH-PM")
