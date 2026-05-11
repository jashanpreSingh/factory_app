from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from .hana_reader import HanaStockDashboardReader
from .serializers import StockDashboardFilterSerializer
from .services import StockDashboardService


class StockDashboardFilterSerializerTests(SimpleTestCase):
    def test_accepts_item_group_filter(self):
        serializer = StockDashboardFilterSerializer(
            data={"item_group": "  PACKAGING MATERIAL  "}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["item_group"], "PACKAGING MATERIAL"
        )

    def test_accepts_movement_status_filter(self):
        serializer = StockDashboardFilterSerializer(
            data={"movement_status": "planned,recent"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["movement_status"], ["planned", "recent"])

    def test_rejects_invalid_movement_status_filter(self):
        serializer = StockDashboardFilterSerializer(
            data={"movement_status": "planned,stale"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("movement_status", serializer.errors)


class HanaStockDashboardReaderQueryTests(SimpleTestCase):
    def setUp(self):
        self.reader = HanaStockDashboardReader.__new__(HanaStockDashboardReader)
        self.reader.connection = SimpleNamespace(schema="SAP_SCHEMA")

    def test_stock_query_filters_by_item_group_name(self):
        query, params = self.reader._build_query(
            {"item_group": "PACKAGING MATERIAL"}
        )

        self.assertIn('"OITB" grp', query)
        self.assertIn('UPPER(IFNULL(grp."ItmsGrpNam", \'\')) = UPPER(?)', query)
        self.assertEqual(params, ["PACKAGING MATERIAL"])

    def test_stock_query_includes_movement_and_open_plan_signals(self):
        query, _ = self.reader._build_query({})

        self.assertIn('"OINM" n', query)
        self.assertIn('"OWOR" po', query)
        self.assertIn('"WOR1" c', query)
        self.assertIn('"LastConsumptionDate"', query)
        self.assertIn('"OpenPlanCount"', query)

    def test_stock_query_filters_by_movement_status(self):
        query, _ = self.reader._build_query(
            {"movement_status": ["planned", "recent"]}
        )

        self.assertIn('IFNULL(plan."OpenPlanCount", 0) > 0', query)
        self.assertIn('DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE) <= 180', query)
        self.assertNotIn("WHERE WHERE", query)

    def test_grouped_stats_query_filters_by_item_group_name(self):
        query, params = self.reader._build_grouped_stats_query(
            {"item_group": "PACKAGING MATERIAL"}
        )

        self.assertIn('"OITB" grp', query)
        self.assertIn('UPPER(IFNULL(grp."ItmsGrpNam", \'\')) = UPPER(?)', query)
        self.assertEqual(params, ["PACKAGING MATERIAL"])

    def test_grouped_stats_query_filters_by_movement_status(self):
        query, _ = self.reader._build_grouped_stats_query(
            {"movement_status": ["slow"]}
        )

        self.assertIn("days_since_last_consumption", query)
        self.assertIn("has_open_plan", query)
        self.assertIn("days_since_last_consumption > 180", query)
        self.assertNotIn("WHERE WHERE", query)


class StockDashboardServiceTests(SimpleTestCase):
    def make_service(self, reader):
        service = StockDashboardService.__new__(StockDashboardService)
        service.reader = reader
        return service

    def test_meta_cards_use_filtered_stats_for_ungrouped_table(self):
        reader = Mock()
        reader.get_warehouses.return_value = ["BH-PM"]
        reader.get_stock_stats.return_value = {
            "total_items": 12,
            "healthy_count": 4,
            "low_count": 3,
            "critical_count": 5,
        }
        reader.get_stock_levels.return_value = [
            {
                "item_code": "PM0001",
                "item_name": "Bottle",
                "warehouse": "BH-PM",
                "on_hand": 10,
                "min_stock": 20,
                "uom": "PCS",
            }
        ]
        service = self.make_service(reader)
        filters = {"item_group": "PACKAGING MATERIAL", "page": 1, "page_size": 50}

        result = service.get_stock_levels(filters)

        reader.get_stock_stats.assert_called_once_with(filters)
        self.assertEqual(result["meta"]["total_items"], 12)
        self.assertEqual(result["meta"]["healthy_count"], 4)
        self.assertEqual(result["meta"]["low_stock_count"], 3)
        self.assertEqual(result["meta"]["critical_stock_count"], 5)

    def test_meta_cards_use_grouped_stats_for_multi_warehouse_table(self):
        reader = Mock()
        reader.get_warehouses.return_value = ["BH-PM", "GP-FG"]
        reader.get_grouped_stock_stats.return_value = {
            "total_items": 7,
            "healthy_count": 2,
            "low_count": 1,
            "critical_count": 4,
        }
        reader.get_grouped_stock_levels.return_value = [
            {
                "item_code": "PM0001",
                "item_name": "Bottle",
                "on_hand": 10,
                "min_stock": 20,
                "uom": "PCS",
                "warehouse_count": 2,
                "critical_warehouses": 1,
                "low_warehouses": 0,
            }
        ]
        service = self.make_service(reader)
        filters = {
            "warehouse": ["BH-PM", "GP-FG"],
            "item_group": "PACKAGING MATERIAL",
            "page": 1,
            "page_size": 50,
        }

        result = service.get_stock_levels(filters)

        reader.get_grouped_stock_stats.assert_called_once_with(filters)
        reader.get_stock_stats.assert_not_called()
        self.assertEqual(result["meta"]["total_items"], 7)
        self.assertEqual(result["meta"]["healthy_count"], 2)
        self.assertEqual(result["meta"]["low_stock_count"], 1)
        self.assertEqual(result["meta"]["critical_stock_count"], 4)

    def test_movement_status_prefers_open_plan(self):
        service = self.make_service(Mock())

        status = service._movement_status(
            {"has_open_plan": True, "days_since_last_consumption": 999}
        )

        self.assertEqual(status, "planned")

    def test_movement_status_marks_recent_consumption_active(self):
        service = self.make_service(Mock())

        status = service._movement_status(
            {"has_open_plan": False, "days_since_last_consumption": 30}
        )

        self.assertEqual(status, "recent")

    def test_movement_status_marks_no_recent_consumption_slow(self):
        service = self.make_service(Mock())

        status = service._movement_status(
            {"has_open_plan": False, "days_since_last_consumption": 181}
        )

        self.assertEqual(status, "slow")
