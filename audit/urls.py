from django.urls import path

from .views import (
    AuditEntryDetailAPI,
    AuditEntryListCreateAPI,
    AuditPreAuditAPI,
    AuditReceiveDocumentsAPI,
    AuditRemarksAPI,
    AuditSummaryAPI,
)

urlpatterns = [
    path("entries/", AuditEntryListCreateAPI.as_view(), name="audit-entry-list-create"),
    path("summary/", AuditSummaryAPI.as_view(), name="audit-summary"),
    path(
        "entries/<int:entry_id>/receive-documents/",
        AuditReceiveDocumentsAPI.as_view(),
        name="audit-entry-receive-documents",
    ),
    path(
        "entries/<int:entry_id>/pre-audit/",
        AuditPreAuditAPI.as_view(),
        name="audit-entry-pre-audit",
    ),
    path(
        "entries/<int:entry_id>/remarks/",
        AuditRemarksAPI.as_view(),
        name="audit-entry-remarks",
    ),
    path("entries/<int:entry_id>/", AuditEntryDetailAPI.as_view(), name="audit-entry-detail"),
]
