from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.permissions import HasCompanyContext
from dispatch_plans.models import DispatchPlan, DispatchPlanStatus
from driver_management.models import Driver, VehicleEntry
from sap_client.exceptions import SAPConnectionError, SAPDataError
from vehicle_management.models import Vehicle

from gate_core.models import (
    SalesDispatchAttachment,
    SalesDispatchAttachmentType,
    SalesDispatchDocumentType,
    SalesDispatchGateOut,
    SalesDispatchGateOutItem,
    SalesDispatchGateOutStatus,
)
from gate_core.serializers_sales_dispatch import (
    SalesDispatchAttachmentSerializer,
    SalesDispatchAttachmentUploadSerializer,
    SalesDispatchDocumentSerializer,
    SalesDispatchGateOutCreateSerializer,
    SalesDispatchGateOutSerializer,
    SalesDispatchGateOutUpdateSerializer,
    SalesDispatchGatepassPrintSerializer,
    SalesDispatchReasonSerializer,
)
from gate_core.services.sales_dispatch_documents import SalesDispatchDocumentService
from gate_core.services.sales_dispatch_gatepass import (
    can_edit,
    ensure_gatepass_ready,
    get_gatepass_readiness,
)


def sales_dispatch_queryset(company):
    return (
        SalesDispatchGateOut.objects
        .filter(company=company, is_active=True)
        .select_related(
            "company",
            "vehicle_entry",
            "dispatch_plan",
            "vehicle",
            "vehicle__vehicle_type",
            "vehicle__transporter",
            "transporter",
            "driver",
        )
        .prefetch_related("items", "attachments")
    )


def get_sales_dispatch_or_404(company, entry_id):
    return get_object_or_404(sales_dispatch_queryset(company), id=entry_id)


class SalesDispatchDocumentListView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request):
        service = SalesDispatchDocumentService(request.company.company)
        try:
            documents = service.list_documents(
                request.query_params.get("document_type", "ALL"),
                {
                    "search": request.query_params.get("search", ""),
                    "from_date": request.query_params.get("from_date"),
                    "to_date": request.query_params.get("to_date"),
                    "branch": request.query_params.get("branch", ""),
                    "booking_status": request.query_params.get("booking_status", "all"),
                    "limit": request.query_params.get("limit", 100),
                },
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError:
            return Response(
                {"detail": "Failed to retrieve Docking documents from SAP."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(SalesDispatchDocumentSerializer(documents, many=True).data)


class SalesDispatchDocumentDetailView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, document_type, doc_entry):
        service = SalesDispatchDocumentService(request.company.company)
        try:
            document = service.get_document(document_type, doc_entry)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError:
            return Response(
                {"detail": "Failed to retrieve Docking document from SAP."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not document:
            raise NotFound("Docking document not found in SAP")
        return Response(SalesDispatchDocumentSerializer(document).data)


class SalesDispatchGateOutListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request):
        qs = sales_dispatch_queryset(request.company.company)
        status_filter = request.query_params.get("status")
        document_type = request.query_params.get("document_type")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        search = (request.query_params.get("search") or "").strip()

        if status_filter:
            qs = qs.filter(status=status_filter)
        if document_type:
            qs = qs.filter(document_type=document_type)
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        if search:
            qs = qs.filter(
                Q(entry_no__icontains=search)
                | Q(sap_doc_num__icontains=search)
                | Q(vehicle_no__icontains=search)
                | Q(customer_name__icontains=search)
            )

        return Response(SalesDispatchGateOutSerializer(qs.distinct(), many=True).data)

    def post(self, request):
        serializer = SalesDispatchGateOutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = SalesDispatchDocumentService(request.company.company)
        try:
            document = service.get_document(data["document_type"], data["sap_doc_entry"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError:
            return Response(
                {"detail": "Failed to retrieve selected Docking document from SAP."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not document:
            raise NotFound("Selected Docking document was not found in SAP")

        duplicate = SalesDispatchGateOut.objects.filter(
            company=request.company.company,
            document_type=document["document_type"],
            sap_doc_entry=document["doc_entry"],
            is_active=True,
            status__in=[
                SalesDispatchGateOutStatus.DOCKED,
                SalesDispatchGateOutStatus.PHOTO_ATTACHED,
                SalesDispatchGateOutStatus.READY_FOR_GATEPASS,
                SalesDispatchGateOutStatus.GATEPASS_PRINTED,
                SalesDispatchGateOutStatus.PRINT_COMMITTED,
                SalesDispatchGateOutStatus.DISPATCHED,
            ],
        ).first()
        if duplicate:
            return Response(
                {
                    "detail": f"This SAP document is already docked as {duplicate.entry_no}.",
                    "linked_sales_dispatch_id": duplicate.id,
                    "linked_entry_no": duplicate.entry_no,
                    "linked_entry_id": duplicate.vehicle_entry_id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        vehicle = get_object_or_404(Vehicle, id=data["vehicle_id"])
        driver = get_object_or_404(Driver, id=data["driver_id"])
        transporter = vehicle.transporter
        dispatch_plan = None
        if data.get("dispatch_plan_id"):
            dispatch_plan = get_object_or_404(
                DispatchPlan,
                id=data["dispatch_plan_id"],
                company=request.company.company,
                is_active=True,
            )
            if document["document_type"] == SalesDispatchDocumentType.INVOICE:
                if dispatch_plan.sap_invoice_doc_entry != document["doc_entry"]:
                    return Response(
                        {"detail": "Dispatch plan does not match selected invoice."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        with transaction.atomic():
            vehicle_entry = VehicleEntry.objects.create(
                entry_no=SalesDispatchGateOut.generate_vehicle_entry_no(),
                company=request.company.company,
                vehicle=vehicle,
                driver=driver,
                entry_type="SALES_DISPATCH",
                status="IN_PROGRESS",
                remarks=data.get("remarks", ""),
                created_by=request.user,
                updated_by=request.user,
            )
            entry = SalesDispatchGateOut.objects.create(
                company=request.company.company,
                entry_no=SalesDispatchGateOut.generate_entry_no(),
                vehicle_entry=vehicle_entry,
                dispatch_plan=dispatch_plan,
                vehicle=vehicle,
                transporter=transporter,
                driver=driver,
                **self._document_snapshot(document),
                **self._transport_snapshot(vehicle, driver, transporter),
                bilty_no=data.get("bilty_no") or document.get("bilty_no", ""),
                bilty_date=data.get("bilty_date") or document.get("bilty_date"),
                freight=data.get("freight"),
                total_freight=data.get("total_freight"),
                dock_incharge=data.get("dock_incharge", ""),
                gate_out_date=data.get("gate_out_date"),
                out_time=data.get("out_time"),
                security_name=data.get("security_name", ""),
                remarks=data.get("remarks", ""),
                created_by=request.user,
                updated_by=request.user,
            )
            self._create_items(entry, document, request.user)

        return Response(
            SalesDispatchGateOutSerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _document_snapshot(document):
        return {
            "document_type": document["document_type"],
            "sap_doc_entry": document["doc_entry"],
            "sap_doc_num": document.get("doc_num", ""),
            "sap_doc_date": document.get("doc_date"),
            "sap_doc_total": decimal_or_none(document.get("doc_total"), "0.01"),
            "sap_branch_id": document.get("branch_id"),
            "sap_branch_name": document.get("branch_name", ""),
            "sap_reference": document.get("sap_reference") or document.get("base_refs", ""),
            "sap_comments": document.get("sap_comments", ""),
            "customer_code": document.get("card_code", ""),
            "customer_name": document.get("card_name", ""),
            "ship_to_code": document.get("ship_to_code", ""),
            "ship_to_address": document.get("ship_to_address", ""),
            "place_of_supply": document.get("place_of_supply", ""),
            "bp_gstin": document.get("bp_gstin", ""),
            "eway_bill": document.get("eway_bill", ""),
            "from_warehouse": document.get("from_warehouse", ""),
            "to_warehouse": document.get("to_warehouse", ""),
            "warehouses": document.get("warehouses", ""),
            "item_summary": document.get("item_summary", ""),
            "base_refs": document.get("base_refs", ""),
            "total_quantity": decimal_or_none(document.get("total_quantity")),
            "total_litres": decimal_or_none(document.get("total_litres")),
            "total_boxes": decimal_or_none(document.get("total_boxes")),
            "total_weight": decimal_or_none(document.get("total_weight")),
        }

    @staticmethod
    def _transport_snapshot(vehicle, driver, transporter):
        return {
            "vehicle_no": vehicle.vehicle_number,
            "transporter_name": transporter.name if transporter else "",
            "transporter_gstin": transporter.gstin if transporter else "",
            "transporter_contact_person": transporter.contact_person if transporter else "",
            "transporter_mobile_no": transporter.mobile_no if transporter else "",
            "driver_name": driver.name,
            "driver_mobile_no": driver.mobile_no,
            "driver_license_no": driver.license_no,
            "driver_id_proof_type": driver.id_proof_type,
            "driver_id_proof_number": driver.id_proof_number,
        }

    @staticmethod
    def _create_items(entry, document, user):
        items = [
            SalesDispatchGateOutItem(
                sales_dispatch=entry,
                created_by=user,
                updated_by=user,
                **item,
            )
            for item in SalesDispatchDocumentService.iter_items(document)
        ]
        SalesDispatchGateOutItem.objects.bulk_create(items)


class SalesDispatchGateOutDetailView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        return Response(SalesDispatchGateOutSerializer(entry).data)

    def patch(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        if not can_edit(entry):
            return Response(
                {"detail": "This Docking entry cannot be edited in its current status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SalesDispatchGateOutUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(entry, field, value)
        entry.updated_by = request.user
        entry.save()
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchGateOutByVehicleEntryView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, vehicle_entry_id):
        entry = sales_dispatch_queryset(request.company.company).filter(
            vehicle_entry_id=vehicle_entry_id,
        ).order_by("-created_at").first()
        if not entry:
            raise NotFound("Docking entry not found for this vehicle entry.")
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchAttachmentListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        return Response(SalesDispatchAttachmentSerializer(entry.attachments.all(), many=True).data)

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        if entry.status in (
            SalesDispatchGateOutStatus.PRINT_COMMITTED,
            SalesDispatchGateOutStatus.DISPATCHED,
            SalesDispatchGateOutStatus.CANCELLED,
            SalesDispatchGateOutStatus.REJECTED,
        ):
            return Response(
                {"detail": "Attachments cannot be changed in this Docking status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SalesDispatchAttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        attachment = SalesDispatchAttachment.objects.create(
            sales_dispatch=entry,
            attachment_type=data["attachment_type"],
            file=data["file"],
            original_filename=getattr(data["file"], "name", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            notes=data.get("notes", ""),
            uploaded_by=request.user,
        )

        if data["attachment_type"] == SalesDispatchAttachmentType.TRUCK_PHOTO:
            entry.truck_photo = attachment.file
            entry.photo_latitude = data.get("latitude")
            entry.photo_longitude = data.get("longitude")
            entry.photo_uploaded_by = request.user
            entry.photo_uploaded_at = timezone.now()
            if entry.status == SalesDispatchGateOutStatus.DOCKED:
                entry.status = SalesDispatchGateOutStatus.PHOTO_ATTACHED
            entry.updated_by = request.user
            entry.save(
                update_fields=[
                    "truck_photo",
                    "photo_latitude",
                    "photo_longitude",
                    "photo_uploaded_by",
                    "photo_uploaded_at",
                    "status",
                    "updated_by",
                    "updated_at",
                ]
            )

        return Response(
            SalesDispatchAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class SalesDispatchGatepassPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        readiness = get_gatepass_readiness(entry)
        if readiness["ready"] and entry.status == SalesDispatchGateOutStatus.PHOTO_ATTACHED:
            entry.status = SalesDispatchGateOutStatus.READY_FOR_GATEPASS
            entry.updated_by = request.user
            entry.save(update_fields=["status", "updated_by", "updated_at"])
        data = SalesDispatchGateOutSerializer(entry).data
        data["gatepass_readiness"] = readiness
        return Response(data)


class SalesDispatchGatepassPrintView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        serializer = SalesDispatchGatepassPrintSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if entry.status in (
            SalesDispatchGateOutStatus.PRINT_COMMITTED,
            SalesDispatchGateOutStatus.DISPATCHED,
            SalesDispatchGateOutStatus.CANCELLED,
            SalesDispatchGateOutStatus.REJECTED,
        ):
            return Response(
                {"detail": "Gatepass cannot be printed in this Docking status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ensure_gatepass_ready(entry)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        for field, value in serializer.validated_data.items():
            if value not in (None, ""):
                setattr(entry, field, value)
        entry.updated_by = request.user
        entry.save()
        entry.assign_gatepass(request.user)
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchCommitPrintView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        if entry.status != SalesDispatchGateOutStatus.GATEPASS_PRINTED:
            return Response(
                {"detail": "Gatepass must be printed before final print commit."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entry.status = SalesDispatchGateOutStatus.PRINT_COMMITTED
        entry.print_committed_by = request.user
        entry.print_committed_at = timezone.now()
        entry.updated_by = request.user
        entry.save(
            update_fields=[
                "status",
                "print_committed_by",
                "print_committed_at",
                "updated_by",
                "updated_at",
            ]
        )
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchMarkDispatchedView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        if entry.status != SalesDispatchGateOutStatus.PRINT_COMMITTED:
            return Response(
                {"detail": "Print must be committed before marking Docking as dispatched."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            entry.status = SalesDispatchGateOutStatus.DISPATCHED
            entry.dispatched_by = request.user
            entry.dispatched_at = timezone.now()
            entry.updated_by = request.user
            entry.save(
                update_fields=[
                    "status",
                    "dispatched_by",
                    "dispatched_at",
                    "updated_by",
                    "updated_at",
                ]
            )
            entry.vehicle_entry.status = "COMPLETED"
            entry.vehicle_entry.updated_by = request.user
            entry.vehicle_entry.save(update_fields=["status", "updated_by", "updated_at"])
            if entry.dispatch_plan_id:
                entry.dispatch_plan.booking_status = DispatchPlanStatus.DISPATCHED
                entry.dispatch_plan.updated_by = request.user
                entry.dispatch_plan.save(update_fields=["booking_status", "updated_by", "updated_at"])
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchRejectView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        serializer = SalesDispatchReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if entry.status == SalesDispatchGateOutStatus.DISPATCHED:
            return Response(
                {"detail": "Dispatched Docking entries cannot be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entry.status = SalesDispatchGateOutStatus.REJECTED
        entry.reject_reason = serializer.validated_data["reason"]
        entry.rejected_by = request.user
        entry.rejected_at = timezone.now()
        entry.updated_by = request.user
        entry.save(
            update_fields=[
                "status",
                "reject_reason",
                "rejected_by",
                "rejected_at",
                "updated_by",
                "updated_at",
            ]
        )
        return Response(SalesDispatchGateOutSerializer(entry).data)


class SalesDispatchCancelView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, entry_id):
        entry = get_sales_dispatch_or_404(request.company.company, entry_id)
        serializer = SalesDispatchReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if entry.status in (
            SalesDispatchGateOutStatus.PRINT_COMMITTED,
            SalesDispatchGateOutStatus.DISPATCHED,
        ):
            return Response(
                {"detail": "Docking entries cannot be cancelled after final print commit."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entry.status = SalesDispatchGateOutStatus.CANCELLED
        entry.cancel_reason = serializer.validated_data["reason"]
        entry.cancelled_by = request.user
        entry.cancelled_at = timezone.now()
        entry.updated_by = request.user
        entry.vehicle_entry.status = "CANCELLED"
        with transaction.atomic():
            entry.save(
                update_fields=[
                    "status",
                    "cancel_reason",
                    "cancelled_by",
                    "cancelled_at",
                    "updated_by",
                    "updated_at",
                ]
            )
            entry.vehicle_entry.updated_by = request.user
            entry.vehicle_entry.save(update_fields=["status", "updated_by", "updated_at"])
        return Response(SalesDispatchGateOutSerializer(entry).data)


def decimal_or_none(value, places="0.001"):
    if value in (None, ""):
        return None
    return Decimal(str(value)).quantize(Decimal(places))
