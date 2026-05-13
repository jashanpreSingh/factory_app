from django.db import models
from django.utils import timezone

from .base import BaseModel


class EmptyVehicleGateInReason(models.TextChoices):
    BST = "BST", "BST"
    DISPATCH = "DISPATCH", "Dispatch"
    REPAIR_MOVEMENT = "REPAIR_MOVEMENT", "Repair Movement"
    JOB_WORK = "JOB_WORK", "Job Work"
    OTHER = "OTHER", "Other"


class EmptyVehicleGateIn(BaseModel):
    """Gate-in record for empty vehicles arriving for an outbound movement."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_ins",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    vehicle_entry = models.OneToOneField(
        "driver_management.VehicleEntry",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_in",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_ins",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_ins",
    )
    reason = models.CharField(
        max_length=30,
        choices=EmptyVehicleGateInReason.choices,
    )
    gate_in_date = models.DateField()
    in_time = models.TimeField()
    sap_doc_entry = models.IntegerField(null=True, blank=True)
    sap_doc_num = models.CharField(max_length=50, blank=True)
    sap_doc_date = models.DateField(null=True, blank=True)
    sap_from_warehouse = models.CharField(max_length=50, blank=True)
    sap_to_warehouse = models.CharField(max_length=50, blank=True)
    sap_reference = models.CharField(max_length=100, blank=True)
    sap_comments = models.TextField(blank=True)
    sap_line_count = models.PositiveIntegerField(default=0)
    sap_total_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    document_reference = models.CharField(max_length=255, blank=True)
    document_notes = models.TextField(blank=True)
    security_name = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-gate_in_date", "-in_time", "-created_at"]
        indexes = [
            models.Index(fields=["company", "gate_in_date"]),
            models.Index(fields=["reason"]),
            models.Index(fields=["vehicle"]),
            models.Index(fields=["sap_doc_entry"], name="gcevg_sapdoc_idx"),
        ]

    def __str__(self):
        return self.entry_no

    @staticmethod
    def generate_entry_no():
        today = timezone.now()
        prefix = f"EVGI-{today.strftime('%Y%m%d')}"
        last = (
            EmptyVehicleGateIn.objects
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


class EmptyVehicleGateInItem(BaseModel):
    """Line-level SAP BST quantity captured when an empty vehicle enters."""

    empty_vehicle_gate_in = models.ForeignKey(
        EmptyVehicleGateIn,
        on_delete=models.CASCADE,
        related_name="items",
    )
    line_num = models.IntegerField()
    item_code = models.CharField(max_length=100, blank=True)
    item_name = models.CharField(max_length=255, blank=True)
    sap_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    actual_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    uom = models.CharField(max_length=50, blank=True)
    from_warehouse = models.CharField(max_length=50, blank=True)
    to_warehouse = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["line_num"]
        constraints = [
            models.UniqueConstraint(
                fields=["empty_vehicle_gate_in", "line_num"],
                name="unique_empty_vehicle_gate_in_line",
            ),
        ]

    def __str__(self):
        return f"{self.empty_vehicle_gate_in.entry_no} - {self.item_code}"
