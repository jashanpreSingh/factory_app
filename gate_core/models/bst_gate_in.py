from django.db import models
from django.utils import timezone

from .base import BaseModel


class BSTGateInStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class BSTGateIn(BaseModel):
    """Receiving-side gate-in record for a BST vehicle that has left another branch."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="bst_gate_ins",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    vehicle_entry = models.ForeignKey(
        "driver_management.VehicleEntry",
        on_delete=models.PROTECT,
        related_name="bst_gate_ins",
    )
    bst_gate_out = models.ForeignKey(
        "gate_core.BSTGateOut",
        on_delete=models.PROTECT,
        related_name="bst_gate_ins",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="bst_gate_ins",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="bst_gate_ins",
    )
    gate_in_date = models.DateField()
    in_time = models.TimeField()
    security_name = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=BSTGateInStatus.choices,
        default=BSTGateInStatus.IN_PROGRESS,
    )

    class Meta:
        ordering = ["-gate_in_date", "-in_time", "-created_at"]
        indexes = [
            models.Index(fields=["company", "gate_in_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["vehicle"]),
            models.Index(fields=["bst_gate_out"]),
        ]

    def __str__(self):
        return self.entry_no

    @staticmethod
    def generate_entry_no():
        today = timezone.now()
        prefix = f"BSTI-{today.strftime('%Y%m%d')}"
        last = (
            BSTGateIn.objects
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


class BSTGateInItem(BaseModel):
    """Receiving-side quantity snapshot for each BST line."""

    bst_gate_in = models.ForeignKey(
        BSTGateIn,
        on_delete=models.CASCADE,
        related_name="items",
    )
    bst_gate_out_item = models.ForeignKey(
        "gate_core.BSTGateOutItem",
        on_delete=models.PROTECT,
        related_name="bst_gate_in_items",
    )
    line_num = models.IntegerField()
    item_code = models.CharField(max_length=100, blank=True)
    item_name = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    actual_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    receiving_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    uom = models.CharField(max_length=50, blank=True)
    from_warehouse = models.CharField(max_length=50, blank=True)
    to_warehouse = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["line_num"]
        constraints = [
            models.UniqueConstraint(
                fields=["bst_gate_in", "line_num"],
                name="unique_bst_gate_in_line",
            ),
        ]

    def __str__(self):
        return f"{self.bst_gate_in.entry_no} - {self.item_code}"
