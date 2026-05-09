import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from .base import BaseModel


class DispatchGateOutStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    REJECTED = "REJECTED", "Rejected"


class DispatchPhysicalUOM(models.TextChoices):
    PCS = "PCS", "Pcs"
    BOX = "BOX", "Box"


class DispatchGateOut(BaseModel):
    """Gate-out record for customer sales dispatches against SAP A/R invoices."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="dispatch_gate_outs",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    dispatch_plan = models.ForeignKey(
        "dispatch_plans.DispatchPlan",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="gate_outs",
    )
    vehicle_entry = models.ForeignKey(
        "driver_management.VehicleEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_gate_outs",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="dispatch_gate_outs",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="dispatch_gate_outs",
    )

    sap_invoice_doc_entry = models.IntegerField()
    sap_invoice_doc_num = models.CharField(max_length=30, blank=True)
    customer_code = models.CharField(max_length=50, blank=True)
    customer_name = models.CharField(max_length=255, blank=True)
    ship_to_address = models.TextField(blank=True)
    invoice_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sap_weight = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)

    gate_out_date = models.DateField()
    out_time = models.TimeField()
    security_name = models.CharField(max_length=100, blank=True)
    seal_no = models.CharField(max_length=100, blank=True)
    pgi_document_no = models.CharField(max_length=100, blank=True)
    goods_issue_posted = models.BooleanField(default=False)
    invoice_checked = models.BooleanField(default=False)
    delivery_note_checked = models.BooleanField(default=False)
    eway_bill_checked = models.BooleanField(default=False)
    lr_checked = models.BooleanField(default=False)

    physical_quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    physical_uom = models.CharField(
        max_length=10,
        choices=DispatchPhysicalUOM.choices,
        blank=True,
    )

    gross_weight = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    tare_weight = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    net_weight = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, editable=False)
    weighbridge_slip_no = models.CharField(max_length=50, blank=True)
    first_weighment_time = models.DateTimeField(null=True, blank=True)
    second_weighment_time = models.DateTimeField(null=True, blank=True)

    dock_photo = models.FileField(upload_to="dispatch_gate/dock_photos/", null=True, blank=True)
    gatepass_document = models.FileField(upload_to="dispatch_gate/gatepass_documents/", null=True, blank=True)
    attachment_notes = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    gatepass_no = models.CharField(max_length=50, blank=True)
    gatepass_code = models.CharField(max_length=20, blank=True)
    gate_printed = models.BooleanField(default=False)
    print_commit = models.BooleanField(default=False)
    printed_at = models.DateTimeField(null=True, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=DispatchGateOutStatus.choices,
        default=DispatchGateOutStatus.IN_PROGRESS,
    )
    cancel_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "gate_out_date"]),
            models.Index(fields=["company", "sap_invoice_doc_entry"]),
            models.Index(fields=["company", "status"]),
            models.Index(fields=["company", "gate_printed", "print_commit"]),
        ]

    def __str__(self):
        return self.entry_no

    @property
    def weight_variance(self):
        if self.sap_weight is None or self.net_weight is None:
            return None
        return self.net_weight - self.sap_weight

    @property
    def qr_payload(self):
        if not self.gatepass_no or not self.gatepass_code:
            return ""
        stamp = (self.printed_at or timezone.now()).strftime("%d%m%Y%I%M%S%p")
        return f"{self.sap_invoice_doc_entry}-{self.gatepass_no}-{self.gatepass_code}-{stamp}"

    def save(self, *args, **kwargs):
        if self.gross_weight is not None and self.tare_weight is not None:
            self.net_weight = self.gross_weight - self.tare_weight
        super().save(*args, **kwargs)

    def ensure_gatepass(self):
        if not self.gatepass_no:
            today = timezone.now()
            prefix = f"GP-SDO-{today.strftime('%Y%m%d')}"
            last = (
                DispatchGateOut.objects
                .filter(gatepass_no__startswith=prefix)
                .order_by("-gatepass_no")
                .first()
            )
            if last:
                try:
                    next_number = int(last.gatepass_no.split("-")[-1]) + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
            self.gatepass_no = f"{prefix}-{next_number:04d}"
        if not self.gatepass_code:
            self.gatepass_code = secrets.token_hex(4).upper()
        if not self.printed_at:
            self.printed_at = timezone.now()
        self.gate_printed = True

    @staticmethod
    def generate_entry_no():
        today = timezone.now()
        prefix = f"SDO-{today.strftime('%Y%m%d')}"
        last = (
            DispatchGateOut.objects
            .filter(entry_no__startswith=prefix)
            .order_by("-entry_no")
            .first()
        )
        if last:
            try:
                next_number = int(last.entry_no.split("-")[-1]) + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1
        return f"{prefix}-{next_number:04d}"


class DispatchGateOutLine(BaseModel):
    entry = models.ForeignKey(
        DispatchGateOut,
        on_delete=models.CASCADE,
        related_name="items",
    )
    line_num = models.IntegerField(default=0)
    item_code = models.CharField(max_length=100, blank=True)
    item_name = models.CharField(max_length=255, blank=True)
    order_qty = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    dispatched_qty = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    uom = models.CharField(max_length=30, blank=True)
    warehouse = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["line_num", "id"]

    def __str__(self):
        return f"{self.entry.entry_no} - {self.item_code or self.item_name}"


class DispatchGateLock(BaseModel):
    company = models.OneToOneField(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="dispatch_gate_lock",
    )
    locked = models.BooleanField(default=False)
    reason = models.TextField(blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_gate_locks_changed",
    )

    def __str__(self):
        return f"{self.company.code} dispatch {'locked' if self.locked else 'unlocked'}"
