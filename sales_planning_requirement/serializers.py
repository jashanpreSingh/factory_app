from rest_framework import serializers


class SalesPlanningRequirementReportFilterSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    status = serializers.ChoiceField(
        required=False,
        choices=["all", "shortage", "po_covered"],
        default="all",
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=200, default=50)

    def validate(self, attrs):
        if attrs.get("status") == "all":
            attrs.pop("status", None)
        return attrs


class SalesPlanningRequirementRefreshSerializer(serializers.Serializer):
    forecast_id = serializers.IntegerField(required=False, min_value=1)
    forecast_name = serializers.CharField(required=False, allow_blank=False, trim_whitespace=True)

    def validate(self, attrs):
        if attrs.get("forecast_id") and attrs.get("forecast_name"):
            raise serializers.ValidationError(
                "Use either forecast_id or forecast_name, not both."
            )
        return attrs
