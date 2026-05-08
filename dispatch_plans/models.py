from django.db import models

from company.models import Company
from driver_management.models import Driver, VehicleEntry
from gate_core.models import BaseModel
from vehicle_management.models import Transporter, Vehicle


class DispatchPlanStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    BOOKED = "BOOKED", "Booked"
    DISPATCHED = "DISPATCHED", "Dispatched"
    CANCELLED = "CANCELLED", "Cancelled"


class DispatchPlan(BaseModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="dispatch_plans",
    )
    sap_invoice_doc_entry = models.IntegerField()
    sap_invoice_doc_num = models.CharField(max_length=30, blank=True, default="")
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_plans",
    )
    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_plans",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_plans",
    )
    linked_vehicle_entry = models.ForeignKey(
        VehicleEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatch_plans",
    )

    booking_status = models.CharField(
        max_length=20,
        choices=DispatchPlanStatus.choices,
        default=DispatchPlanStatus.PENDING,
    )
    dispatch_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=50, blank=True, default="")

    transporter_name = models.CharField(max_length=150, blank=True, default="")
    transporter_gstin = models.CharField(max_length=20, blank=True, default="")
    contact_person = models.CharField(max_length=100, blank=True, default="")
    mobile_no = models.CharField(max_length=50, blank=True, default="")
    vehicle_no = models.CharField(max_length=30, blank=True, default="")
    driver_name = models.CharField(max_length=100, blank=True, default="")
    driver_mobile_no = models.CharField(max_length=50, blank=True, default="")
    driver_license_no = models.CharField(max_length=50, blank=True, default="")
    driver_id_proof_type = models.CharField(max_length=50, blank=True, default="")
    driver_id_proof_number = models.CharField(max_length=50, blank=True, default="")

    bilty_no = models.CharField(max_length=50, blank=True, default="")
    bilty_date = models.DateField(null=True, blank=True)

    freight = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_freight = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    kanta_weight = models.DecimalField(
        max_digits=18, decimal_places=3, null=True, blank=True
    )
    remarks = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sap_invoice_doc_entry"],
                name="unique_dispatch_plan_invoice_per_company",
            )
        ]
        indexes = [
            models.Index(fields=["company", "sap_invoice_doc_entry"]),
            models.Index(fields=["company", "booking_status"]),
            models.Index(fields=["company", "dispatch_date"]),
            models.Index(fields=["company", "vehicle"]),
            models.Index(fields=["company", "driver"]),
            models.Index(fields=["company", "linked_vehicle_entry"]),
        ]
        permissions = [
            ("can_view_dispatch_plans", "Can view Dispatch Plans dashboard"),
            ("can_edit_dispatch_plans", "Can edit Dispatch Plans bookings"),
        ]

    def __str__(self):
        doc_num = self.sap_invoice_doc_num or self.sap_invoice_doc_entry
        return f"{self.company.code} invoice {doc_num}"
