import json
import logging

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.permissions import HasCompanyContext
from grpo.serializers import (
    ServiceGRPOOptionsSerializer,
    ServiceGRPOPendingEntrySerializer,
    ServiceGRPOPostRequestSerializer,
    ServiceGRPOPostResponseSerializer,
    ServiceGRPOPostingSerializer,
    ServiceGRPOPreviewSerializer,
)
from grpo.services import GRPOService
from sap_client.exceptions import SAPConnectionError, SAPDataError, SAPValidationError

from .invoice_services import DispatchInvoiceService
from .permissions import (
    CanPreviewBiltyServiceGRPO,
    CanPostBiltyServiceGRPO,
    CanPostTransporterAPInvoice,
    CanEditDispatchPlansOrLinkDispatchVehicle,
    CanLookupDispatchBill,
    CanViewOpenBiltiesOrPostTransporterAPInvoice,
    CanViewBiltyServiceGRPODetail,
    CanViewBiltyServiceGRPOHistory,
    CanViewBiltyServiceGRPOQueue,
    CanViewDispatchPlansOrLinkDispatchVehicle,
    CanViewTransporterAPInvoice,
)
from .serializers import (
    DispatchBillDetailSerializer,
    DispatchBillFilterSerializer,
    DispatchBillListResponseSerializer,
    DispatchPlanSerializer,
    DispatchPlanUpdateSerializer,
    OpenBiltySerializer,
    TransporterAPInvoicePostRequestSerializer,
    TransporterAPInvoicePostResponseSerializer,
    TransporterAPInvoicePostingSerializer,
    TransporterAPInvoicePreviewRequestSerializer,
    TransporterAPInvoicePreviewSerializer,
    TransporterAPInvoiceSAPPostRequestSerializer,
    TransporterAPInvoiceSubmitRequestSerializer,
)
from .services import DispatchPlansService

logger = logging.getLogger(__name__)


class DispatchBillListAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanViewDispatchPlansOrLinkDispatchVehicle,
    ]

    def get(self, request):
        filter_serializer = DispatchBillFilterSerializer(data=request.query_params)
        if not filter_serializer.is_valid():
            return Response(
                {
                    "detail": "Invalid query parameters.",
                    "errors": filter_serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchPlansService(company_code=request.company.company.code)

        try:
            result = service.get_bills(filter_serializer.validated_data)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(DispatchBillListResponseSerializer(result).data)


class DispatchBillByNumberAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanLookupDispatchBill]

    def get(self, request, invoice_number: str):
        invoice_number = (invoice_number or "").strip()
        if not invoice_number:
            return Response(
                {"detail": "Invoice number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchPlansService(company_code=request.company.company.code)

        try:
            bill = service.get_bill_by_number(invoice_number)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not bill:
            return Response(
                {"detail": f"SAP invoice {invoice_number} was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(DispatchBillDetailSerializer(bill).data)


class DispatchPlanUpdateAPI(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanEditDispatchPlansOrLinkDispatchVehicle,
    ]

    def patch(self, request, sap_invoice_doc_entry: int):
        serializer = DispatchPlanUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid dispatch plan details.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchPlansService(company_code=request.company.company.code)
        try:
            plan = service.update_plan(
                sap_invoice_doc_entry=sap_invoice_doc_entry,
                data=dict(serializer.validated_data),
                user=request.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(DispatchPlanSerializer(plan).data)


class DispatchPendingBiltyGRPOListAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewBiltyServiceGRPOQueue]

    def get(self, request):
        service = GRPOService(company_code=request.company.company.code)
        dispatch_plans = service.get_pending_service_grpo_entries()

        result = []
        for plan in dispatch_plans:
            vehicle_no = plan.vehicle_no or (
                plan.vehicle.vehicle_number if plan.vehicle_id else ""
            )
            bill_snapshot = service._get_dispatch_bill_snapshot(plan)
            result.append(
                {
                    "dispatch_plan_id": plan.id,
                    "sap_invoice_doc_entry": plan.sap_invoice_doc_entry,
                    "sap_invoice_doc_num": plan.sap_invoice_doc_num,
                    "booking_status": plan.booking_status,
                    "dispatch_date": plan.dispatch_date,
                    "vehicle_no": vehicle_no,
                    "driver_name": plan.driver_name,
                    "transporter_name": plan.transporter_name,
                    "transporter_gstin": plan.transporter_gstin,
                    "source_state": bill_snapshot.get("state", "") or plan.place_of_supply,
                    "bilty_no": plan.bilty_no,
                    "bilty_date": plan.bilty_date,
                    "freight": plan.freight,
                    "total_freight": plan.total_freight,
                    "created_at": plan.created_at,
                    "updated_at": plan.updated_at,
                }
            )

        serializer = ServiceGRPOPendingEntrySerializer(result, many=True)
        return Response(serializer.data)


class DispatchBiltyGRPOOptionsAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanPreviewBiltyServiceGRPO]

    def get(self, request):
        service = GRPOService(company_code=request.company.company.code)
        try:
            options = service.get_service_grpo_options()
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(ServiceGRPOOptionsSerializer(options).data)


class DispatchBiltyGRPOPreviewAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanPreviewBiltyServiceGRPO]

    def get(self, request, dispatch_plan_id):
        service = GRPOService(company_code=request.company.company.code)
        try:
            preview_data = service.get_service_grpo_preview_data(dispatch_plan_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(ServiceGRPOPreviewSerializer(preview_data).data)


class DispatchBiltyServiceGRPOPostAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanPostBiltyServiceGRPO]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        parsed_data, attachments, error_response = self._parse_payload(request)
        if error_response:
            return error_response

        serializer = ServiceGRPOPostRequestSerializer(data=parsed_data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid request data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = GRPOService(company_code=request.company.company.code)

        try:
            grpo_posting = service.post_service_grpo(
                dispatch_plan_id=serializer.validated_data["dispatch_plan_id"],
                user=request.user,
                vendor_code=serializer.validated_data["vendor_code"],
                branch_id=serializer.validated_data["branch_id"],
                service_description=serializer.validated_data["service_description"],
                amount=serializer.validated_data["amount"],
                tax_code=serializer.validated_data.get("tax_code"),
                gl_account=serializer.validated_data.get("gl_account"),
                unit_price=serializer.validated_data.get("unit_price"),
                place_of_supply=serializer.validated_data.get("place_of_supply"),
                effective_month=serializer.validated_data.get("effective_month"),
                budget_delivery_point=serializer.validated_data.get(
                    "budget_delivery_point"
                ),
                location_code=serializer.validated_data.get("location_code"),
                location_name=serializer.validated_data.get("location_name"),
                sac_entry=serializer.validated_data.get("sac_entry"),
                sac_code=serializer.validated_data.get("sac_code"),
                product_variety=serializer.validated_data.get("product_variety"),
                total_litres=serializer.validated_data.get("total_litres"),
                invoice_number=serializer.validated_data.get("invoice_number"),
                eway_bill=serializer.validated_data.get("eway_bill"),
                invoice_weight=serializer.validated_data.get("invoice_weight"),
                invoice_amount=serializer.validated_data.get("invoice_amount"),
                comments=serializer.validated_data.get("comments"),
                vendor_ref=serializer.validated_data.get("vendor_ref"),
                extra_charges=serializer.validated_data.get("extra_charges"),
                attachments=attachments,
                include_bilty_attachment=serializer.validated_data.get(
                    "include_bilty_attachment", True
                ),
                doc_date=serializer.validated_data.get("doc_date"),
                doc_due_date=serializer.validated_data.get("doc_due_date"),
                tax_date=serializer.validated_data.get("tax_date"),
                should_roundoff=serializer.validated_data.get("should_roundoff", False),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPValidationError as e:
            return Response(
                {"detail": f"SAP validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_data = {
            "success": True,
            "service_grpo_posting_id": grpo_posting.id,
            "sap_doc_entry": grpo_posting.sap_doc_entry,
            "sap_doc_num": grpo_posting.sap_doc_num,
            "sap_doc_total": grpo_posting.sap_doc_total,
            "message": (
                "Service GRPO posted successfully. "
                f"SAP Doc Num: {grpo_posting.sap_doc_num}"
            ),
            "attachments": grpo_posting.attachments.all(),
        }
        return Response(
            ServiceGRPOPostResponseSerializer(
                response_data, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _parse_payload(request):
        if request.content_type and "multipart" in request.content_type:
            try:
                raw_data = request.data.get("data", "{}")
                parsed_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            except json.JSONDecodeError:
                return (
                    None,
                    [],
                    Response(
                        {"detail": "Invalid JSON in 'data' field"},
                        status=status.HTTP_400_BAD_REQUEST,
                    ),
                )
            attachments = request.FILES.getlist("attachments")
        else:
            parsed_data = request.data
            attachments = []
        return parsed_data, attachments, None


class DispatchBiltyGRPOPostingHistoryAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewBiltyServiceGRPOHistory]

    def get(self, request):
        dispatch_plan_id = request.GET.get("dispatch_plan_id")
        service = GRPOService(company_code=request.company.company.code)
        postings = service.get_service_grpo_posting_history(
            dispatch_plan_id=int(dispatch_plan_id) if dispatch_plan_id else None
        )
        serializer = ServiceGRPOPostingSerializer(postings, many=True)
        return Response(serializer.data)


class DispatchBiltyGRPOPostingDetailAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewBiltyServiceGRPODetail]

    def get(self, request, posting_id: int):
        from grpo.models import ServiceGRPOPosting

        try:
            posting = (
                ServiceGRPOPosting.objects.select_related(
                    "dispatch_plan",
                    "dispatch_plan__company",
                    "posted_by",
                )
                .prefetch_related("lines", "attachments")
                .get(
                    id=posting_id,
                    dispatch_plan__company=request.company.company,
                )
            )
        except ServiceGRPOPosting.DoesNotExist:
            return Response(
                {"detail": "Service GRPO posting not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ServiceGRPOPostingSerializer(
            posting,
            context={"request": request},
        )
        return Response(serializer.data)


class OpenBiltyListAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanViewOpenBiltiesOrPostTransporterAPInvoice,
    ]

    def get(self, request):
        service = DispatchInvoiceService(company_code=request.company.company.code)
        try:
            open_bilties = service.get_open_bilties()
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(OpenBiltySerializer(open_bilties, many=True).data)


class TransporterAPInvoicePreviewAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanPostTransporterAPInvoice,
    ]

    def post(self, request):
        serializer = TransporterAPInvoicePreviewRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid request data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchInvoiceService(company_code=request.company.company.code)
        try:
            preview = service.preview_ap_invoice(
                service_grpo_posting_ids=serializer.validated_data[
                    "service_grpo_posting_ids"
                ],
                vendor_code=serializer.validated_data.get("vendor_code"),
                branch_id=serializer.validated_data.get("branch_id"),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(TransporterAPInvoicePreviewSerializer(preview).data)


class TransporterAPInvoicePostAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanPostTransporterAPInvoice,
    ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, posting_id: int | None = None):
        if posting_id is not None:
            serializer = TransporterAPInvoiceSAPPostRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"detail": "Invalid request data", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            service = DispatchInvoiceService(company_code=request.company.company.code)
            try:
                posting = service.post_submitted_ap_invoice(
                    posting_id=posting_id,
                    user=request.user,
                    doc_date=serializer.validated_data.get("doc_date"),
                    doc_due_date=serializer.validated_data.get("doc_due_date"),
                    tax_date=serializer.validated_data.get("tax_date"),
                    comments=serializer.validated_data.get("comments", ""),
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except SAPValidationError as e:
                return Response(
                    {"detail": f"SAP validation error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except SAPConnectionError:
                return Response(
                    {"detail": "SAP system is currently unavailable. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            except SAPDataError as e:
                return Response(
                    {"detail": f"SAP error: {str(e)}"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            posting = service.get_ap_invoice(posting.id)
            response_data = {
                "success": True,
                "transporter_ap_invoice_posting_id": posting.id,
                "sap_doc_entry": posting.sap_doc_entry,
                "sap_doc_num": posting.sap_doc_num,
                "sap_doc_total": posting.sap_doc_total,
                "message": (
                    "A/P Invoice posted successfully. "
                    f"SAP Doc Num: {posting.sap_doc_num}"
                ),
                "posting": posting,
            }
            return Response(
                TransporterAPInvoicePostResponseSerializer(
                    response_data, context={"request": request}
                ).data
            )

        parsed_data, attachments, error_response = self._parse_payload(request)
        if error_response:
            return error_response

        serializer = TransporterAPInvoicePostRequestSerializer(data=parsed_data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid request data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchInvoiceService(company_code=request.company.company.code)
        try:
            posting = service.post_ap_invoice(
                service_grpo_posting_ids=serializer.validated_data[
                    "service_grpo_posting_ids"
                ],
                user=request.user,
                invoice_number=serializer.validated_data["invoice_number"],
                invoice_amount=serializer.validated_data["invoice_amount"],
                attachments=attachments,
                invoice_date=serializer.validated_data.get("invoice_date"),
                doc_date=serializer.validated_data.get("doc_date"),
                doc_due_date=serializer.validated_data.get("doc_due_date"),
                tax_date=serializer.validated_data.get("tax_date"),
                vendor_code=serializer.validated_data.get("vendor_code"),
                branch_id=serializer.validated_data.get("branch_id"),
                comments=serializer.validated_data.get("comments", ""),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPValidationError as e:
            return Response(
                {"detail": f"SAP validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        posting = service.get_ap_invoice(posting.id)
        response_data = {
            "success": True,
            "transporter_ap_invoice_posting_id": posting.id,
            "sap_doc_entry": posting.sap_doc_entry,
            "sap_doc_num": posting.sap_doc_num,
            "sap_doc_total": posting.sap_doc_total,
            "message": (
                "Transporter A/P Invoice posted successfully. "
                f"SAP Doc Num: {posting.sap_doc_num}"
            ),
            "posting": posting,
        }
        return Response(
            TransporterAPInvoicePostResponseSerializer(
                response_data, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _parse_payload(request):
        if request.content_type and "multipart" in request.content_type:
            try:
                raw_data = request.data.get("data", "{}")
                parsed_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            except json.JSONDecodeError:
                return (
                    None,
                    [],
                    Response(
                        {"detail": "Invalid JSON in 'data' field"},
                        status=status.HTTP_400_BAD_REQUEST,
                    ),
                )
            attachments = request.FILES.getlist("attachments")
        else:
            parsed_data = request.data
            attachments = []
        return parsed_data, attachments, None


class TransporterAPInvoiceSubmitAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanPostTransporterAPInvoice,
    ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        parsed_data, attachments, error_response = TransporterAPInvoicePostAPI._parse_payload(
            request
        )
        if error_response:
            return error_response

        serializer = TransporterAPInvoiceSubmitRequestSerializer(data=parsed_data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid request data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DispatchInvoiceService(company_code=request.company.company.code)
        try:
            posting = service.submit_ap_invoice(
                service_grpo_posting_ids=serializer.validated_data[
                    "service_grpo_posting_ids"
                ],
                user=request.user,
                invoice_number=serializer.validated_data["invoice_number"],
                invoice_amount=serializer.validated_data["invoice_amount"],
                attachments=attachments,
                invoice_date=serializer.validated_data.get("invoice_date"),
                vendor_code=serializer.validated_data.get("vendor_code"),
                branch_id=serializer.validated_data.get("branch_id"),
                comments=serializer.validated_data.get("comments", ""),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except SAPDataError as e:
            return Response(
                {"detail": f"SAP data error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        posting = service.get_ap_invoice(posting.id)
        response_data = {
            "success": True,
            "transporter_ap_invoice_posting_id": posting.id,
            "sap_doc_entry": posting.sap_doc_entry,
            "sap_doc_num": posting.sap_doc_num,
            "sap_doc_total": posting.sap_doc_total,
            "message": "Transporter invoice submitted for A/P Invoice posting.",
            "posting": posting,
        }
        return Response(
            TransporterAPInvoicePostResponseSerializer(
                response_data, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )


class TransporterAPInvoiceHistoryAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanViewTransporterAPInvoice,
    ]

    def get(self, request):
        service = DispatchInvoiceService(company_code=request.company.company.code)
        postings = service.get_ap_invoice_history()
        serializer = TransporterAPInvoicePostingSerializer(
            postings,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class TransporterAPInvoiceDetailAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanViewTransporterAPInvoice,
    ]

    def get(self, request, posting_id: int):
        service = DispatchInvoiceService(company_code=request.company.company.code)
        try:
            posting = service.get_ap_invoice(posting_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransporterAPInvoicePostingSerializer(
            posting,
            context={"request": request},
        )
        return Response(serializer.data)
