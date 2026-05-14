from rest_framework import serializers

from .models import DispatchPlan, DispatchPlanStatus


class DispatchBillFilterSerializer(serializers.Serializer):
    STATUS_CHOICES = [("all", "All")] + list(DispatchPlanStatus.choices)

    date_from = serializers.DateField(required=True, input_formats=["%Y-%m-%d"])
    date_to = serializers.DateField(required=True, input_formats=["%Y-%m-%d"])
    booking_status = serializers.ChoiceField(
        choices=STATUS_CHOICES,
        default="all",
        required=False,
    )
    search = serializers.CharField(required=False, max_length=120, allow_blank=True)
    branch = serializers.CharField(required=False, max_length=80, allow_blank=True)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=2000)

    def validate(self, attrs):
        if attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError("date_from must be before or equal to date_to.")
        return attrs


class DispatchPlanSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.IntegerField(read_only=True, allow_null=True)
    transporter_id = serializers.IntegerField(read_only=True, allow_null=True)
    driver_id = serializers.IntegerField(read_only=True, allow_null=True)
    linked_vehicle_entry_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = DispatchPlan
        fields = [
            "id",
            "sap_invoice_doc_entry",
            "sap_invoice_doc_num",
            "vehicle_id",
            "transporter_id",
            "driver_id",
            "linked_vehicle_entry_id",
            "booking_status",
            "dispatch_date",
            "priority",
            "transporter_name",
            "transporter_gstin",
            "contact_person",
            "mobile_no",
            "vehicle_no",
            "driver_name",
            "driver_mobile_no",
            "driver_license_no",
            "driver_id_proof_type",
            "driver_id_proof_number",
            "bilty_no",
            "bilty_date",
            "freight",
            "total_freight",
            "kanta_weight",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DispatchPlanUpdateSerializer(serializers.Serializer):
    sap_invoice_doc_num = serializers.CharField(
        required=False, max_length=30, allow_blank=True
    )
    vehicle_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    transporter_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    driver_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    linked_vehicle_entry_id = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    booking_status = serializers.ChoiceField(
        choices=DispatchPlanStatus.choices,
        required=False,
    )
    dispatch_date = serializers.DateField(
        required=False, allow_null=True, input_formats=["%Y-%m-%d"]
    )
    priority = serializers.CharField(required=False, max_length=50, allow_blank=True)
    transporter_name = serializers.CharField(
        required=False, max_length=150, allow_blank=True
    )
    transporter_gstin = serializers.CharField(
        required=False, max_length=20, allow_blank=True
    )
    contact_person = serializers.CharField(
        required=False, max_length=100, allow_blank=True
    )
    mobile_no = serializers.CharField(required=False, max_length=50, allow_blank=True)
    vehicle_no = serializers.CharField(required=False, max_length=30, allow_blank=True)
    driver_name = serializers.CharField(required=False, max_length=100, allow_blank=True)
    driver_mobile_no = serializers.CharField(required=False, max_length=50, allow_blank=True)
    driver_license_no = serializers.CharField(required=False, max_length=50, allow_blank=True)
    driver_id_proof_type = serializers.CharField(
        required=False, max_length=50, allow_blank=True
    )
    driver_id_proof_number = serializers.CharField(
        required=False, max_length=50, allow_blank=True
    )
    bilty_no = serializers.CharField(required=False, max_length=50, allow_blank=True)
    bilty_date = serializers.DateField(
        required=False, allow_null=True, input_formats=["%Y-%m-%d"]
    )
    freight = serializers.DecimalField(
        required=False, allow_null=True, max_digits=18, decimal_places=2
    )
    total_freight = serializers.DecimalField(
        required=False, allow_null=True, max_digits=18, decimal_places=2
    )
    kanta_weight = serializers.DecimalField(
        required=False, allow_null=True, max_digits=18, decimal_places=3
    )
    remarks = serializers.CharField(required=False, allow_blank=True)


class DispatchBillSerializer(serializers.Serializer):
    doc_entry = serializers.IntegerField()
    doc_num = serializers.CharField()
    doc_date = serializers.CharField(allow_null=True)
    create_date = serializers.CharField(allow_null=True)
    create_time = serializers.CharField(allow_blank=True)
    card_code = serializers.CharField()
    card_name = serializers.CharField()
    doc_total = serializers.FloatField()
    branch_id = serializers.IntegerField(allow_null=True)
    branch_name = serializers.CharField()
    ship_to_code = serializers.CharField()
    ship_to_address = serializers.CharField()
    state = serializers.CharField()
    city = serializers.CharField()
    bp_gstin = serializers.CharField()
    sap_dispatch_date = serializers.CharField(allow_null=True)
    sap_bilty_no = serializers.CharField()
    sap_bilty_date = serializers.CharField(allow_null=True)
    sap_transporter_name = serializers.CharField()
    sap_vehicle_no = serializers.CharField()
    sap_transporter_invoice = serializers.CharField()
    sap_lr_number = serializers.CharField()
    gst_vehicle_no = serializers.CharField()
    gst_transport_date = serializers.CharField(allow_null=True)
    gst_transport_reason = serializers.CharField()
    line_count = serializers.IntegerField()
    total_quantity = serializers.FloatField()
    total_litres = serializers.FloatField()
    total_boxes = serializers.FloatField()
    total_weight = serializers.FloatField()
    total_line_amount = serializers.FloatField()
    total_gross_amount = serializers.FloatField()
    warehouses = serializers.CharField()
    item_summary = serializers.CharField()
    base_refs = serializers.CharField()
    plan = DispatchPlanSerializer(allow_null=True)


class DispatchBillLineSerializer(serializers.Serializer):
    line_num = serializers.IntegerField()
    item_code = serializers.CharField(allow_blank=True)
    item_name = serializers.CharField(allow_blank=True)
    quantity = serializers.FloatField()
    uom = serializers.CharField(allow_blank=True)
    rate = serializers.FloatField()
    line_total = serializers.FloatField()
    gross_total = serializers.FloatField()
    warehouse_code = serializers.CharField(allow_blank=True)
    base_ref = serializers.CharField(allow_blank=True)
    base_entry = serializers.IntegerField(allow_null=True)
    base_type = serializers.IntegerField(allow_null=True)
    tax_code = serializers.CharField(allow_blank=True)
    total_litres = serializers.FloatField()
    total_boxes = serializers.FloatField()
    total_weight = serializers.FloatField()


class DispatchBillDetailSerializer(DispatchBillSerializer):
    items = DispatchBillLineSerializer(many=True)


class DispatchPlansMetaSerializer(serializers.Serializer):
    total_bills = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    booked_count = serializers.IntegerField()
    dispatched_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    total_doc_value = serializers.FloatField()
    total_litres = serializers.FloatField()
    total_boxes = serializers.FloatField()
    fetched_at = serializers.CharField()


class DispatchBillListResponseSerializer(serializers.Serializer):
    data = DispatchBillSerializer(many=True)
    meta = DispatchPlansMetaSerializer()
