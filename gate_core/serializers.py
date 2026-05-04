from rest_framework import serializers
from .models import (
    EmptyVehicleGateOut,
    GateAttachment,
    RejectedQCReturnEntry,
    RejectedQCReturnItem,
    UnitChoice,
)

class UnitChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitChoice
        fields = ['id', 'name']


class GateAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateAttachment
        fields = ['id', 'file', 'uploaded_at']


class EmptyVehicleEligibleEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    entry_no = serializers.CharField()
    entry_type = serializers.CharField()
    status = serializers.CharField()
    entry_time = serializers.DateTimeField()
    vehicle_id = serializers.IntegerField(source="vehicle.id")
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number")
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", allow_null=True)
    driver_id = serializers.IntegerField(source="driver.id")
    driver_name = serializers.CharField(source="driver.name")
    driver_mobile = serializers.CharField(source="driver.mobile_no")
    remarks = serializers.CharField()


class EmptyVehicleGateOutSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_type = serializers.CharField(source="vehicle_entry.entry_type", read_only=True)
    vehicle_entry_time = serializers.DateTimeField(source="vehicle_entry.entry_time", read_only=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)

    class Meta:
        model = EmptyVehicleGateOut
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_type", "vehicle_entry_time", "vehicle", "vehicle_number",
            "driver", "driver_name", "driver_mobile", "gate_out_date", "out_time",
            "security_name", "remarks", "status", "created_at", "updated_at",
        ]
        read_only_fields = fields


class EmptyVehicleGateOutCreateSerializer(serializers.Serializer):
    vehicle_entry_id = serializers.IntegerField()
    gate_out_date = serializers.DateField()
    out_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class RejectedQCReturnItemSerializer(serializers.ModelSerializer):
    inspection_id = serializers.IntegerField(source="inspection.id", read_only=True)

    class Meta:
        model = RejectedQCReturnItem
        fields = [
            "id", "inspection_id", "gate_entry_no", "report_no",
            "internal_lot_no", "item_name", "supplier_name",
            "quantity", "uom",
        ]
        read_only_fields = fields


class RejectedQCReturnEntrySerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    items = RejectedQCReturnItemSerializer(many=True, read_only=True)

    class Meta:
        model = RejectedQCReturnEntry
        fields = [
            "id", "entry_no", "company", "vehicle", "vehicle_number",
            "driver", "driver_name", "driver_mobile", "gate_out_date",
            "out_time", "challan_no", "eway_bill_no", "manual_sap_reference",
            "security_name", "remarks", "status", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "entry_no", "company", "vehicle_number", "driver_name",
            "driver_mobile", "status", "items", "created_at", "updated_at",
        ]


class RejectedQCReturnCreateSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()
    gate_out_date = serializers.DateField()
    out_time = serializers.TimeField(required=False, allow_null=True)
    challan_no = serializers.CharField(required=False, allow_blank=True, default="")
    eway_bill_no = serializers.CharField(required=False, allow_blank=True, default="")
    manual_sap_reference = serializers.CharField(required=False, allow_blank=True, default="")
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    inspection_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
    )
