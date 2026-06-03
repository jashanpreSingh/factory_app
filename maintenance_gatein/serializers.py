from rest_framework import serializers

from maintenance.constants import GateQCStatus, GateReceiptStatus
from maintenance.models import Asset, MaintenanceGateLink, MaintenanceSpare, MaintenanceWorkOrder

from .models import MaintenanceGateEntry, MaintenanceType


class MaintenanceTypeSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceType lookup"""

    class Meta:
        model = MaintenanceType
        fields = "__all__"


class MaintenanceGateEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for MaintenanceGateEntry.
    Follows same pattern as DailyNeedGateEntrySerializer.
    """

    maintenance_asset = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.none(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    maintenance_work_order = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceWorkOrder.objects.none(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    maintenance_spare = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceSpare.objects.none(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    qc_required = serializers.BooleanField(required=False, write_only=True)
    qc_status = serializers.ChoiceField(
        choices=GateQCStatus.choices,
        required=False,
        write_only=True,
    )
    grpo_reference = serializers.CharField(required=False, allow_blank=True, write_only=True)
    grpo_doc_entry = serializers.IntegerField(required=False, allow_null=True, min_value=1, write_only=True)
    grpo_doc_num = serializers.CharField(required=False, allow_blank=True, write_only=True)
    maintenance_link = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceGateEntry
        fields = [
            "id",
            "maintenance_type",
            "work_order_number",
            "supplier_name",
            "material_description",
            "part_number",
            "quantity",
            "unit",
            "invoice_number",
            "equipment_id",
            "receiving_department",
            "urgency_level",
            "inward_time",
            "remarks",
            "created_at",
            "updated_at",
            "maintenance_asset",
            "maintenance_work_order",
            "maintenance_spare",
            "qc_required",
            "qc_status",
            "grpo_reference",
            "grpo_doc_entry",
            "grpo_doc_num",
            "maintenance_link",
        ]
        read_only_fields = ("created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = self._company()
        if not company:
            return
        self.fields["maintenance_asset"].queryset = Asset.objects.filter(
            company=company,
            is_active=True,
        )
        self.fields["maintenance_work_order"].queryset = MaintenanceWorkOrder.objects.filter(
            company=company,
            is_active=True,
        )
        self.fields["maintenance_spare"].queryset = MaintenanceSpare.objects.filter(
            company=company,
            is_active=True,
        )

    def _company(self):
        request = self.context.get("request")
        return request.company.company if request and hasattr(request, "company") else None

    def _existing_link(self):
        if not self.instance:
            return None
        try:
            return self.instance.maintenance_link
        except MaintenanceGateLink.DoesNotExist:
            return None

    def _resolve_asset(self, company, attrs, work_order):
        link = self._existing_link()
        asset = attrs.get("maintenance_asset", link.asset if link else None)
        equipment_id = attrs.get("equipment_id", getattr(self.instance, "equipment_id", None))
        if work_order and not asset:
            asset = work_order.asset
        if not asset and company and equipment_id:
            asset = Asset.objects.filter(
                company=company,
                asset_code__iexact=str(equipment_id).strip(),
                is_active=True,
            ).first()
        return asset

    def _resolve_spare(self, company, attrs):
        link = self._existing_link()
        spare = attrs.get("maintenance_spare", link.spare if link else None)
        part_number = attrs.get("part_number", getattr(self.instance, "part_number", None))
        if not spare and company and part_number:
            spare = MaintenanceSpare.objects.filter(
                company=company,
                part_number__iexact=str(part_number).strip(),
                is_active=True,
            ).first()
        return spare

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number")
        return value

    def validate_supplier_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Supplier name must be at least 2 characters")
        return value.strip() if value else value

    def validate_material_description(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Material description must be at least 5 characters")
        return value.strip() if value else value

    def validate(self, attrs):
        company = self._company()
        link = self._existing_link()
        work_order = attrs.get("maintenance_work_order", link.work_order if link else None)
        if work_order and company and work_order.company_id != company.id:
            raise serializers.ValidationError(
                {"maintenance_work_order": "Work order must belong to current company."}
            )

        asset = self._resolve_asset(company, attrs, work_order)
        if asset and company and asset.company_id != company.id:
            raise serializers.ValidationError(
                {"maintenance_asset": "Asset must belong to current company."}
            )
        if work_order and asset and work_order.asset_id != asset.id:
            raise serializers.ValidationError(
                {"maintenance_asset": "Asset must match the selected work order."}
            )

        spare = self._resolve_spare(company, attrs)
        if spare and company and spare.company_id != company.id:
            raise serializers.ValidationError(
                {"maintenance_spare": "Spare must belong to current company."}
            )

        if asset:
            attrs["maintenance_asset"] = asset
        if work_order:
            attrs["maintenance_work_order"] = work_order
        if spare:
            attrs["maintenance_spare"] = spare

        qc_required = attrs.get("qc_required")
        if qc_required is None:
            qc_required = link.qc_required if link else False
        if spare and spare.is_critical and "qc_required" not in attrs:
            qc_required = True
        attrs["qc_required"] = qc_required

        if "qc_status" not in attrs:
            if link:
                attrs["qc_status"] = link.qc_status
            elif qc_required:
                attrs["qc_status"] = GateQCStatus.PENDING
            else:
                attrs["qc_status"] = GateQCStatus.NOT_REQUIRED
        if not qc_required and attrs["qc_status"] == GateQCStatus.PENDING:
            attrs["qc_status"] = GateQCStatus.NOT_REQUIRED

        return attrs

    def _pop_link_data(self, validated_data):
        link_keys = [
            "maintenance_asset",
            "maintenance_work_order",
            "maintenance_spare",
            "qc_required",
            "qc_status",
            "grpo_reference",
            "grpo_doc_entry",
            "grpo_doc_num",
        ]
        return {key: validated_data.pop(key) for key in link_keys if key in validated_data}

    def _sync_link(self, instance, link_data):
        company = self._company()
        if not company or not link_data:
            return
        has_link_value = any(
            link_data.get(key) not in (None, "")
            for key in [
                "maintenance_asset",
                "maintenance_work_order",
                "maintenance_spare",
                "grpo_reference",
                "grpo_doc_entry",
                "grpo_doc_num",
            ]
        ) or link_data.get("qc_required") is True or link_data.get("qc_status") not in (None, "", GateQCStatus.NOT_REQUIRED)
        if not has_link_value:
            return

        request = self.context.get("request")
        user = getattr(request, "user", None)
        link, created = MaintenanceGateLink.objects.get_or_create(
            gate_entry=instance,
            defaults={
                "company": company,
                "created_by": user if user and user.is_authenticated else None,
                "updated_by": user if user and user.is_authenticated else None,
            },
        )
        link.company = company
        field_map = {
            "maintenance_asset": "asset",
            "maintenance_work_order": "work_order",
            "maintenance_spare": "spare",
        }
        for source, target in field_map.items():
            if source in link_data:
                setattr(link, target, link_data[source])
        for field in ["qc_required", "qc_status", "grpo_reference", "grpo_doc_entry", "grpo_doc_num"]:
            if field in link_data:
                setattr(link, field, link_data[field])
        if link.spare and link.spare.is_critical and not link.qc_required:
            link.qc_required = True
        if link.qc_required and link.qc_status == GateQCStatus.NOT_REQUIRED:
            link.qc_status = GateQCStatus.PENDING
        if not link.qc_required and link.qc_status == GateQCStatus.PENDING:
            link.qc_status = GateQCStatus.NOT_REQUIRED
        if created and link.receipt_status == "":
            link.receipt_status = GateReceiptStatus.NOT_RECEIVED
        if user and user.is_authenticated:
            link.updated_by = user
        link.save()

    def create(self, validated_data):
        link_data = self._pop_link_data(validated_data)
        instance = super().create(validated_data)
        self._sync_link(instance, link_data)
        return instance

    def update(self, instance, validated_data):
        link_data = self._pop_link_data(validated_data)
        instance = super().update(instance, validated_data)
        self._sync_link(instance, link_data)
        return instance

    def get_maintenance_link(self, instance):
        try:
            link = instance.maintenance_link
        except MaintenanceGateLink.DoesNotExist:
            return None
        return {
            "id": link.id,
            "asset": link.asset_id,
            "asset_code": link.asset.asset_code if link.asset else "",
            "asset_name": link.asset.name if link.asset else "",
            "work_order": link.work_order_id,
            "work_order_no": link.work_order.work_order_no if link.work_order else "",
            "work_order_title": link.work_order.title if link.work_order else "",
            "spare": link.spare_id,
            "spare_part_number": link.spare.part_number if link.spare else "",
            "spare_name": link.spare.name if link.spare else "",
            "spare_uom": link.spare.uom if link.spare else "",
            "spare_is_critical": link.spare.is_critical if link.spare else False,
            "qc_required": link.qc_required,
            "qc_status": link.qc_status,
            "grpo_reference": link.grpo_reference,
            "grpo_doc_entry": link.grpo_doc_entry,
            "grpo_doc_num": link.grpo_doc_num,
            "receipt_status": link.receipt_status,
            "received_quantity": str(link.received_quantity),
            "received_at": link.received_at,
            "received_by": link.received_by_id,
            "received_by_name": link.received_by.full_name if link.received_by else "",
        }

    def to_representation(self, instance):
        """Expand ForeignKey fields for API response"""
        data = super().to_representation(instance)

        # Expand maintenance_type
        if instance.maintenance_type:
            data['maintenance_type'] = {
                'id': instance.maintenance_type.id,
                'type_name': instance.maintenance_type.type_name
            }

        # Expand receiving_department
        if instance.receiving_department:
            data['receiving_department'] = {
                'id': instance.receiving_department.id,
                'name': instance.receiving_department.name
            }
        
        if instance.unit:
            data['unit'] = {
                'id': instance.unit.id,
                'name': instance.unit.name
            }

        return data
