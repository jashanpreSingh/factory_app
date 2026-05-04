from django.contrib import admin
from .models import EmptyVehicleGateOut, RejectedQCReturnEntry, RejectedQCReturnItem, UnitChoice


# Register your models here.
admin.site.register(UnitChoice)


class RejectedQCReturnItemInline(admin.TabularInline):
    model = RejectedQCReturnItem
    extra = 0
    readonly_fields = (
        "inspection", "gate_entry_no", "report_no", "internal_lot_no",
        "item_name", "supplier_name", "quantity", "uom",
    )


@admin.register(RejectedQCReturnEntry)
class RejectedQCReturnEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "vehicle", "driver", "gate_out_date",
        "status", "created_at",
    )
    list_filter = ("company", "status", "gate_out_date")
    search_fields = (
        "entry_no", "vehicle__vehicle_number", "driver__name",
        "challan_no", "eway_bill_no",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")
    inlines = [RejectedQCReturnItemInline]


@admin.register(EmptyVehicleGateOut)
class EmptyVehicleGateOutAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "vehicle_entry", "vehicle", "driver",
        "gate_out_date", "out_time", "status", "created_at",
    )
    list_filter = ("company", "status", "gate_out_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "vehicle__vehicle_number",
        "driver__name", "security_name",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")
