from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditEntryStatus, AuditInvoiceEntry, AuditTrackerType
from .permissions import (
    CanAuditEntries,
    CanSubmitAuditEntry,
    can_view_all_audit_entries,
)
from .serializers import (
    AuditActionSerializer,
    AuditEntrySubmitSerializer,
    AuditInvoiceEntrySerializer,
    AuditRemarksSerializer,
)
from .services import AuditService


def _visible_queryset(request):
    """All entries for auditors, otherwise only the user's own submissions."""
    qs = AuditInvoiceEntry.objects.all()
    if not can_view_all_audit_entries(request.user):
        qs = qs.filter(created_by=request.user)
    return qs


class AuditEntryListCreateAPI(APIView):
    """
    GET  /api/v1/audit/entries/   List entries (own, or all for auditors).
                                  Filters: ?type=&status=&scope=mine|all
    POST /api/v1/audit/entries/   Submit a new invoice-tracker entry.
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CanSubmitAuditEntry()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = _visible_queryset(request)

        tracker_type = request.query_params.get("type")
        if tracker_type:
            qs = qs.filter(tracker_type=tracker_type)

        entry_status = request.query_params.get("status")
        if entry_status:
            qs = qs.filter(status=entry_status)

        if request.query_params.get("scope") == "mine":
            qs = qs.filter(created_by=request.user)

        serializer = AuditInvoiceEntrySerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuditEntrySubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        tracker_type = data.pop("tracker_type")

        entry = AuditService.submit_entry(
            user=request.user,
            tracker_type=tracker_type,
            data=data,
        )
        return Response(
            AuditInvoiceEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class AuditEntryDetailAPI(APIView):
    """GET /api/v1/audit/entries/<id>/"""

    permission_classes = [IsAuthenticated]

    def get(self, request, entry_id):
        entry = get_object_or_404(_visible_queryset(request), pk=entry_id)
        return Response(AuditInvoiceEntrySerializer(entry).data)


class AuditReceiveDocumentsAPI(APIView):
    """POST /api/v1/audit/entries/<id>/receive-documents/"""

    permission_classes = [IsAuthenticated, CanAuditEntries]

    def post(self, request, entry_id):
        entry = get_object_or_404(AuditInvoiceEntry, pk=entry_id)
        serializer = AuditActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        remarks = serializer.validated_data.get("remarks")
        entry = AuditService.receive_documents(entry, request.user, remarks)
        return Response(AuditInvoiceEntrySerializer(entry).data)


class AuditPreAuditAPI(APIView):
    """POST /api/v1/audit/entries/<id>/pre-audit/"""

    permission_classes = [IsAuthenticated, CanAuditEntries]

    def post(self, request, entry_id):
        entry = get_object_or_404(AuditInvoiceEntry, pk=entry_id)
        serializer = AuditActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        remarks = serializer.validated_data.get("remarks")
        entry = AuditService.pre_audit(entry, request.user, remarks)
        return Response(AuditInvoiceEntrySerializer(entry).data)


class AuditRemarksAPI(APIView):
    """PATCH /api/v1/audit/entries/<id>/remarks/"""

    permission_classes = [IsAuthenticated, CanAuditEntries]

    def patch(self, request, entry_id):
        entry = get_object_or_404(AuditInvoiceEntry, pk=entry_id)
        serializer = AuditRemarksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = AuditService.set_remarks(
            entry, serializer.validated_data.get("remarks", "")
        )
        return Response(AuditInvoiceEntrySerializer(entry).data)


class AuditSummaryAPI(APIView):
    """GET /api/v1/audit/summary/  Counts by status and by type."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _visible_queryset(request)

        by_status = {row["status"]: row["n"] for row in qs.values("status").annotate(n=Count("id"))}
        by_type = {row["tracker_type"]: row["n"] for row in qs.values("tracker_type").annotate(n=Count("id"))}

        return Response(
            {
                "total": qs.count(),
                "by_status": {
                    choice.value: by_status.get(choice.value, 0)
                    for choice in AuditEntryStatus
                },
                "by_type": {
                    choice.value: by_type.get(choice.value, 0)
                    for choice in AuditTrackerType
                },
            }
        )
