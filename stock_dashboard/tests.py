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

    def test_accepts_planned_qty_sort(self):
        serializer = StockDashboardFilterSerializer(data={"sort_by": "planned_qty"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["sort_by"], "planned_qty")

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
        self.assertIn('"OpenPlanQty"', query)
        self.assertIn('AS "PlannedQty"', query)

    def test_stock_movement_is_item_level_not_selected_warehouse_level(self):
        query, _ = self.reader._build_query({"warehouse": ["BH-BS", "BH-PM"]})

        self.assertIn('GROUP BY n."ItemCode"', query)
        self.assertNotIn('GROUP BY n."ItemCode", n."Warehouse"', query)
        self.assertNotIn('mov."Warehouse" = w."WhsCode"', query)

    def test_stock_query_filters_by_movement_status(self):
        query, _ = self.reader._build_query(
            {"movement_status": ["planned", "recent"]}
        )

        self.assertIn('IFNULL(plan."OpenPlanCount", 0) > 0', query)
        self.assertIn('DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE) <= 30', query)
        self.assertNotIn("WHERE WHERE", query)

    def test_stock_query_sorts_by_planned_qty(self):
        query, _ = self.reader._build_query({"sort_by": "planned_qty"})

        self.assertIn('ORDER BY IFNULL(plan."OpenPlanQty", 0) ASC', query)

    def test_single_status_filter_excludes_slow_moving_rows(self):
        query, _ = self.reader._build_query({"status": ["healthy"]})

        self.assertIn('NOT (IFNULL(plan."OpenPlanCount", 0) = 0', query)
        self.assertIn('mov."LastConsumptionDate" IS NULL', query)
        self.assertIn('DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE) > 30', query)
        self.assertNotIn('OR (IFNULL(plan."OpenPlanCount", 0) = 0', query)

    def test_default_operational_status_filter_keeps_benchmarked_no_status_slow_rows(self):
        query, _ = self.reader._build_query({"status": ["healthy", "low", "critical"]})

        self.assertIn(
            'OR ((w."MinStock" + IFNULL(plan."OpenPlanQty", 0)) > 0 AND '
            'IFNULL(plan."OpenPlanCount", 0) = 0 AND '
            '(mov."LastConsumptionDate" IS NULL OR '
            'DAYS_BETWEEN(mov."LastConsumptionDate", CURRENT_DATE) > 30))',
            query,
        )

    def test_critical_status_uses_required_quantity(self):
        query, _ = self.reader._build_query({"status": ["critical"]})

        self.assertIn(
            'w."OnHand" < (w."MinStock" + IFNULL(plan."OpenPlanQty", 0)) * 0.6',
            query,
        )
        self.assertNotIn('w."MinStock" = 0 AND IFNULL(plan."OpenPlanCount", 0) > 0', query)

    def test_unset_status_requires_no_benchmark_or_planned_qty(self):
        query, _ = self.reader._build_query({"status": ["unset"]})

        self.assertIn(
            '(w."MinStock" + IFNULL(plan."OpenPlanQty", 0)) = 0',
            query,
        )

    def test_stock_stats_count_statuses_by_required_quantity(self):
        query, _ = self.reader._build_stats_query({})

        self.assertIn(
            'w."OnHand" >= (w."MinStock" + IFNULL(plan."OpenPlanQty", 0))',
            query,
        )
        self.assertIn(
            'w."OnHand" < (w."MinStock" + IFNULL(plan."OpenPlanQty", 0)) * 0.6',
            query,
        )
        self.assertIn('AND NOT (IFNULL(plan."OpenPlanCount", 0) = 0', query)

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
        self.assertIn("days_since_last_consumption > 30", query)
        self.assertNotIn("WHERE WHERE", query)

    def test_grouped_critical_status_uses_required_quantity(self):
        query, _ = self.reader._build_grouped_query({"status": ["critical"]})

        self.assertIn("on_hand < (min_stock + planned_qty) * 0.6", query)
        self.assertIn("AS planned_without_benchmark", query)
        self.assertIn("NOT (IFNULL(has_open_plan, 0) = 0", query)

    def test_grouped_default_operational_status_filter_keeps_benchmarked_no_status_slow_rows(self):
        query, _ = self.reader._build_grouped_query(
            {"status": ["healthy", "low", "critical"]}
        )

        self.assertIn(
            "OR ((min_stock + planned_qty) > 0 AND IFNULL(has_open_plan, 0) = 0 AND "
            "(days_since_last_consumption IS NULL OR "
            "days_since_last_consumption > 30))",
            query,
        )

    def test_grouped_query_sorts_by_planned_qty(self):
        query, _ = self.reader._build_grouped_query({"sort_by": "planned_qty"})

        self.assertIn("SUM(IFNULL(plan.\"OpenPlanQty\", 0)) AS planned_qty", query)
        self.assertIn("ORDER BY planned_qty ASC", query)

    def test_row_mapper_includes_planned_qty(self):
        row = (
            "PM0001",
            "Bottle",
            "BH-PM",
            10,
            20,
            "PCS",
            None,
            None,
            1,
            125.5,
        )

        mapped = self.reader._map_row(row)

        self.assertEqual(mapped["planned_qty"], 125.5)
        self.assertTrue(mapped["has_open_plan"])

    def test_grouped_row_mapper_includes_planned_qty(self):
        row = (
            "PM0001",
            "Bottle",
            10,
            20,
            "PCS",
            2,
            1,
            0,
            None,
            None,
            1,
            0,
            250,
        )

        mapped = self.reader._map_grouped_row(row)

        self.assertEqual(mapped["planned_qty"], 250.0)
        self.assertTrue(mapped["has_open_plan"])


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

    def test_uncovered_planned_item_without_benchmark_is_critical(self):
        service = self.make_service(Mock())

        status = service._stock_status(0, 0, planned_qty=1, has_open_plan=True)

        self.assertEqual(status, "critical")

    def test_unplanned_item_without_benchmark_is_unset(self):
        service = self.make_service(Mock())

        status = service._stock_status(0, 0, has_open_plan=False)

        self.assertEqual(status, "unset")

    def test_grouped_planned_without_benchmark_can_be_healthy_when_covered(self):
        service = self.make_service(Mock())

        status = service._stock_status(
            100,
            0,
            planned_qty=10,
            has_open_plan=True,
            planned_without_benchmark=True,
        )

        self.assertEqual(status, "healthy")

    def test_health_ratio_includes_planned_quantity(self):
        service = self.make_service(Mock())

        ratio = service._health_ratio({"on_hand": 75, "min_stock": 50, "planned_qty": 50})

        self.assertEqual(ratio, 0.75)

    def test_slow_moving_item_has_no_stock_status(self):
        service = self.make_service(Mock())

        status = service._stock_status(
            0,
            100,
            has_open_plan=False,
            movement_status="slow",
        )

        self.assertEqual(status, "none")

    def test_slow_moving_healthy_item_has_no_stock_status(self):
        service = self.make_service(Mock())

        status = service._stock_status(
            200,
            100,
            has_open_plan=False,
            movement_status="slow",
        )

        self.assertEqual(status, "none")

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
            {"has_open_plan": False, "days_since_last_consumption": 31}
        )

        self.assertEqual(status, "slow")
