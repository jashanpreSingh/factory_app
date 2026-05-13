from django.db import models
from django.conf import settings
from django.utils import timezone

from .base import BaseModel


class BSTGateOutStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class BSTGateOut(BaseModel):
    """Gate-out record for a Branch Stock Transfer already posted in SAP."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="bst_gate_outs",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    vehicle_entry = models.ForeignKey(
        "driver_management.VehicleEntry",
        on_delete=models.PROTECT,
        related_name="bst_gate_outs",
    )
    empty_vehicle_gate_in = models.ForeignKey(
        "gate_core.EmptyVehicleGateIn",
        on_delete=models.PROTECT,
        related_name="bst_gate_outs",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="bst_gate_outs",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="bst_gate_outs",
    )
    sap_doc_entry = models.IntegerField()
    sap_doc_num = models.CharField(max_length=50)
    sap_doc_date = models.DateField(null=True, blank=True)
    sap_from_warehouse = models.CharField(max_length=50, blank=True)
    sap_to_warehouse = models.CharField(max_length=50, blank=True)
    sap_reference = models.CharField(max_length=100, blank=True)
    sap_comments = models.TextField(blank=True)
    gate_out_date = models.DateField()
    out_time = models.TimeField()
    security_name = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=BSTGateOutStatus.choices,
        default=BSTGateOutStatus.IN_PROGRESS,
    )
    cancel_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bst_gate_outs_cancelled",
    )

    class Meta:
        ordering = ["-gate_out_date", "-out_time", "-created_at"]
        indexes = [
            models.Index(fields=["company", "gate_out_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["sap_doc_entry"]),
            models.Index(fields=["sap_doc_num"]),
        ]

    def __str__(self):
        return self.entry_no

    @staticmethod
    def generate_entry_no():
        today = timezone.now()
        prefix = f"BSTO-{today.strftime('%Y%m%d')}"
        last = (
            BSTGateOut.objects
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


class BSTGateOutItem(BaseModel):
    """Snapshot of SAP WTR1 lines selected for BST gate-out."""

    bst_gate_out = models.ForeignKey(
        BSTGateOut,
        on_delete=models.CASCADE,
        related_name="items",
    )
    line_num = models.IntegerField()
    item_code = models.CharField(max_length=100, blank=True)
    item_name = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    actual_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    uom = models.CharField(max_length=50, blank=True)
    from_warehouse = models.CharField(max_length=50, blank=True)
    to_warehouse = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["line_num"]
        constraints = [
            models.UniqueConstraint(
                fields=["bst_gate_out", "line_num"],
                name="unique_bst_gate_out_line",
            ),
        ]

    def __str__(self):
        return f"{self.bst_gate_out.entry_no} - {self.item_code}"
