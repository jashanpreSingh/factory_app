from typing import Any, Dict, Optional

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import AuditEntryStatus, AuditInvoiceEntry


class AuditService:
    """Business logic for the invoice-tracker audit workflow."""

    @staticmethod
    @transaction.atomic
    def submit_entry(*, user, tracker_type: str, data: Dict[str, Any]) -> AuditInvoiceEntry:
        """Create a new entry, assigning the next per-type serial number."""
        last = (
            AuditInvoiceEntry.objects
            .select_for_update()
            .filter(tracker_type=tracker_type)
            .order_by("-serial_no")
            .first()
        )
        next_serial = (last.serial_no + 1) if last else 1

        return AuditInvoiceEntry.objects.create(
            tracker_type=tracker_type,
            serial_no=next_serial,
            created_by=user,
            **data,
        )

    @staticmethod
    def receive_documents(
        entry: AuditInvoiceEntry,
        user,
        remarks: Optional[str] = None,
    ) -> AuditInvoiceEntry:
        if entry.status != AuditEntryStatus.PENDING:
            raise ValidationError(
                "Documents can only be received for entries that are still pending."
            )
        entry.status = AuditEntryStatus.DOCUMENTS_RECEIVED
        entry.documents_received_at = timezone.now()
        entry.documents_received_by = user
        if remarks is not None:
            entry.auditor_remarks = remarks
        entry.save()
        return entry

    @staticmethod
    def pre_audit(
        entry: AuditInvoiceEntry,
        user,
        remarks: Optional[str] = None,
    ) -> AuditInvoiceEntry:
        if entry.status != AuditEntryStatus.DOCUMENTS_RECEIVED:
            raise ValidationError(
                "An entry must have its documents received before it can be pre-audited."
            )
        entry.status = AuditEntryStatus.PRE_AUDITED
        entry.pre_audited_at = timezone.now()
        entry.pre_audited_by = user
        if remarks is not None:
            entry.auditor_remarks = remarks
        entry.save()
        return entry

    @staticmethod
    def set_remarks(entry: AuditInvoiceEntry, remarks: str) -> AuditInvoiceEntry:
        entry.auditor_remarks = remarks
        entry.save(update_fields=["auditor_remarks", "updated_at"])
        return entry
