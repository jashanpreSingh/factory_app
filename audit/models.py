from django.conf import settings
from django.db import models


class AuditTrackerType(models.TextChoices):
    FACTORY = "FACTORY", "Factory"
    MAYAPURI = "MAYAPURI", "Mayapuri"
    MART = "MART", "Mart"
    IMPORT_EXPORT = "IMPORT_EXPORT", "Import/Export"


class AuditEntryStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    DOCUMENTS_RECEIVED = "DOCUMENTS_RECEIVED", "Documents Received"
    PRE_AUDITED = "PRE_AUDITED", "Pre-Audited"


class AuditInvoiceEntry(models.Model):
    """
    A single invoice-tracker row submitted for the Delhi office audit queue.

    Submitters fill only the invoice-data fields (which differ per tracker
    type). The Delhi auditor advances the status via two sequential actions
    (Received Documents -> Pre-Audited) and may attach remarks. The
    audit/accounts columns from the legacy Excel tracker are intentionally
    not stored - the status workflow replaces them.
    """

    tracker_type = models.CharField(
        max_length=20,
        choices=AuditTrackerType.choices,
    )
    serial_no = models.PositiveIntegerField(
        help_text="Per-type running serial number (the Excel 'S. No.')."
    )

    # ----- Core invoice fields (all types) -----
    invoice_date = models.DateField()
    party_name = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    # ----- Type-specific invoice fields (nullable) -----
    grpo_no = models.CharField(max_length=120, blank=True, default="")  # Factory
    dispatch_date = models.DateField(null=True, blank=True)             # Factory, Mart
    record_date = models.DateField(null=True, blank=True)               # Mayapuri "Date"
    receiving_date = models.DateField(null=True, blank=True)            # Mart
    rec_from_imp_exp_date = models.DateField(null=True, blank=True)     # Import/Export

    # ----- Workflow -----
    status = models.CharField(
        max_length=20,
        choices=AuditEntryStatus.choices,
        default=AuditEntryStatus.PENDING,
    )
    auditor_remarks = models.TextField(blank=True, default="")

    documents_received_at = models.DateTimeField(null=True, blank=True)
    documents_received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_documents_received",
    )
    pre_audited_at = models.DateTimeField(null=True, blank=True)
    pre_audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_pre_audited",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit Invoice Entry"
        verbose_name_plural = "Audit Invoice Entries"
        unique_together = ("tracker_type", "serial_no")
        permissions = [
            ("can_audit_invoice_entries", "Can advance audit status and add remarks"),
            ("can_view_all_audit_entries", "Can view all audit entries (auditor)"),
        ]

    def __str__(self):
        return f"{self.get_tracker_type_display()} #{self.serial_no} - {self.party_name}"
