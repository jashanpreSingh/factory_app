from rest_framework import serializers

from .models import AuditInvoiceEntry, AuditTrackerType


# Invoice-data fields the submitter may provide, keyed by tracker type.
# Core fields (always required) + the type-specific optional fields.
CORE_FIELDS = ["invoice_date", "party_name", "invoice_no", "amount"]

TYPE_FIELDS = {
    AuditTrackerType.FACTORY: ["grpo_no", "dispatch_date"],
    AuditTrackerType.MAYAPURI: ["record_date"],
    AuditTrackerType.MART: ["receiving_date", "dispatch_date"],
    AuditTrackerType.IMPORT_EXPORT: ["rec_from_imp_exp_date"],
}

TYPE_FIELDS_ALL = [
    "grpo_no",
    "dispatch_date",
    "record_date",
    "receiving_date",
    "rec_from_imp_exp_date",
]


class AuditInvoiceEntrySerializer(serializers.ModelSerializer):
    """Read serializer with display labels and actor names."""

    tracker_type_display = serializers.CharField(
        source="get_tracker_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    documents_received_by_name = serializers.SerializerMethodField()
    pre_audited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditInvoiceEntry
        fields = [
            "id",
            "tracker_type",
            "tracker_type_display",
            "serial_no",
            "invoice_date",
            "party_name",
            "invoice_no",
            "amount",
            "grpo_no",
            "dispatch_date",
            "record_date",
            "receiving_date",
            "rec_from_imp_exp_date",
            "status",
            "status_display",
            "auditor_remarks",
            "documents_received_at",
            "documents_received_by",
            "documents_received_by_name",
            "pre_audited_at",
            "pre_audited_by",
            "pre_audited_by_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    @staticmethod
    def _name(user):
        if not user:
            return ""
        full = user.get_full_name() if hasattr(user, "get_full_name") else ""
        return full or getattr(user, "email", "") or str(user)

    def get_created_by_name(self, obj):
        return self._name(obj.created_by)

    def get_documents_received_by_name(self, obj):
        return self._name(obj.documents_received_by)

    def get_pre_audited_by_name(self, obj):
        return self._name(obj.pre_audited_by)


class AuditEntrySubmitSerializer(serializers.ModelSerializer):
    """Write serializer for submitting a new entry (invoice-data only)."""

    class Meta:
        model = AuditInvoiceEntry
        fields = [
            "tracker_type",
            "invoice_date",
            "party_name",
            "invoice_no",
            "amount",
            "grpo_no",
            "dispatch_date",
            "record_date",
            "receiving_date",
            "rec_from_imp_exp_date",
        ]
        extra_kwargs = {
            "grpo_no": {"required": False},
            "dispatch_date": {"required": False},
            "record_date": {"required": False},
            "receiving_date": {"required": False},
            "rec_from_imp_exp_date": {"required": False},
        }

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        tracker_type = attrs.get("tracker_type")
        allowed = set(CORE_FIELDS) | set(TYPE_FIELDS.get(tracker_type, []))
        # Drop type-specific fields that do not belong to the selected type so
        # an irrelevant value can never leak onto the entry.
        for field in TYPE_FIELDS_ALL:
            if field not in allowed:
                attrs.pop(field, None)
        return attrs


class AuditActionSerializer(serializers.Serializer):
    """Optional remarks supplied alongside a status transition."""

    remarks = serializers.CharField(required=False, allow_blank=True)


class AuditRemarksSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True)
