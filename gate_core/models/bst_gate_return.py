from django.db import models
from django.utils import timezone

from .base import BaseModel


class BSTGateReturnStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class BSTGateReturn(BaseModel):
    """Source-side gate-in record for a BST vehicle that returned before BST In."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="bst_gate_returns",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    vehicle_entry = models.ForeignKey(
        "driver_management.VehicleEntry",
        on_delete=models.PROTECT,
        related_name="bst_gate_returns",
    )
    bst_gate_out = models.ForeignKey(
        "gate_core.BSTGateOut",
        on_delete=models.PROTECT,
        related_name="bst_gate_returns",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="bst_gate_returns",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="bst_gate_returns",
    )
    gate_in_date = models.DateField()
    in_time = models.TimeField()
    security_name = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=BSTGateReturnStatus.choices,
        default=BSTGateReturnStatus.IN_PROGRESS,
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
        prefix = f"BSTR-{today.strftime('%Y%m%d')}"
        last = (
            BSTGateReturn.objects
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
