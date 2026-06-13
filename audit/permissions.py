"""Permission-based access control for the audit module."""

from rest_framework.permissions import BasePermission


class CanSubmitAuditEntry(BasePermission):
    """Permission to submit (create) an invoice-tracker entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("audit.add_auditinvoiceentry")


class CanAuditEntries(BasePermission):
    """Permission to advance audit status and edit remarks (Delhi auditor)."""

    def has_permission(self, request, view):
        return request.user.has_perm("audit.can_audit_invoice_entries")


def can_view_all_audit_entries(user) -> bool:
    """True if the user may see every entry (not just their own submissions)."""
    return user.has_perm("audit.can_view_all_audit_entries") or user.has_perm(
        "audit.can_audit_invoice_entries"
    )
