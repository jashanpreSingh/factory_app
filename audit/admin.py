from django.contrib import admin

from .models import AuditInvoiceEntry


@admin.register(AuditInvoiceEntry)
class AuditInvoiceEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tracker_type",
        "serial_no",
        "party_name",
        "invoice_no",
        "amount",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("tracker_type", "status")
    search_fields = ("party_name", "invoice_no", "grpo_no")
    readonly_fields = (
        "created_at",
        "updated_at",
        "documents_received_at",
        "pre_audited_at",
    )
    ordering = ("-created_at",)
