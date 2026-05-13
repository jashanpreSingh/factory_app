import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.permissions import HasCompanyContext
from sap_client.exceptions import SAPConnectionError, SAPDataError

from .permissions import CanEditDispatchPlans, CanViewDispatchPlans
from .serializers import (
    DispatchBillFilterSerializer,
    DispatchBillListResponseSerializer,
    DispatchPlanSerializer,
    DispatchPlanUpdateSerializer,
)
from .services import DispatchPlansService

logger = logging.getLogger(__name__)


class DispatchBillListAPI(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewDispatchPlans]

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


class DispatchPlanUpdateAPI(APIView):
    permission_classes = [
        IsAuthenticated,
        HasCompanyContext,
        CanViewDispatchPlans,
        CanEditDispatchPlans,
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
