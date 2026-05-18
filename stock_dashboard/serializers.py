"""
stock_dashboard/serializers.py

DRF serializers for validating query parameters and shaping API responses.
All data is read-only (no database writes), so only plain Serializer classes are used.
"""

from rest_framework import serializers


# ---------------------------------------------------------------------------
# Query Parameter Serializers (Input Validation)
# ---------------------------------------------------------------------------


class StockDashboardFilterSerializer(serializers.Serializer):
    """Validates query parameters for the stock dashboard endpoint."""

    search = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Search by item code, item name, or warehouse code",
    )
    warehouse = serializers.CharField(
        required=False,
        default="",
        help_text="Comma-separated warehouse codes to filter by (e.g. 'WH-01,BH-PM')",
    )
    item_group = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        max_length=100,
        help_text="Item group name from OITB to filter by (e.g. 'PACKAGING MATERIAL')",
    )

    def validate_warehouse(self, value):
        if not value:
            return []
        return [w.strip() for w in value.split(",") if w.strip()]

    def validate_item_group(self, value):
        return value.strip() if value else ""

    status = serializers.CharField(
        required=False,
        default="",
        help_text="Comma-separated stock health statuses to filter by (e.g. 'low,critical')",
    )

    def validate_status(self, value):
        if not value:
            return []
        allowed = {"healthy", "low", "critical", "unset"}
        statuses = [s.strip() for s in value.split(",") if s.strip()]
        invalid = set(statuses) - allowed
        if invalid:
            raise serializers.ValidationError(
                f"Invalid status values: {', '.join(invalid)}. Allowed: {', '.join(sorted(allowed))}"
            )
        return statuses

    movement_status = serializers.CharField(
        required=False,
        default="",
        help_text="Comma-separated movement statuses to filter by (planned,recent,slow)",
    )

    def validate_movement_status(self, value):
        if not value:
            return []
        allowed = {"planned", "recent", "slow"}
        statuses = [s.strip() for s in value.split(",") if s.strip()]
        invalid = set(statuses) - allowed
        if invalid:
            raise serializers.ValidationError(
                f"Invalid movement status values: {', '.join(invalid)}. Allowed: {', '.join(sorted(allowed))}"
            )
        return statuses

    sort_by = serializers.ChoiceField(
        choices=[
            "item_code",
            "item_name",
            "warehouse",
            "on_hand",
            "min_stock",
            "planned_qty",
            "health_ratio",
        ],
        default="health_ratio",
        required=False,
    )
    sort_dir = serializers.ChoiceField(
        choices=["asc", "desc"],
        default="asc",
        required=False,
    )
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=50, min_value=1, max_value=200)


# ---------------------------------------------------------------------------
# Response Serializers (Output Shape)
# ---------------------------------------------------------------------------


class StockItemSerializer(serializers.Serializer):
    """One row per item-warehouse (or grouped item when multi-warehouse)."""

    item_code = serializers.CharField()
    item_name = serializers.CharField()
    warehouse = serializers.CharField(default="")
    on_hand = serializers.FloatField()
    min_stock = serializers.FloatField()
    planned_qty = serializers.FloatField(default=0)
    uom = serializers.CharField()
    stock_status = serializers.CharField()
    health_ratio = serializers.FloatField()
    movement_status = serializers.CharField(default="slow")
    last_consumption_date = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    days_since_last_consumption = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
    )
    has_open_plan = serializers.BooleanField(default=False)
    # Grouped-only fields
    warehouse_count = serializers.IntegerField(default=1)
    has_warning = serializers.BooleanField(default=False)


class StockDashboardMetaSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    healthy_count = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    critical_stock_count = serializers.IntegerField()
    warehouses = serializers.ListField(child=serializers.CharField())
    fetched_at = serializers.CharField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()


class StockDashboardResponseSerializer(serializers.Serializer):
    data = StockItemSerializer(many=True)
    meta = StockDashboardMetaSerializer()


# ---------------------------------------------------------------------------
# Item Detail (expand) Serializers
# ---------------------------------------------------------------------------


class ItemDetailFilterSerializer(serializers.Serializer):
    warehouse = serializers.CharField(
        required=True,
        help_text="Comma-separated warehouse codes",
    )

    def validate_warehouse(self, value):
        return [w.strip() for w in value.split(",") if w.strip()]


class ItemDetailResponseSerializer(serializers.Serializer):
    data = StockItemSerializer(many=True)
