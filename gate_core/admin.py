from django.contrib import admin
from .models import (
    BSTGateIn,
    BSTGateOut,
    BSTGateOutItem,
    BSTGateReturn,
    EmptyVehicleGateIn,
    EmptyVehicleGateOut,
    JobWorkGateIn,
    JobWorkGateInItem,
    RejectedQCReturnEntry,
    RejectedQCReturnItem,
    SalesDispatchAttachment,
    SalesDispatchGateOut,
    SalesDispatchGateOutItem,
    SalesDispatchGatepassSequence,
    UnitChoice,
)


# Register your models here.
admin.site.register(UnitChoice)


class BSTGateOutItemInline(admin.TabularInline):
    model = BSTGateOutItem
    extra = 0
    readonly_fields = (
        "line_num", "item_code", "item_name", "quantity", "uom",
        "from_warehouse", "to_warehouse",
    )


@admin.register(BSTGateOut)
class BSTGateOutAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "vehicle", "driver", "sap_doc_num",
        "sap_from_warehouse", "sap_to_warehouse", "gate_out_date",
        "status", "created_at",
    )
    list_filter = ("company", "status", "gate_out_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "vehicle__vehicle_number",
        "driver__name", "sap_doc_num", "sap_from_warehouse", "sap_to_warehouse",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")
    inlines = [BSTGateOutItemInline]


class SalesDispatchGateOutItemInline(admin.TabularInline):
    model = SalesDispatchGateOutItem
    extra = 0
    readonly_fields = (
        "line_num", "item_code", "item_name", "quantity", "uom",
        "warehouse_code", "from_warehouse", "to_warehouse",
    )


class SalesDispatchAttachmentInline(admin.TabularInline):
    model = SalesDispatchAttachment
    extra = 0
    readonly_fields = ("uploaded_at", "uploaded_by", "original_filename")


@admin.register(SalesDispatchGateOut)
class SalesDispatchGateOutAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "document_type", "sap_doc_num",
        "vehicle_no", "driver_name", "status", "gatepass_no", "created_at",
    )
    list_filter = ("company", "document_type", "status", "created_at")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "sap_doc_num",
        "vehicle_no", "driver_name", "customer_name", "gatepass_no",
    )
    readonly_fields = ("entry_no", "gatepass_no", "created_at", "updated_at")
    inlines = [SalesDispatchGateOutItemInline, SalesDispatchAttachmentInline]


@admin.register(SalesDispatchGatepassSequence)
class SalesDispatchGatepassSequenceAdmin(admin.ModelAdmin):
    list_display = ("company", "financial_year", "last_number", "updated_at")
    list_filter = ("company", "financial_year")


class JobWorkGateInItemInline(admin.TabularInline):
    model = JobWorkGateInItem
    extra = 0
    readonly_fields = (
        "line_num", "item_code", "item_name", "quantity", "uom",
        "warehouse_code", "base_type", "base_entry", "base_line",
    )


@admin.register(JobWorkGateIn)
class JobWorkGateInAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "vehicle", "driver", "production_order_doc_num",
        "production_item_name", "gate_in_date", "in_time", "status", "created_at",
    )
    list_filter = ("company", "status", "gate_in_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "vehicle__vehicle_number",
        "driver__name", "production_order_doc_num", "production_item_code",
        "production_item_name", "sap_doc_num",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")
    inlines = [JobWorkGateInItemInline]


@admin.register(BSTGateIn)
class BSTGateInAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "bst_gate_out", "vehicle", "driver",
        "gate_in_date", "in_time", "status", "created_at",
    )
    list_filter = ("company", "status", "gate_in_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "bst_gate_out__entry_no",
        "vehicle__vehicle_number", "driver__name", "bst_gate_out__sap_doc_num",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")


@admin.register(BSTGateReturn)
class BSTGateReturnAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "bst_gate_out", "vehicle", "driver",
        "gate_in_date", "in_time", "status", "created_at",
    )
    list_filter = ("company", "status", "gate_in_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "bst_gate_out__entry_no",
        "vehicle__vehicle_number", "driver__name", "bst_gate_out__sap_doc_num",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")


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


@admin.register(EmptyVehicleGateIn)
class EmptyVehicleGateInAdmin(admin.ModelAdmin):
    list_display = (
        "entry_no", "company", "vehicle_entry", "vehicle", "driver",
        "reason", "sap_doc_num", "gate_in_date", "in_time", "created_at",
    )
    list_filter = ("company", "reason", "gate_in_date")
    search_fields = (
        "entry_no", "vehicle_entry__entry_no", "vehicle__vehicle_number",
        "driver__name", "security_name", "sap_doc_num", "document_reference",
    )
    readonly_fields = ("entry_no", "created_at", "updated_at")
