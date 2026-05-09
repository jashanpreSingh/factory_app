from decimal import Decimal, InvalidOperation

from rest_framework import serializers
from .models import (
    BSTGateIn,
    BSTGateInItem,
    BSTGateOut,
    BSTGateOutItem,
    BSTGateReturn,
    DispatchGateLock,
    DispatchGateOut,
    DispatchGateOutLine,
    DispatchGateOutStatus,
    DispatchPhysicalUOM,
    EmptyVehicleGateIn,
    EmptyVehicleGateInItem,
    EmptyVehicleGateOut,
    GateAttachment,
    JobWorkGateIn,
    JobWorkGateInItem,
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


class SAPStockTransferLineSerializer(serializers.Serializer):
    line_num = serializers.IntegerField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    quantity = serializers.FloatField()
    uom = serializers.CharField()
    from_warehouse = serializers.CharField()
    to_warehouse = serializers.CharField()


class SAPStockTransferSerializer(serializers.Serializer):
    doc_entry = serializers.IntegerField()
    doc_num = serializers.CharField()
    doc_date = serializers.DateField(allow_null=True)
    tax_date = serializers.DateField(allow_null=True)
    doc_status = serializers.CharField()
    from_warehouse = serializers.CharField()
    to_warehouse = serializers.CharField()
    comments = serializers.CharField(allow_blank=True)
    reference = serializers.CharField(allow_blank=True)
    branch_id = serializers.IntegerField(allow_null=True)
    line_count = serializers.IntegerField()
    total_quantity = serializers.FloatField()
    lines = SAPStockTransferLineSerializer(many=True, required=False)


class SAPGRPOLineSerializer(serializers.Serializer):
    line_num = serializers.IntegerField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    quantity = serializers.FloatField()
    uom = serializers.CharField()
    warehouse_code = serializers.CharField()
    base_type = serializers.IntegerField(allow_null=True)
    base_entry = serializers.IntegerField(allow_null=True)
    base_line = serializers.IntegerField(allow_null=True)


class SAPGRPOSerializer(serializers.Serializer):
    doc_entry = serializers.IntegerField()
    doc_num = serializers.CharField()
    doc_date = serializers.DateField(allow_null=True)
    doc_time = serializers.TimeField(allow_null=True)
    tax_date = serializers.DateField(allow_null=True)
    doc_status = serializers.CharField()
    supplier_code = serializers.CharField()
    supplier_name = serializers.CharField()
    reference = serializers.CharField(allow_blank=True)
    comments = serializers.CharField(allow_blank=True)
    branch_id = serializers.IntegerField(allow_null=True)
    line_count = serializers.IntegerField()
    total_quantity = serializers.FloatField()
    lines = SAPGRPOLineSerializer(many=True, required=False)


class SAPProductionOrderComponentSerializer(serializers.Serializer):
    line_num = serializers.IntegerField()
    item_code = serializers.CharField(allow_blank=True)
    item_name = serializers.CharField(allow_blank=True)
    planned_qty = serializers.FloatField()
    issued_qty = serializers.FloatField()
    warehouse = serializers.CharField(allow_blank=True, allow_null=True)
    uom = serializers.CharField(allow_blank=True, allow_null=True)


class SAPProductionOrderSerializer(serializers.Serializer):
    doc_entry = serializers.IntegerField()
    doc_num = serializers.CharField()
    item_code = serializers.CharField(allow_blank=True)
    item_name = serializers.CharField(allow_blank=True)
    planned_qty = serializers.FloatField()
    completed_qty = serializers.FloatField()
    rejected_qty = serializers.FloatField()
    remaining_qty = serializers.FloatField()
    start_date = serializers.DateField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    warehouse = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField(allow_blank=True)
    components = SAPProductionOrderComponentSerializer(many=True, required=False)


class DispatchGateOutLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispatchGateOutLine
        fields = [
            "id", "line_num", "item_code", "item_name", "order_qty",
            "dispatched_qty", "uom", "warehouse",
        ]
        read_only_fields = fields


class DispatchGateOutSerializer(serializers.ModelSerializer):
    dispatch_plan_id = serializers.IntegerField(read_only=True, allow_null=True)
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True, allow_null=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True, allow_null=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    weight_variance = serializers.DecimalField(max_digits=18, decimal_places=3, read_only=True, allow_null=True)
    qr_payload = serializers.CharField(read_only=True)
    items = DispatchGateOutLineSerializer(many=True, read_only=True)

    class Meta:
        model = DispatchGateOut
        fields = [
            "id", "entry_no", "company", "dispatch_plan", "dispatch_plan_id",
            "vehicle_entry", "vehicle_entry_no", "vehicle_entry_status",
            "vehicle", "vehicle_number", "vehicle_type", "transporter_name",
            "driver", "driver_name", "driver_mobile", "sap_invoice_doc_entry",
            "sap_invoice_doc_num", "customer_code", "customer_name",
            "ship_to_address", "invoice_amount", "sap_weight",
            "gate_out_date", "out_time", "security_name", "seal_no",
            "pgi_document_no", "goods_issue_posted", "invoice_checked",
            "delivery_note_checked", "eway_bill_checked", "lr_checked",
            "physical_quantity", "physical_uom", "gross_weight", "tare_weight",
            "net_weight", "weight_variance", "weighbridge_slip_no",
            "first_weighment_time", "second_weighment_time", "dock_photo",
            "gatepass_document", "attachment_notes", "remarks", "gatepass_no",
            "gatepass_code", "gate_printed", "print_commit", "printed_at",
            "committed_at", "qr_payload", "status", "cancel_reason",
            "cancelled_at", "rejected_reason", "rejected_at", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class DispatchGateOutCreateSerializer(serializers.Serializer):
    sap_invoice_doc_entry = serializers.IntegerField()
    sap_invoice_doc_num = serializers.CharField(required=False, allow_blank=True, default="")
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()
    linked_vehicle_entry_id = serializers.IntegerField(required=False, allow_null=True)
    customer_code = serializers.CharField(required=False, allow_blank=True, default="")
    customer_name = serializers.CharField(required=False, allow_blank=True, default="")
    ship_to_address = serializers.CharField(required=False, allow_blank=True, default="")
    invoice_amount = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    sap_weight = serializers.DecimalField(max_digits=18, decimal_places=3, required=False, allow_null=True)
    gate_out_date = serializers.DateField()
    out_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    seal_no = serializers.CharField(required=False, allow_blank=True, default="")
    pgi_document_no = serializers.CharField(required=False, allow_blank=True, default="")
    goods_issue_posted = serializers.BooleanField(required=False, default=False)
    invoice_checked = serializers.BooleanField(required=False, default=False)
    delivery_note_checked = serializers.BooleanField(required=False, default=False)
    eway_bill_checked = serializers.BooleanField(required=False, default=False)
    lr_checked = serializers.BooleanField(required=False, default=False)
    physical_quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    physical_uom = serializers.ChoiceField(choices=DispatchPhysicalUOM.choices)
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        default=list,
    )

    def validate_physical_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Physical quantity must be greater than zero.")
        return value


class DispatchGateOutUpdateSerializer(serializers.Serializer):
    gate_out_date = serializers.DateField(required=False)
    out_time = serializers.TimeField(required=False)
    security_name = serializers.CharField(required=False, allow_blank=True)
    seal_no = serializers.CharField(required=False, allow_blank=True)
    pgi_document_no = serializers.CharField(required=False, allow_blank=True)
    goods_issue_posted = serializers.BooleanField(required=False)
    invoice_checked = serializers.BooleanField(required=False)
    delivery_note_checked = serializers.BooleanField(required=False)
    eway_bill_checked = serializers.BooleanField(required=False)
    lr_checked = serializers.BooleanField(required=False)
    physical_quantity = serializers.DecimalField(max_digits=18, decimal_places=3, required=False, allow_null=True)
    physical_uom = serializers.ChoiceField(choices=DispatchPhysicalUOM.choices, required=False, allow_blank=True)
    gross_weight = serializers.DecimalField(max_digits=18, decimal_places=3, required=False, allow_null=True)
    tare_weight = serializers.DecimalField(max_digits=18, decimal_places=3, required=False, allow_null=True)
    weighbridge_slip_no = serializers.CharField(required=False, allow_blank=True)
    first_weighment_time = serializers.DateTimeField(required=False, allow_null=True)
    second_weighment_time = serializers.DateTimeField(required=False, allow_null=True)
    attachment_notes = serializers.CharField(required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if "physical_quantity" in attrs and attrs["physical_quantity"] is not None and attrs["physical_quantity"] <= 0:
            raise serializers.ValidationError({"physical_quantity": "Physical quantity must be greater than zero."})

        gross_weight = attrs.get("gross_weight")
        tare_weight = attrs.get("tare_weight")
        if gross_weight is not None and gross_weight < 0:
            raise serializers.ValidationError({"gross_weight": "Gross weight cannot be negative."})
        if tare_weight is not None and tare_weight < 0:
            raise serializers.ValidationError({"tare_weight": "Tare weight cannot be negative."})
        if gross_weight is not None and tare_weight is not None and tare_weight > gross_weight:
            raise serializers.ValidationError({"tare_weight": "Tare weight cannot be greater than gross weight."})
        return attrs


class DispatchGateOutAttachmentSerializer(serializers.Serializer):
    dock_photo = serializers.FileField(required=False, allow_empty_file=False)
    gatepass_document = serializers.FileField(required=False, allow_empty_file=False)
    attachment_notes = serializers.CharField(required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class DispatchGateOutActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class DispatchGateLockSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DispatchGateLock
        fields = [
            "id", "company", "locked", "reason", "locked_at",
            "unlocked_at", "changed_by", "changed_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return ""
        return getattr(obj.changed_by, "full_name", "") or getattr(obj.changed_by, "email", "")


class DispatchGateLockUpdateSerializer(serializers.Serializer):
    locked = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True, default="")


def parse_dispatch_line_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise serializers.ValidationError("Enter a valid quantity.")


class BSTGateOutItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BSTGateOutItem
        fields = [
            "id", "line_num", "item_code", "item_name", "quantity",
            "actual_quantity", "uom", "from_warehouse", "to_warehouse",
        ]
        read_only_fields = fields


class BSTGateInItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BSTGateInItem
        fields = [
            "id", "line_num", "item_code", "item_name", "quantity",
            "actual_quantity", "receiving_quantity", "uom",
            "from_warehouse", "to_warehouse",
        ]
        read_only_fields = fields


class BSTGateOutSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True)
    empty_vehicle_gate_in_entry_no = serializers.CharField(
        source="empty_vehicle_gate_in.entry_no",
        read_only=True,
    )
    empty_vehicle_gate_in_date = serializers.DateField(
        source="empty_vehicle_gate_in.gate_in_date",
        read_only=True,
    )
    empty_vehicle_in_time = serializers.TimeField(
        source="empty_vehicle_gate_in.in_time",
        read_only=True,
    )
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    items = BSTGateOutItemSerializer(many=True, read_only=True)

    class Meta:
        model = BSTGateOut
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_status", "empty_vehicle_gate_in",
            "empty_vehicle_gate_in_entry_no", "empty_vehicle_gate_in_date",
            "empty_vehicle_in_time", "vehicle", "vehicle_number", "vehicle_type",
            "transporter_name", "driver", "driver_name", "driver_mobile",
            "sap_doc_entry", "sap_doc_num", "sap_doc_date", "sap_from_warehouse",
            "sap_to_warehouse", "sap_reference", "sap_comments", "gate_out_date",
            "out_time", "security_name", "remarks", "status", "cancel_reason",
            "cancelled_at", "cancelled_by", "items", "created_at", "updated_at",
        ]
        read_only_fields = fields


class BSTGateOutCreateSerializer(serializers.Serializer):
    empty_vehicle_gate_in_id = serializers.IntegerField()
    sap_doc_entry = serializers.IntegerField()
    gate_out_date = serializers.DateField()
    out_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class BSTGateOutCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class JobWorkGateInItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobWorkGateInItem
        fields = [
            "id", "line_num", "item_code", "item_name", "quantity",
            "uom", "warehouse_code", "base_type", "base_entry", "base_line",
        ]
        read_only_fields = fields


class JobWorkGateInSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    items = JobWorkGateInItemSerializer(many=True, read_only=True)

    class Meta:
        model = JobWorkGateIn
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_status", "vehicle", "vehicle_number", "vehicle_type",
            "transporter_name", "driver", "driver_name", "driver_mobile",
            "sap_doc_entry", "sap_doc_num", "sap_doc_date", "sap_doc_time",
            "sap_supplier_code", "sap_supplier_name", "sap_reference",
            "sap_comments", "sap_branch_id", "production_order_doc_entry",
            "production_order_doc_num", "production_item_code",
            "production_item_name", "production_planned_qty",
            "production_completed_qty", "production_rejected_qty",
            "production_remaining_qty", "production_start_date",
            "production_due_date", "production_warehouse",
            "production_status", "gate_in_date", "in_time", "security_name",
            "remarks", "status", "items", "created_at", "updated_at",
        ]
        read_only_fields = fields


class JobWorkGateInCreateSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()
    sap_doc_entry = serializers.IntegerField(required=False, allow_null=True)
    production_order_doc_entry = serializers.IntegerField(required=False, allow_null=True)
    gate_in_date = serializers.DateField()
    in_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class BSTGateInSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True)
    bst_gate_out_entry_no = serializers.CharField(source="bst_gate_out.entry_no", read_only=True)
    bst_gate_out_vehicle_entry = serializers.IntegerField(
        source="bst_gate_out.vehicle_entry_id",
        read_only=True,
    )
    bst_gate_out_date = serializers.DateField(source="bst_gate_out.gate_out_date", read_only=True)
    bst_gate_out_time = serializers.TimeField(source="bst_gate_out.out_time", read_only=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    sap_doc_entry = serializers.IntegerField(source="bst_gate_out.sap_doc_entry", read_only=True)
    sap_doc_num = serializers.CharField(source="bst_gate_out.sap_doc_num", read_only=True)
    sap_doc_date = serializers.DateField(source="bst_gate_out.sap_doc_date", read_only=True)
    sap_from_warehouse = serializers.CharField(source="bst_gate_out.sap_from_warehouse", read_only=True)
    sap_to_warehouse = serializers.CharField(source="bst_gate_out.sap_to_warehouse", read_only=True)
    sap_reference = serializers.CharField(source="bst_gate_out.sap_reference", read_only=True)
    sap_comments = serializers.CharField(source="bst_gate_out.sap_comments", read_only=True)
    items = BSTGateInItemSerializer(many=True, read_only=True)

    class Meta:
        model = BSTGateIn
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_status", "bst_gate_out", "bst_gate_out_entry_no",
            "bst_gate_out_vehicle_entry", "bst_gate_out_date", "bst_gate_out_time",
            "vehicle", "vehicle_number", "vehicle_type", "transporter_name",
            "driver", "driver_name", "driver_mobile", "sap_doc_entry",
            "sap_doc_num", "sap_doc_date", "sap_from_warehouse",
            "sap_to_warehouse", "sap_reference", "sap_comments", "gate_in_date",
            "in_time", "security_name", "remarks", "status", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class BSTGateInCreateSerializer(serializers.Serializer):
    bst_gate_out_id = serializers.IntegerField()
    gate_in_date = serializers.DateField()
    in_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        default=list,
    )


class BSTGateReturnSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True)
    bst_gate_out_entry_no = serializers.CharField(source="bst_gate_out.entry_no", read_only=True)
    bst_gate_out_vehicle_entry = serializers.IntegerField(
        source="bst_gate_out.vehicle_entry_id",
        read_only=True,
    )
    bst_gate_out_date = serializers.DateField(source="bst_gate_out.gate_out_date", read_only=True)
    bst_gate_out_time = serializers.TimeField(source="bst_gate_out.out_time", read_only=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    sap_doc_entry = serializers.IntegerField(source="bst_gate_out.sap_doc_entry", read_only=True)
    sap_doc_num = serializers.CharField(source="bst_gate_out.sap_doc_num", read_only=True)
    sap_doc_date = serializers.DateField(source="bst_gate_out.sap_doc_date", read_only=True)
    sap_from_warehouse = serializers.CharField(source="bst_gate_out.sap_from_warehouse", read_only=True)
    sap_to_warehouse = serializers.CharField(source="bst_gate_out.sap_to_warehouse", read_only=True)
    sap_reference = serializers.CharField(source="bst_gate_out.sap_reference", read_only=True)
    sap_comments = serializers.CharField(source="bst_gate_out.sap_comments", read_only=True)
    items = BSTGateOutItemSerializer(source="bst_gate_out.items", many=True, read_only=True)

    class Meta:
        model = BSTGateReturn
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_status", "bst_gate_out", "bst_gate_out_entry_no",
            "bst_gate_out_vehicle_entry", "bst_gate_out_date", "bst_gate_out_time",
            "vehicle", "vehicle_number", "vehicle_type", "transporter_name",
            "driver", "driver_name", "driver_mobile", "sap_doc_entry",
            "sap_doc_num", "sap_doc_date", "sap_from_warehouse",
            "sap_to_warehouse", "sap_reference", "sap_comments", "gate_in_date",
            "in_time", "security_name", "remarks", "status", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class BSTGateReturnCreateSerializer(serializers.Serializer):
    bst_gate_out_id = serializers.IntegerField()
    gate_in_date = serializers.DateField()
    in_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class EmptyVehicleGateInReasonSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class EmptyVehicleGateInItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmptyVehicleGateInItem
        fields = [
            "id", "line_num", "item_code", "item_name", "sap_quantity",
            "actual_quantity", "uom", "from_warehouse", "to_warehouse",
        ]
        read_only_fields = fields


class EmptyVehicleGateInSerializer(serializers.ModelSerializer):
    vehicle_entry_no = serializers.CharField(source="vehicle_entry.entry_no", read_only=True)
    vehicle_entry_status = serializers.CharField(source="vehicle_entry.status", read_only=True)
    vehicle_entry_time = serializers.DateTimeField(source="vehicle_entry.entry_time", read_only=True)
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.vehicle_type.name", read_only=True, allow_null=True)
    transporter_name = serializers.CharField(source="vehicle.transporter.name", read_only=True, allow_null=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    driver_mobile = serializers.CharField(source="driver.mobile_no", read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    bst_gate_out_id = serializers.SerializerMethodField()
    bst_gate_out_entry_no = serializers.SerializerMethodField()
    bst_gate_out_status = serializers.SerializerMethodField()
    is_bst_document_locked = serializers.SerializerMethodField()
    items = EmptyVehicleGateInItemSerializer(many=True, read_only=True)

    class Meta:
        model = EmptyVehicleGateIn
        fields = [
            "id", "entry_no", "company", "vehicle_entry", "vehicle_entry_no",
            "vehicle_entry_status", "vehicle_entry_time", "vehicle", "vehicle_number",
            "vehicle_type", "transporter_name", "driver", "driver_name",
            "driver_mobile", "reason", "reason_display", "gate_in_date",
            "in_time", "sap_doc_entry", "sap_doc_num", "sap_doc_date",
            "sap_from_warehouse", "sap_to_warehouse", "sap_reference",
            "sap_comments", "sap_line_count", "sap_total_quantity",
            "document_reference", "document_notes", "bst_gate_out_id",
            "bst_gate_out_entry_no", "bst_gate_out_status",
            "is_bst_document_locked", "items", "security_name", "remarks",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def _active_bst_gate_out(self, obj):
        return (
            obj.bst_gate_outs
            .filter(is_active=True, status__in=["IN_PROGRESS", "COMPLETED"])
            .order_by("-created_at")
            .first()
        )

    def get_bst_gate_out_id(self, obj):
        bst_out = self._active_bst_gate_out(obj)
        return bst_out.id if bst_out else None

    def get_bst_gate_out_entry_no(self, obj):
        bst_out = self._active_bst_gate_out(obj)
        return bst_out.entry_no if bst_out else ""

    def get_bst_gate_out_status(self, obj):
        bst_out = self._active_bst_gate_out(obj)
        return bst_out.status if bst_out else ""

    def get_is_bst_document_locked(self, obj):
        return bool(self._active_bst_gate_out(obj))


class EmptyVehicleGateInCreateSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=EmptyVehicleGateIn._meta.get_field("reason").choices)
    gate_in_date = serializers.DateField()
    in_time = serializers.TimeField()
    sap_doc_entry = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    document_reference = serializers.CharField(required=False, allow_blank=True, default="")
    document_notes = serializers.CharField(required=False, allow_blank=True, default="")
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if attrs["reason"] == "BST" and not attrs.get("sap_doc_entry"):
            raise serializers.ValidationError({
                "sap_doc_entry": "Select the SAP BST document for this empty vehicle entry."
            })
        if attrs["reason"] != "BST" and attrs.get("sap_doc_entry"):
            raise serializers.ValidationError({
                "sap_doc_entry": "SAP BST document can only be linked when the reason is BST."
            })
        return attrs


class EmptyVehicleGateInUpdateSerializer(serializers.Serializer):
    sap_doc_entry = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
    )
    document_reference = serializers.CharField(required=False, allow_blank=True)
    document_notes = serializers.CharField(required=False, allow_blank=True)
    security_name = serializers.CharField(required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


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
            "security_name", "remarks", "status", "cancel_reason", "cancelled_at",
            "cancelled_by", "created_at", "updated_at",
        ]
        read_only_fields = fields


class EmptyVehicleGateOutCreateSerializer(serializers.Serializer):
    vehicle_entry_id = serializers.IntegerField()
    gate_out_date = serializers.DateField()
    out_time = serializers.TimeField()
    security_name = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class EmptyVehicleGateOutCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


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
            "security_name", "gross_weight", "tare_weight", "net_weight",
            "weighbridge_slip_no", "first_weighment_time",
            "second_weighment_time", "gatepass_documents", "remarks", "status", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "entry_no", "company", "vehicle_number", "driver_name",
            "driver_mobile", "net_weight", "gatepass_documents", "status", "items",
            "created_at", "updated_at",
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
    gross_weight = serializers.DecimalField(max_digits=12, decimal_places=3)
    tare_weight = serializers.DecimalField(max_digits=12, decimal_places=3)
    weighbridge_slip_no = serializers.CharField(required=False, allow_blank=True, default="")
    first_weighment_time = serializers.DateTimeField(required=False, allow_null=True)
    second_weighment_time = serializers.DateTimeField(required=False, allow_null=True)
    gatepass_documents = serializers.ListField(
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        min_length=1,
    )
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    inspection_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
    )

    def validate(self, attrs):
        gross_weight = attrs.get("gross_weight")
        tare_weight = attrs.get("tare_weight")

        if gross_weight is None or gross_weight <= 0:
            raise serializers.ValidationError({"gross_weight": "Gross weight is required."})
        if tare_weight is None or tare_weight < 0:
            raise serializers.ValidationError({"tare_weight": "Tare weight is required."})
        if tare_weight > gross_weight:
            raise serializers.ValidationError(
                {"tare_weight": "Tare weight cannot be greater than gross weight."}
            )

        return attrs
