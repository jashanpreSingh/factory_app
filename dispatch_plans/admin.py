from django.contrib import admin

from .models import DispatchPlan


@admin.register(DispatchPlan)
class DispatchPlanAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "sap_invoice_doc_num",
        "booking_status",
        "dispatch_date",
        "transporter_name",
        "vehicle_no",
        "driver_name",
        "bilty_no",
        "updated_at",
    )
    list_filter = ("company", "booking_status", "dispatch_date")
    search_fields = (
        "sap_invoice_doc_num",
        "transporter_name",
        "vehicle_no",
        "driver_name",
        "driver_mobile_no",
        "driver_license_no",
        "bilty_no",
        "mobile_no",
    )
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
