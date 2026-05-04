from django.db import models
from django.utils import timezone

from .base import BaseModel


class EmptyVehicleGateOutStatus(models.TextChoices):
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class EmptyVehicleGateOut(BaseModel):
    """Physical gate-out record for an inward vehicle leaving empty."""

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_outs",
    )
    entry_no = models.CharField(max_length=50, unique=True)
    vehicle_entry = models.OneToOneField(
        "driver_management.VehicleEntry",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_out",
    )
    vehicle = models.ForeignKey(
        "vehicle_management.Vehicle",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_outs",
    )
    driver = models.ForeignKey(
        "driver_management.Driver",
        on_delete=models.PROTECT,
        related_name="empty_vehicle_gate_outs",
    )
    gate_out_date = models.DateField()
    out_time = models.TimeField()
    security_name = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=EmptyVehicleGateOutStatus.choices,
        default=EmptyVehicleGateOutStatus.COMPLETED,
    )

    class Meta:
        ordering = ["-gate_out_date", "-out_time", "-created_at"]
        indexes = [
            models.Index(fields=["company", "gate_out_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.entry_no

    @staticmethod
    def generate_entry_no():
        today = timezone.now()
        prefix = f"EVGO-{today.strftime('%Y%m%d')}"
        last = (
            EmptyVehicleGateOut.objects
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
